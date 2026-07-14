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
echo '10.42.218.230 web0x01.hbtn' >> /etc/hosts
```

### 1.3 local PC add `web0x01.hbtn` to `/etc/hosts` with localhost ip

```bash
sudo bash -c "echo '127.0.0.1 web0x01.hbtn' >> /etc/hosts"
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

We got a username and in the beginning of the exercise we got a hint to use the previous task to debug the password.

```bash
./1-xor_decoder.sh Dz58Ni4POxFrKm8YCDlyLis8aysRGBEmHg==
# Pa#iqPdN4u0GWf-qtc4tNGNyA
```

Now we know user and password.
- We navigate with Firefox to page `http://web0x01.hbtn:8080/a2/crypto_encoding_failure/`
- We press the logout button, arriving to `http://web0x01.hbtn:8080/a2/crypto_encoding_failure/login`
- entering `yosri`:`Pa#iqPdN4u0GWf-qtc4tNGNyA`
- getting flag: `4343ff5ad0978b8d4d23aec625591f15`

Alternatively we can get the flag with curl:
```bash
curl 'http://web0x01.hbtn:8080/api/a2/crypto_encoding_failure/login' \
  -X POST \
  -H 'content-type: application/json' \
  -d '{"username":"yosri","password":"Pa#iqPdN4u0GWf-qtc4tNGNyA"}'

{"message":"Crypto Cracked!\nFLAG:\n4343ff5ad0978b8d4d23aec625591f15","status":"success"}
```


- save flag:
```bash
echo 4343ff5ad0978b8d4d23aec625591f15 > 2-flag.txt

cat 2-flag.txt
```

- commit & verify



## Task 2. (A3:2021) - Injection [Stored XSS] - part 1/3

This set of tasks is designed to mimic the famous `Samy worm`, which propagated across MySpace in 2005 by exploiting Cross-Site Scripting (XSS) vulnerabilities.

### Identifying Profiles to Follow

The first task is to identify three specific profiles within our web application that you need to follow. These profiles are crucial for the next steps of this exercise.

**Instructions**:

1. Navigate and Capture Requests:
   - Begin by exploring the web application, paying close attention to the network requests and responses.
   - You can use browser developer tools (F12) to monitor these interactions.

2. Identify Profile IDs:
   - Look for requests that return user information.
   - Within these responses, identify three specific profile IDs that you are instructed to follow.

3. Follow the Profiles:
   - Once you have identified the profile IDs, navigate to each profile: http://[MACHINE-IP]/a3/xss_stored/profile/[PROFILE-ID].
   - Follow each profile by clicking on the heart icon or the designated follow button on their profile page.

4. Catch the Flag:
   - Go back to your profile to find your waiting Flag ⛳️.


<!--
### 2.1 start sandbox `cyber_websec_0x01`

- hostname: `web-0-251-155.cod-eu-west-3.hbtn.io`
- ip: `10.42.251.155`


### 2.2 Ubuntu sandbox

ssh login

```bash
ssh -p 12290 root@ssh.cod-eu-west-3.hbtn.io
# Password: bed316fafc34473c880e14822800322c
```


add `cyber_websec_0x01`'s ip to `/etc/hosts` as `web0x01.hbtn`

```bash
echo '10.42.251.155 web0x01.hbtn' >> /etc/hosts
```
verify the `/etc/hosts` on the ubuntu, delete the eventual extra lines, this should be the output:

```bash
cat /etc/hosts
127.0.0.1 localhost
10.42.251.155 web0x01.hbtn
```


### 2.3 local PC add `web0x01.hbtn` to `/etc/hosts` with localhost ip

```bash
sudo bash -c "echo '127.0.0.1 web0x01.hbtn' >> /etc/hosts"
```
We need this because the cyber websec site expects the `web0x01.hbtn` hostname.


### 2.4 local PC port 8080 ssh forwarding to ubuntu port 80

```bash
ssh -L 8080:web0x01.hbtn:80 -p 12290 root@ssh.cod-eu-west-3.hbtn.io
# Password: bed316fafc34473c880e14822800322c
```
the `-L` forwards `local_port`:`destination_host`:`destination_port`

-->

### 2.0 start sandbox `cyber_websec_0x01`

- hostname: `web-0-251-155.cod-eu-west-3.hbtn.io`
- ip: `10.42.251.155`


### 2.1 Start VPN

- visit `https://intranet-dlh.hbtn.io/user_sandboxes#`
- \ Create VPN Configuration
- \ Choose Region -> Europe
- \ Create VPN Configuration
- wait a few seconds, reload page
- \ Europe (Paris) Download configuration
- download file `attila_nemet_cyber_dlh_lu.ovpn` (in my case)
- nice observation: **it lasts for 3 months :-)**
  - Created: 2026-07-14
  - Expires: 2026-10-14
- execute:
```bash
sudo openvpn attila_nemet_cyber_dlh_lu.ovpn
```
- the prompt is not returned, that is ok


### 2.2 Set `web0x01.hbtn` to point to ip of `cyber_websec_0x01`

On local PC edit `/etc/hosts`:

```bash
sudo bash -c "echo '10.42.251.155 web0x01.hbtn' >> /etc/hosts"
```

Make sure your `hosts` file is clean and tidy, if not clean it.

```bash
cat /etc/hosts
127.0.0.1       localhost
127.0.1.1       kali
::1             localhost ip6-localhost ip6-loopback
ff02::1         ip6-allnodes
ff02::2         ip6-allrouters
10.42.251.155 web0x01.hbtn
```

