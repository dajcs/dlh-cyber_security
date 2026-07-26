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

We were checking whether the main domain exposes any **real paths** — an upload endpoint, a `robots.txt`, a sitemap, static assets, or an index that names other subdomains. Any of these could hand us the real subdomain directly instead of guessing -- but nope, no clues here either :-(



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
git commit -m "0-target.txt with domain"
git push
```