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

## Task 2 - inspect website

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