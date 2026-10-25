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


## Task 1 - Bypassing Blacklist Restrictions to Read a File

Write a script to retrieve the content of the file located at `/home/user/flag`, but with a challenge—certain commands and common approaches are blacklisted.

You need to find a creative way to read the flag using alternative methods to bypass the blacklist.

Restricted Commands
- The following commands and patterns are blacklisted:
`bash, sh, zsh, SHELL, grep, vi, vim, scp, ssh, awk, tar, nano, pico, ed, ex, gedit, emacs, kate, lime, jed, find`
- Special characters like `|, -, +, *, ?`
- Control structures like `echo, for, while, do, done, if, and others`
- The space character `(' ')`is also blacklisted

Attempts to use any blacklisted command will result in an error.

Target machine for this task:
`cyber shell 0x01 task3`

to connect use :

```bash
ssh user@ YOUR _ CONTAINER _ IP
password : user
```

Repo:

GitHub repository: `dlh-cyber_security`
Directory: `privilege_escalation_security_shells/0x00_what_the_shell`
File: `2-flag.txt`

### Solution

- start sandbox `cyber_shell_0x01_what_is_shell_task3`
- start openvpn

```bash
neat@dellw:/mnt/c/Users/dajcs/code/dlh-cyber_security/privilege_escalation_security_shells/0x00_what_the_shell
$ ping 10.42.61.178
PING 10.42.61.178 (10.42.61.178) 56(84) bytes of data.
64 bytes from 10.42.61.178: icmp_seq=1 ttl=126 time=21.3 ms
64 bytes from 10.42.61.178: icmp_seq=2 ttl=126 time=20.4 ms
64 bytes from 10.42.61.178: icmp_seq=3 ttl=126 time=21.6 ms
^C
--- 10.42.61.178 ping statistics ---
3 packets transmitted, 3 received, 0% packet loss, time 1999ms
rtt min/avg/max/mdev = 20.360/21.099/21.631/0.539 ms
neat@dellw:/mnt/c/Users/dajcs/code/dlh-cyber_security/privilege_escalation_security_shells/0x00_what_the_shell
$ ssh user@10.42.61.178
The authenticity of host '10.42.61.178 (10.42.61.178)' can't be established.
ED25519 key fingerprint is SHA256:ePalN2vmJ9sA/h+ef8A1XpWjvDIP6nxOIWpXEDYk9vk.
This host key is known by the following other names/addresses:
    ~/.ssh/known_hosts:27: [hashed name]
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '10.42.61.178' (ED25519) to the list of known hosts.
user@10.42.61.178's password:
Your Goal is to read '/home/user/flag' content
Have fun


cat</home/user/flag
CTF{who_needs_espace_when_u_have_bash_HASH : 00fa93e7548c60d5ec8c7079f4ca9456}
```

Ctrl-C to exit the session.

```bash
echo 00fa93e7548c60d5ec8c7079f4ca9456 >2-flag.txt
```

