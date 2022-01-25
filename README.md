# Random and somewhat useful tools

Requires:
* Python 3.9+
* bash

Install in `$HOME/.local/hedgehog`:
```console
curl -sSL https://raw.githubusercontent.com/sjoegren/hedgehog/main/install-hedgehog.bash | bash
```

## Tools
<!-- following is automatically generated -->
### dirstack
```
usage: dirstack [-h] [-V] [--color | --no-color] [-v] [--debug] [--add DIR]
                [--delete] [--list]

dirstack - keep a list of recently visited directories to choose from, invoke
with `ds` shell function.

options:
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
### fzfdirs
```
usage: fzfdirs [-h] [-V] [--color | --no-color] [-v] [--debug] [--file FILE]
               [-e] [--add-recent PATH] [--bookmark DIR]

fzfdirs - print bookmarked directories to feed to fzf.

Shell function `cdg` opens fzf with the list of bookmarks and cd to the selected path.
`cdg -e` to open bookmarks file in $EDITOR.

options:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  --color, --no-color
  -v, --verbose        Increase verbosity level.
  --debug              Extra debug output.
  --file FILE          Bookmarks file (default:
                       /home/aksel/.config/hedgehog/bookmarks.yaml)
  -e, --edit           Edit bookmarks file
  --add-recent PATH    Add PATH to recently used file
  --bookmark DIR       Add bookmark

```
### git-cob
```
usage: git-cob [-h] [-V] [--color | --no-color] [-v] [--debug] [-a] [-P]

git cob - display a menu with branches to choose from to checkout.

options:
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

Display a menu with commits to choose from to create a fixup commit.

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --color, --no-color
  -v, --verbose         Increase verbosity level.
  --debug               Extra debug output.
  -n MAX_COUNT, --max-count MAX_COUNT
                        Number of commits to show in menu, default: 10.
  -s, --squash          git commit --squash instead of --fixup

```
### git-getbranch
```
usage: git-getbranch [-h] [-V] [--color | --no-color] [-v] [--debug] [-a] [-P]

git getbranch - select a branch from a menu and print it.

options:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  --color, --no-color
  -v, --verbose        Increase verbosity level.
  --debug              Extra debug output.
  -a, --all            Show branches from remotes too.
  -P, --no-preview     Don't show preview window in menu with latest commits.

```
### git-lstree
```
usage: git-lstree [-h] [-V] [--color | --no-color] [-v] [--debug]

git lstree - Print a tree of files from ls-files

options:
  -h, --help           show this help message and exit
  -V, --version        show program's version number and exit
  --color, --no-color
  -v, --verbose        Increase verbosity level.
  --debug              Extra debug output.

```
### git-pv
```
usage: git-pv [opts] [<revision range>] [[--] <path>...]

Preview commits and show or print selected commit.

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --color, --no-color
  -v, --verbose         Increase verbosity level.
  --debug               Extra debug output.
  -n MAX_COUNT, --max-count MAX_COUNT
                        Number of commits to show in menu, default: 20.
  -l, --log-preview     Show preview of git log instead of patches.
  -p, --print           Print selected commit id instead of showing the patch.

```
### git-rmb
```
usage: git-rmb [-h] [-V] [--color | --no-color] [-v] [--debug]

git rmb - select a branch to remove remote and locally.

options:
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

options:
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
                  [--config CONFIG] [--scp [hostname]] [-c FILE] [--copy-id]
                  [-l] [-L] [-i INVENTORY] [--no-local-inventory]
                  [--ssh-config] [--hosts-file]
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

options:
  -h, --help            show this help message and exit
  -V, --version         show program's version number and exit
  --color, --no-color
  -v, --verbose         Increase verbosity level.
  --debug               Extra debug output.
  --config CONFIG       Config file (default:
                        /home/aksel/.config/hedgehog/ssh.yaml)
  --scp [hostname]      Run scp instead of ssh, if used together with -l no
                        hostname is required, leave host empty is target spec.
  -c FILE, --remote-cmd FILE
                        Execute remote command read from FILE (- to read from
                        stdin), on target host
  --copy-id             Run ssh-copy-id instead of ssh
  -l, --last            ssh to last target used
  -L, --list            List hosts in inventory
  -i INVENTORY, --inventory INVENTORY
                        Ansible inventory file (yaml or ini). When not
                        specified, use environment variable ANSIBLE_INVENTORY
                        if set, else look for yaml inventory in CWD.
  --no-local-inventory
  --ssh-config          Re-write host aliases to ssh_config from ansible
                        inventory. Normally this is done automatically on each
                        invocation.
  --hosts-file          Write ansible hosts to /etc/hosts

```
