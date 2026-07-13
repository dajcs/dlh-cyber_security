# OWASP Top 10

- 1-xor_decoder.sh
- 2_flag.txt
















## Task 1. (A2:2021) - Cryptographic Failures - Catch The Flag

- Turn back to the target machine `cyber_websec_0x01`
- Heads out to: A2 - Cryptographic Failures -> Encoding Failure.
- The goal is finding out the the login credentials in order to retreive the flag on sign in.
- Login page: `http://[MACHINE-IP]/a2/crypto_encoding_failure/`
- **Hints**:
  - Start with the profile page: `/a2/crypto_encoding_failure/profile`
  - Think about the headers of all Fetch/XHR made requests
  - Use the previous task to decrypt the password


### 1.1 start sandbox `cyber_websec_0x01`

- hostname: `web-0-218-230.cod-eu-west-3.hbtn.io`
- ip: `10.42.218.230`


### 1.2 start sandbox `ubuntu_2204`

- login with ssh:

```bash
ssh -p 13554 root@ssh.cod-eu-west-3.hbtn.io
# Password: c12d5f6296ce4d04b14be2d3798da563
```

add `cyber_websec_0x01`'s ip to `/etc/hosts` as `web0x01.hbtn`

```bash
echo 10.42.218.230 web0x01.hbtn' >> /etc/hosts
```

### 1.3 local PC add `web0x01.hbtn` to `/etc/hosts`

```bash
sudo bash -c "echo '10.42.36.192 web0x01.hbtn' >> /etc/hosts"
```
We need this because the cyber websec site expects the `web0x01.hbtn` hostname.


### 1.4 local PC port 8080 ssh forwarding to ubuntu port 80

```bash
ssh -L 8080:web0x01.hbtn:80 -p 13554 root@ssh.cod-eu-west-3.hbtn.io
# Password: c12d5f6296ce4d04b14be2d3798da563
```
the `-L` forwards `local_port`:`destination_host`:`destination_port`

This creates a local TCP tunnel with this path:

```bash
Kali browser
    |
    | connects to localhost:8080
    v
SSH client on Kali
    |
    | encrypted SSH connection
    v
Ubuntu SSH host
    |
    | connects from Ubuntu to web0x01.hbtn:80
    v
cyber web server
```


- `8080`: port opened on your Kali machine
- `web0x01.hbtn`: destination resolved and contacted by the Ubuntu SSH host
- `80`: HTTP port on that destination

> **Note**: if we know that there is no local server on our PC listening on port 80 and we have root access,
we could use the local port `80` and we could use the original links without port numbers



### 1.5 curl http://web0x01.hbtn:8080/a2/crypto_encoding_failure/


