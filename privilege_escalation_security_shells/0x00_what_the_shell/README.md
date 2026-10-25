## Tasks 0 - Escape the Blacklist and Read the Flag

Your goal is to read the content of the file located at `/home/user/flag`, but with a twist—certain commands and approaches are blacklisted.

You need to find a creative way to read the flag using alternative methods to bypass the blacklist.

### Restricted Commands

The following commands and patterns are blacklisted: `bash`, `sh`, `zsh`, `SHELL`, `grep`, `vi`, `vim`, `scp`, `ssh`, `awk`, `tar`, `nano`, `pico`, `ed`, `ex`, `gedit`, `emacs`, `kate`, `lime`, `jed`, `find`, `cat`, `less`, `more`, `tail`, `head`, `wc`, `ls`, `pwd`, `cd`, `ls`, `echo`, `printf`, `read`, `set`, `unset`, `export`, `alias`, `unalias`, `history`, `jobs`, `bg`, `fg`, `kill`, `ps`, `top`, `htop`, `df`, `du`, `free`, `vmstat`, `iostat`, `netstat`, `ss`, `ifconfig`, `ping`, `traceroute`, `nslookup`, `dig`, `host`, `resolveip` |, `-`, `echo`, `for`, `while`, `do`, `done`, `if`, `{}`, and others.

Attempts to use any blacklisted command will result in an error.

### Your goal

Find a way to read the contents of `/home/user/flag`.

You cannot directly reference the file's name as it appears.

### Target machine for this task:
- `cyber shell 0x01 task2`

to connect use:

```bash
ssh user@ YOUR _ CONTAINER _ IP
password : user
```

Repo:


- GitHub repository: `dlh-cyber_security`
- Directory: `privilege_escalation_security_shells/0x00_what_the_shell`
- File: `1-flag.txt`


### Solution

- start sandbox `cyber_shell_0x01_what_is_shell_task2`
- start openvpn

```bash
$ ssh user@10.42.219.24
The authenticity of host '10.42.219.24 (10.42.219.24)' can't be established.
ED25519 key fingerprint is SHA256:ePalN2vmJ9sA/h+ef8A1XpWjvDIP6nxOIWpXEDYk9vk.
This key is not known by any other names
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.42.219.24' (ED25519) to the list of known hosts.
user@10.42.219.24's password:
Your Goal is to read '/home/user/flag' content.
Have fun.
$ head /home/user/fla?
CTF{who_needs_espace_when_u_have_bash_HASH : 0822405a8bf7f75fc4003d2adb761225}
$
```

- local machine:

```bash
echo 0822405a8bf7f75fc4003d2adb761225 >1-flag.txt
```

