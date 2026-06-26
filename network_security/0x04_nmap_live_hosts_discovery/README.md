# Nmap Live Host Discovery

- 0-arp_scan.sh
- 1-icmp_echo_scan.sh
- 2-icmp_timestamp_scan.sh
- 3-icmp_address_mask_scan.sh
- 4-tcp_syn_ping.sh
- 5-tcp_ack_ping.sh
- 6-udp_ping_scan.sh
- 100-flag.txt

## Getting the 100-flag.txt

### Get a cyber_netsec_0x04 Sandbox

1.    \>_ Get a sandbox
2.    \ Europe (Paris)
3.    \ cyber_netsec_0x04
4.    \ "Network Information"
5.    \ Local IP: (10.42.82.181 in my case)

### Get an ubuntu_2204 Sandbox

1.    \>_ Get a sandbox
2.    \ Europe (Paris)
3.    \ ubuntu_2204
4.    \ login (SSH or Webterminal)

```bash
ssh -p 18331 root@ssh.cod-eu-west-3.hbtn.io
# Password: c4db717d67804c48bda4190dbcd9cdb2

# install nmap
apt update
apt install nmap

# run nmap
# -sU        UDP scan
# -sV        service version detection
# -p200-300  UDP port range 200-300
# <target IP> the IP of cyber_netsec_0x04 host

nmap -sU -sV -p200-300 10.42.82.181
# Starting Nmap 7.80 ( https://nmap.org ) at 2026-06-26 12:00 UTC
# Nmap scan report for 10.42.82.181
# Host is up (0.00081s latency).
# Not shown: 100 closed ports
# PORT    STATE SERVICE VERSION
  255/udp open  mdns    Lexmark - Holberton Sec Lab - cf33b0802fa80ee471822b3bfd78001c - printer mdns
# MAC Address: 0A:9A:9D:D1:51:D3 (Unknown)
# Service Info: Device: printer; CPE: cpe:/h:lexmark:-_holberton_sec_lab_-_cf33b0802fa80ee471822b3bfd78001c_-

# Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
# Nmap done: 1 IP address (1 host up) scanned in 137.56 seconds
```

Save flag on a local terminal:

```bash
echo cf33b0802fa80ee471822b3bfd78001c > 100-flag.txt

# check
cat 100-flag.txt
# cf33b0802fa80ee471822b3bfd78001c
```