```bash
curl -v http://web0x01.hbtn:8080/a2/crypto_encoding_failure/
* Host web0x01.hbtn:8080 was resolved.
* IPv6: (none)
* IPv4: 127.0.0.1
*   Trying 127.0.0.1:8080...
* Established connection to web0x01.hbtn (127.0.0.1 port 8080) from 127.0.0.1 port 37840 
* using HTTP/1.x
> GET /a2/crypto_encoding_failure/ HTTP/1.1
> Host: web0x01.hbtn:8080
> User-Agent: curl/8.19.0
> Accept: */*
> 
* Request completely sent off
< HTTP/1.1 200 OK
< Server: nginx/1.22.1
< Date: Mon, 13 Jul 2026 22:43:44 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 2715
< Connection: keep-alive
< Vary: Cookie
< Set-Cookie: session=bEqo-Xq55R9d6zRfp5F1h0yYdK6GlYnTjp26by0md8w.jarNTeVpi1F-C6HnUoCmrx5wbrQ; HttpOnly; Path=/
< X-XSS-Protection: 0
< 
<!DOCTYPE html>
<html lang="en">

<head>
        <meta charset="utf-8" />
        <link rel="shortcut icon" type="image/x-icon" href="/static/favicon.ico" />
        <meta name="viewport" content="initial-scale=1, width=device-width" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
        <link rel="stylesheet"
                href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" />
        <title>dexterGOAT - Holberton School Edition - by Yosri.me</title>
        <style>
                html,
                body {
                        margin: 0;
                        padding: 0;
                }

                main {
                        display: flex;
                        flex-direction: row;
                        flex-wrap: nowrap;
                        margin: 0;
                        padding: 0;
                }

                #sidebar {
                        flex-grow: 0;
                }

                #main {
                        flex-grow: 1;
                }
        </style>
        <script type="module" crossorigin src="/static/sidebar.js"></script>

    <script type="module" crossorigin src="/static/tasks/a2_crypto_encoding_failure.js"></script>

</head>

<body>
        <main>
                <div id="sidebar" data-titles="[{&#34;id&#34;: &#34;a1&#34;, &#34;name&#34;: &#34;A1 - Broken Access Control&#34;, &#34;subs&#34;: [{&#34;name&#34;: &#34;Hijack a session&#34;, &#34;url&#34;: &#34;/a1/hijack_session/&#34;}]}, {&#34;id&#34;: &#34;a2&#34;, &#34;name&#34;: &#34;A2 - Cryptographic Failures&#34;, &#34;subs&#34;: [{&#34;name&#34;: &#34;Encoding Failure&#34;, &#34;url&#34;: &#34;/a2/crypto_encoding_failure/&#34;}]}, {&#34;id&#34;: &#34;a3&#34;, &#34;name&#34;: &#34;A3 - Injection&#34;, &#34;subs&#34;: [{&#34;name&#34;: &#34;Cross Site Scripting - Stored&#34;, &#34;url&#34;: &#34;/a3/xss_stored/&#34;}, {&#34;name&#34;: &#34;SQL Injection&#34;, &#34;url&#34;: &#34;/a3/sql_injection/&#34;}, {&#34;name&#34;: &#34;noSQL Injection&#34;, &#34;url&#34;: &#34;/a3/nosql_injection/&#34;}]}, {&#34;id&#34;: &#34;a4&#34;, &#34;name&#34;: &#34;A4 - Insecure Design&#34;, &#34;subs&#34;: []}, {&#34;id&#34;: &#34;a5&#34;, &#34;name&#34;: &#34;A5 - Security Misconfiguration&#34;, &#34;subs&#34;: []}, {&#34;id&#34;: &#34;a6&#34;, &#34;name&#34;: &#34;A6 - Vuln &amp; Outdated Components&#34;, &#34;subs&#34;: []}, {&#34;id&#34;: &#34;a7&#34;, &#34;name&#34;: &#34;A7 - Identity &amp; Auth Failure&#34;, &#34;subs&#34;: []}, {&#34;id&#34;: &#34;a8&#34;, &#34;name&#34;: &#34;A8 - Software &amp; Data Integrity&#34;, &#34;subs&#34;: []}, {&#34;id&#34;: &#34;a9&#34;, &#34;name&#34;: &#34;A9 - Security Logging Failures&#34;, &#34;subs&#34;: []}, {&#34;id&#34;: &#34;a10&#34;, &#34;name&#34;: &#34;A10 - Server-Side Request Forgery&#34;, &#34;subs&#34;: []}]"></div><div id="main" csrf-token="eyd1c2VybmFtZSc6ICd5b3NyaScsICdwYXNzd29yZF9oYXNoJzogJ0R6NThOaTRQT3hGckttOFlDRGx5TGlzOGF5c1JHQkVtSGc9PSd9" ></div>
        </main>
</body>

* Connection #0 to host web0x01.hbtn:8080 left intact
</html>
```

Here the `csrf-token` is the most interesting. Let's try a base64 decode of its value:

```bash
echo -n eyd1c2VybmFtZSc6ICd5b3NyaScsICdwYXNzd29yZF9oYXNoJzogJ0R6NThOaTRQT3hGckttOFlDRGx5TGlzOGF5c1JHQkVtSGc9PSd9 | base64 -d

# {'username': 'yosri', 'password_hash': 'Dz58Ni4POxFrKm8YCDlyLis8aysRGBEmHg=='} 
```

We got a username and in the beginning we got a hint to use the previous task to debug the password.

```bash
./1-xor_decoder.sh Dz58Ni4POxFrKm8YCDlyLis8aysRGBEmHg==
# Pa#iqPdN4u0GWf-qtc4tNGNyA
```

Now we know user and password.
- We navigate with Firefox to page `http://web0x01.hbtn:8080/a2/crypto_encoding_failure/`
- We press the logout button, arriving to `http://web0x01.hbtn:8080/a2/crypto_encoding_failure/login`
- entering `yosri`:`Pa#iqPdN4u0GWf-qtc4tNGNyA`
- getting flag: `4343ff5ad0978b8d4d23aec625591f15`
- save flage:
```bash
echo 4343ff5ad0978b8d4d23aec625591f15 > 2-flag.txt

cat 2-flag.txt
```

- commit & verify