### 2.3 Continue with the link from last exercise

When we visited the [http://web0x01.hbtn:8080/a2/crypto_encoding_failure/](http://web0x01.hbtn:8080/a2/crypto_encoding_failure/) link we saw the left sidebar has an item **A3 - Injection** and clicking on this we have our next candidate: [Cross Site Scripting - Stored](http://web0x01.hbtn/a3/xss_stored/profile)
- goto: [http://web0x01.hbtn/a3/xss_stored/profile](http://web0x01.hbtn/a3/xss_stored/profile)
- login `yosri`:`yosri`
- F12 (developer tools)
- soon every few seconds we're getting a 200 GET `http://web0x01.hbtn/api/a3/xss_stored/profile`
- checking the response to this request we see:
```json
{
	"status": "success",
	"user_data": {
		"FLAG_1": false,
		"FLAG_2": false,
		"followers": [],
		"following": [],
		"last_actions": [
			"John - Visited you - Tue Jul 14 11:13:01 2026 - UserID: 918203",
			"Jimmy - Visited you - Tue Jul 14 11:13:01 2026 - UserID: 32781850",
			"Dexter - Visited you - Tue Jul 14 11:13:01 2026 - UserID: 811152675"
		]
	}
}
```

- following the hints for this exercise, we're going to visit each profile:

  - http://web0x01.hbtn/a3/xss_stored/profile/918203
  - http://web0x01.hbtn/a3/xss_stored/profile/32781850
  - http://web0x01.hbtn/a3/xss_stored/profile/811152675

- clicking the heart of each user (or alternatively visiting the links below)

  - http://web0x01.hbtn/api/a3/xss_stored/like/918203
  - http://web0x01.hbtn/api/a3/xss_stored/like/32781850
  - http://web0x01.hbtn/api/a3/xss_stored/like/811152675

- ... and Yosri is happy, he's giving us the solution:
  ```
  Congratulations!
  FLAG_1/2:
  a28af3d118142ab65b02599477bd698c
  ```

### 2.4 Report the Flag

```bash
echo a28af3d118142ab65b02599477bd698c > 3-flag.txt

cat 3-flag.txt
```

- commit and run correction



## Task 3. (A3:2021) - Injection [Stored XSS] - part 2/3

### Discovering a Vulnerable Input Field

Identify which input field in the profile edit page is vulnerable to Cross-Site Scripting (XSS).

**Instructions**:

1. Explore Edit Profile Page:
   - Navigate to your profile's edit page: http://[MACHINE-IP]/a3/xss_stored/edit.
   - This page contains multiple input fields where you can enter or update your personal information.
2. Test for XSS Vulnerability:
   - Test each input field for XSS vulnerability by entering a simple script such as <script>alert('XSS')</script> into the field and saving your changes.
   - Observe which input field, when modified, triggers the JavaScript alert upon viewing your profile. This indicates an XSS vulnerability.
3. Submit the vuln case name:
   - Observe the source code behavior. `Quotes..`
   - Find out the vuln field name.

    ```bash
    $ echo "name" > 4-vuln.txt
    ```


### Solution

- visit http://web0x01.hbtn/a3/xss_stored/edit
- put `<script>alert('XSS')</script>` in First Name (in my case?), update, got
  ```
  Congratulations!
  FLAG_1/2:
  a28af3d118142ab65b02599477bd698c
  ```
- checking the html of the profile page we see a `div` tag:
  ```html
  </div><div id="main"  f_name="&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;" l_name="x" email="yosri@web0x01.hbtn" role="x" tz="1" bio="" ></div>
  ```
- now this is somewhat ugly, it is nicer if we check this `div` tag before we changed yosri's name:
  ```html
  <div id="main"  f_name="Yosri" l_name="G" email="yosri@web0x01.hbtn" role="Cyber Security Expert" tz="1" bio="Hello, Follow me through our journey towards Cyber Security Expertise." ></div>
  ```
- now if we insert our javascript alert `<script>alert('XSS')</script>` in `f_name` we're getting:
  ```html
  <div id="main" f_name="<script>alert('XSS')</script>" l_name="G" ... ></div>
  ```
- we got only flag 1/2 because we manipulated the correct field, but our script won't be executed since it is between quotation marks, so the browser it considers as text and it displays
- to trigger the execution of our script there was a suggestion: `Quotes..`
- if we're injecting
  ```html
  "><script>alert('XSS')</script>
  ```
  this will be our new html code:
  ```html
  <div id="main" f_name=""><script>alert('XSS')</script>" l_name="G" ... ></div>
  ```
- By starting with `>"`, we are explicitly closing the `f_name` attribute and the `<div id="main">` tag. After that, our `<script>` tag is "eliberated" and it will be executed!
- in my case it got frozen, but let's try anyway sending `f_name` as flag

  ```bash
  echo f_name > 4-vuln.txt
  
  cat 4-vuln.txt
  ```
- commit - run verification - didn't accept.
- it turned out that exactly this time was timing out my cyber sandbox :-(
- update `/etc/hosts` with new ip and repeating only last step
- wasn't enough
- I've clicked on previous 3 "like" links then changed `f_name`: I've got only flag 1/2
- Then I've entered the `"><script>alert('XSS')</script>` into `bio` and finally I've got and alert `XSS`
- new try with vulnerability `bio`:

  ```bash
  echo bio > 4-vuln.txt
  
  cat 4-vuln.txt

  git commit -am "4-vuln.txt - bio"
  ```
