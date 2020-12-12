# Random and somewhat useful tools

Requires:
* Python 3.9+
* bash

Install in `$HOME/.local/hedgehog`:
```console
curl -sSL https://raw.githubusercontent.com/akselsjogren/hedgehog/main/install-hedgehog.bash | bash
```

## Tools
<!-- following is automatically generated -->
### dirstack
```
usage: dirstack [-h] [-V] [--color | --no-color] [-v] [--debug] [--add DIR]
                [--delete] [--list]

dirstack - keep a list of recently visited directories to choose from, invoke
with `ds` shell function.

optional arguments:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  --color, --no-color
  -v, --verbose        Increase verbosity level.
  --debug              Extra debug output.
  --add DIR            Add path to dirstack
  --delete             Delete the dirstack file.
  --list               List current dirstack entries sorted on access time on
                       stdout.

```
### git-cob
```
usage: git-cob [-h] [-V] [--color | --no-color] [-v] [--debug] [-a] [-P]

git cob - display a menu with branches to choose from to checkout.

optional arguments:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  --color, --no-color
  -v, --verbose        Increase verbosity level.
  --debug              Extra debug output.
  -a, --all            Show branches from remotes too.
  -P, --no-preview     Don't show preview window in menu with latest commits.

```
### git-fixup
```
usage: git-fixup [opts] [git-commit args]

git fixup - display a menu with commits to choose from to create a fixup commit.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --color, --no-color
  -v, --verbose         Increase verbosity level.
  --debug               Extra debug output.
  -n MAX_COUNT, --max-count MAX_COUNT
                        Number of commits to show in menu, default: 10.

```
### git-getbranch
```
usage: git-getbranch [-h] [-V] [--color | --no-color] [-v] [--debug] [-a] [-P]

git getbranch - select a branch from a menu and print it.

optional arguments:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  --color, --no-color
  -v, --verbose        Increase verbosity level.
  --debug              Extra debug output.
  -a, --all            Show branches from remotes too.
  -P, --no-preview     Don't show preview window in menu with latest commits.

```
### git-rmb
```
usage: git-rmb [-h] [-V] [--color | --no-color] [-v] [--debug]

git rmb - select a branch to remove remote and locally.

optional arguments:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  --color, --no-color
  -v, --verbose        Increase verbosity level.
  --debug              Extra debug output.

```
### hhdiff
```
usage: hhdiff [-h] [-V] [--color | --no-color] [-c] [-u] [-m] [-n] [-l LINES]
              fromfile tofile

Multiple diff formats - colorize intraline diffs.

* ndiff:    lists every line and highlights interline changes.
* context:  highlights clusters of changes in a before/after format.
* unified:  highlights clusters of changes in an inline format.
* html:     generates side by side comparison with change highlights.

positional arguments:
  fromfile
  tofile

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --color, --no-color
  -c, --context         Produce a context format diff (default)
  -u, --unified         Produce a unified format diff
  -m, --html            Produce HTML side by side diff (can use -c and -l in
                        conjunction)
  -n, --ndiff           Produce a ndiff format diff
  -l LINES, --lines LINES
                        Set number of context lines (default 3)

```
### sshansible
```
usage: sshansible [-h] [-V] [--color | --no-color] [-v] [--debug]
                  [--scp [hostname]] [-c FILE] [--copy-id] [-l] [-L]
                  [--ssh-config]
                  [arg ...]

SSH to hostnames in an ansible-inventory using "ansible_host" address instead
of name resolution.

Given an inventory file like this:

    [buildslaves]
    foo     ansible_host=192.0.2.1

Running 'sshansible.py -- -v foo', will exec the command:
  ssh -o Hostname=192.0.2.1 -v foo

That way any config in 'ssh_config' for host 'foo' will still be honored.

scp:
    sshansible.py --scp bar -- /etc/foo.conf bar:/tmp

positional arguments:
  arg                   ssh arguments, like host from ansible inventory to
                        connect to

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --color, --no-color
  -v, --verbose         Increase verbosity level.
  --debug               Extra debug output.
  --scp [hostname]      Run scp instead of ssh, if used together with -l no
                        hostname is required, leave host empty is target spec.
  -c FILE, --remote-cmd FILE
                        Execute remote command read from FILE (- to read from
                        stdin), on target host
  --copy-id             Run ssh-copy-id instead of ssh
  -l, --last            ssh to last target used
  -L, --list            List hosts in inventory
  --ssh-config          Re-write host aliases to ssh_config from ansible
                        inventory. Normally this is done automatically on each
                        invocation.

```
