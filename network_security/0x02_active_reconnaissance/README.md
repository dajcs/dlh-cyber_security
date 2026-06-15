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