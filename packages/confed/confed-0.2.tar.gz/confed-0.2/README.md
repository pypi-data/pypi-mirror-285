# confed

A command line tool for programmatically modifying text-based configuration files.

Did you ever need to script a server configuration or migration or such a need to update the configuration of a service from your script? The command line for many a server admin and the go to scripting language of course is [bash](https://www.gnu.org/software/bash/manual/bash.html) today on some [*nix](https://en.wikipedia.org/wiki/Unix-like) flavour (commiserations if you're using [powershell](https://learn.microsoft.com/en-us/powershell/)) on a [Windows server](https://en.wikipedia.org/wiki/Windows_Server).

Typically we'd use standard tools like [sed](https://manpages.org/sed), [awk](https://manpages.org/awk) or [perl](https://manpages.org/perl), and invariable end up wrangling with [regular expressions](https://regex101.com/) and all the idiosyncrasies of each tool's slightly different implementation of them the minute you want to capture groups and make changes or never mind trying to match flexibly:

- value
- 'value'
- "value"

Well, say goodbye to all that, and avoid regular expressions for the best part and indulge in the [Python flavor](https://docs.python.org/3/howto/regex.html) if you must, using `confed` instead.

`confed` is a command line tool written in Python (and so can offer Pythonic regular expressions) that means to make it much easier. The very use case that justified writing it one afternoon was changing the [postgresql](https://www.postgresql.org/) data-directory:

```
confed -I /etc/postgresql/14/main/postgresql.conf data_directory /data/postgresql/14/main
```

and it's done. 

`confed` will scan the input file (`/etc/postgresql/14/main/postgresql.conf` in this example), find all lines that appear to defined the specified setting (`data_directory` in this example) and add a definition that sets it to the specified value (`/data/postgresql/14/main` in  this example) just after any existing lines it found setting the value, comment out the existing definition and  respect the quoting convention it found when adding the new. 

## Installing confed

Simply:

```
sudo pip install confed
```

if for any odd reason you lack pip, install that: https://pip.pypa.io/en/stable/installation/

And if you lack Python, you're probably not configuring any popular distro of *nix, but it's easy to get: https://www.python.org/downloads/

**Note:** That is a system wide installation and not actually highly recommended on any system in which python and python packages are relevant system tools, which increasingly is many a distro with a desktop environment. Servers are generally safer, but either way you may prefer some safer options so...

### Safer options

Yes, `sudo pip install` is not always the safest options, so it pays to be careful. The reason is that increasingly there are system tools (especially in desktop environments), that are written in Python. It is after all [the most popular of languages](https://www.hackerrank.com/blog/most-popular-languages-2024/). And Python brings with it package dependencies, `confed` for example depends upon the package `pyparsing` and a particular version of Python too ...and you system may have an older version of Python or an older version of `pyparsing`  installed and they are not always backward compatible ... 

For that reason Python supports and is it is ubiquitously recommended to use, virtual environments ([venvs](https://docs.python.org/3/library/venv.html)). The only problem is they are a modest hassle to implement, not huge but modest, and so there are a few possible approaches to isolating a given pip install from the system Python environment:

#### Make a venv and deploy in it

Bit of a hassle, not least as you need to make a decision on where to house the venv. Let's assume you're using `/opt/venvs` to house system level (not user level) venvs (as good a place as any) then:

```
python -m venv /opt/venvs/confed  			# create the venv
source /opt/venvs/confed/bin/activate		# activate it
sudo -E pip install confed					# pip will now install into that venv
```

should do the job, but aside from being cumbersome it's bothersome, we' can expect confed to be installed in the venv too at `/opt/venvs/confed/bin/confed` and so you'd need `/opt/venvs/confed/bin` in you [PATH](https://en.wikipedia.org/wiki/PATH_(variable)) to run it.

Conclusion, lot of hassle and kludgy.

### Isolate it in user space

Much simpler is just:

```
python install --user confed
```

and this will install it in user space, and it will (probably) be in your path and can run it with `condfed`. The only drawback is, that's only available to the user logged in who installed it (in `~/.local/bin` typically). That is usually fine though and if it is, this is simple and the clean and the easiest solution. 

Conclusion: Easy, safe and convenient. But tool is not available globally at system level

### use pipx

[pipx](https://github.com/pypa/pipx) is a great tool for installing scripts at system level in isolated environments! It's designed or just this. And in theory once it's installed it's as simple as:

```
pipx install --global confed
```

Well, that's pipx's goal anyhow. The problem is it's still in heavy development and evolving so, for example the latest version is 1.6.0 at time of writing which supports install `--global` but the Ubuntu distribution (`sudo apt install pipx`) is 1.0 which doesn't support the `--global` option yet. So first you have to work out how to install 1.6 and that's a hassle right there. You see pix is a python tool itself so the question of installing it in an isolated environment with pip emerges see [Installing confed](#Installing_confed) above (and we have a recursive issue). 

Conclusion: Could be great but getting the right version is as complicated as the problem we're trying to solve and so not simple approach.

## Using confed

The best help is provided by `confed` itself:

```
confed --help
```

or [RTFM](https://en.wiktionary.org/wiki/RTFM):

```
man confed
```

The basics to note are:

`confed` supports single line settings only. More complex grammars with multiple lines used to define a configuration setting are not (yet) supported.

The four most important concepts are:

- **setting** - the name of a configuration setting.
- **value** - the value you'd like to set it to.
- **INPUT** - the configuration it reads. If not specified will read [stdin](https://en.wikipedia.org/wiki/Standard_streams). With `-i/--input` will read a nominated file and with `-I/--Inplace` will read a dominated file and write back to it! (It keeps no backup, so test well before doing that and consider in your script or generally, keeping backups).
- **OUTPUT** -  If not specified will write to [stdout](https://en.wikipedia.org/wiki/Standard_streams) otherwise with -`o/--output` will write to a nominated file. If the same file as INPUT is nominated is the same as  `-I/--Inplace` (which is shorthand for that) . It makes no sense to specify both -`o/--output`  and  `-I/--Inplace`.

Other important concepts:

- The **COMMENTCHARACTER** defaults to '#' and is understood to introduce comments, both whole of line comments and end of line comments). Any character can be specified with `-C/--CommentCharacter`. Only single character definitions are tested and supported (at present) but you can always experiment with strings.
- The **ASSIGNMENTCHARACTER** defaults to '=' and is what separates the **setting** from the **value**. If empty then white space separates them (one or more space or tab characters). Any character can be specified with `-A/--AssignmentCharacter`. Only single character definitions are tested and supported (at present) but you can always experiment with strings.
- **NAMECHARACTERS** is a is list of legal characters in setting names and can be specified with `-N/--NameCharacters`. Sensible defaults are in place. 
- **VALUECHARACTERS** is a is list of legal characters in setting values and can be specified with `-V/--ValueCharacters`. Sensible defaults are in place.
- `-m/--multiple` is an important argument that lets `confed` know that the nominated setting can validly be set multiple time in the one configuration file. If that's not specified `confed` will only leave one definition of that setting uncommented in the output. If it is specified then `'-d/--delete` is available to delete a specific setting/value pair from such a multiple set, and `-r/--regex` to help specifiy values and settings a little more flexibly (than literally).
- Configuration defaults are pre-implemented for some common configuration file formats:
  - `--postgres` for [PostgreSQL](https://www.postgresql.org/) configuration file defaults
  - `--ssh` for [ssh and sshdaemon](https://linuxhandbook.com/enable-ssh-ubuntu/) style configuration file defaults.
  - `--sudo` for [`\etc\sudoers`](https://help.ubuntu.com/community/Sudoers) style configuration defaults.
  - `--php` for [PHP](https://www.php.net/) configuration defaults.
  - `--uwsgi` for [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/) configuration file defaults.
- Testing - always test you proposed changes using the `-t/--test` option. That will make no changes (leave everything inctact) but display a [diff](https://manpages.org/diff) of the changes it *would* apply, so you can feel sure you have the name and value right and `confed` is doing what you need. 

## Examples

The test script tries to cover all the supported use cases  and variants (clearly, to keen an eye on stability and that everything still works when tweaking the script). Here's a (not exhaustive) list of them:

- `confed setting_name setting_value < old.conf >  new.conf`

  Reads `old.conf`, cleanly adds a line that sets s*etting_name* to *setting_value* and writes it to `new.conf` being as clean and clever about it as it can be.

- `confed setting_name setting_value -i old.conf -o new.conf`

  Same thing using command line options rather than standard io streams.

- `confed setting_name setting_value -I test.conf`

  Reads  `test.conf` and writes back to it the modified version. An in place edit.

- `confed setting_name setting_value -tI test.conf`

  Same thing except it's a non destructive test that prints to stdout the diff between the original and what it would have written. Important for testing any modification not least an in-place modification to see it's doing what you want!

- `confed -i test.conf setting_name setting_value -c "An end of line comment"`

  Reads `test.conf` adding a line to that sets *setting_name* to *setting_value* and adds an end of line comment of "An end of line comment" to that line (so so you can leave a record whys and wherefores)

- `confed --ssh -I /etc/ssh/sshd_config ListenAddress "127.0.0.1" -c "**add local loopback" -m`

  Using ssh configuration syntax and knowing that *ListenAddress* can appear multiple times (`-m`) adds a definition  setting one at *127.0.0.1* in the ssh daemon configuration file.

  The `-m`is crucial here or `confed` would comment out all other lines that seem to set *ListenAddress* at the same time!

  `confed` performs an in place edit here and keeps no backup so that you're responsible for that, and using the `-t` option prudently to test non-destructively first.

- `confed --ssh -I /etc/ssh/sshd_config -d ListenAddress "::" -m`

  Similar to previous example but deletes (`-d`) any line that sets *ListenAddress* to "::".

- `confed --ssh -I /etc/ssh/sshd_config -mdk ListenAddress "::"`

  Same again only keeps (`-k`) the line commenting it out instead of deleting it!

- `confed --ssh -I /etc/ssh/sshd_config -mdkr ListenAddress "198\..*"`

  Same again but deletes any lines (comments them out) that which match the regular expression "ListenAddress\s+198\..*"

  The name (ListenAddress) is also interpreted as a regular expression so for safety you might consider using "^ListenAddress$". While completely hypothetical ListenAddress may match MyListenAddress and ListenAddressTheSecond or OnTheLeftListenAddressOnTheRight etc. IN fact n guarantees here, use `-t`! If you ever apply regular expressions anywhere without testing you probably drive without a seat belt on and cross roads without looking, good luck!

## Alternatives and similar projects

One of the main advantages of publishing a system tool on [PyPI](https://pypi.org/) is that it can me installed with pip on almost nay distro and OS without trouble. One of drawbacks of publishing a command line tool on PyPI is that anyone can and so it's a free for all on names.  

In writing this I'd called it reconf.  But lo and behold:

https://pypi.org/project/reconf/

A 2015 project a light extension of [ConfigParser](https://docs.python.org/3/library/configparser.html) in Python 2.7 last touched in 2015!

And all these names were taken:

- [configure](https://pypi.org/project/configure/) - a YAML configuration library last tocuhed in 2012
- [reconfigure](https://pypi.org/project/reconfigure/) - an undocument package uploaded in 202 with no clue what it's about.
- [confit](https://pypi.org/project/confit/) - a (supposedly) complete and easy-to-use configuration framework with a fair stab at [comparisons with alternatives](https://aphp.github.io/confit/latest/alternatives/) and still ind evelopment but not a command line tool pitching at this need.
- [confiture](https://pypi.org/project/confiture/) - an (allegedly) advanced configuration parser , not touched since 2016 listed with a dead [homepage](https://idevelop.org/p/confiture/) but clearly migrated to github: https://github.com/NaPs/Confiture (without updating the PyPI listing)
- [ced](https://pypi.org/project/ced/) - a nice variant on sed, namewise, but taken bya very lightweight stab at something similar in fact. Poorly documented alas and not touched since 2017. It is indeed very lightweight and a simple wrapper around [string.Template](https://docs.python.org/3/library/string.html#template-strings).
- [confedit](https://pypi.org/project/confedit/) - completely undocumented, anybody's guess what this is and does, and not touched since 2018. Being Python we could just install it and read the code but hey ... pass.
- [confetti](https://pypi.org/project/confetti/) - Described only as "Generic configuration mechanism" this is being actively developed it seems and handles *hierarchical configuration data*. To wit, this could well form a better basis than [pyparsing](https://github.com/pyparsing/pyparsing) should `confed` want to handly hierarchical configurations and multi-line definitions some time. For now `confed` is a line based app (like sed) and is based on on pyparsing to analyse the lines one by one.

And that is just a sampling of the PyPI landscape touched on in trying to find an available name there. There is a plethora a more targeted and diverse configuration file editing tools out in the wild, but I couldn't find one that was just that small step up from sed, which would make it easy peasy to alter configuration files from scripts I use to manage servers.

## Contributing

Code contributions are always welcome. If you need more features, like more complex settings or different flavours of default

Simply submit a [pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests) and consider following [best practices](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/getting-started/best-practices-for-pull-requests).

Above all, make sure your modified script passes all the tests and add tests for any new use cases you've added support for! The test scrip is simple bash and all it does is run `confed` on a test file, and compare the result against a recorded expectation reporting PASS or FAIL. It's not rocket science, and a testing framework as simple as this one file script is. Not many bells and whistles. 
