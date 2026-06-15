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




- 0-ports.txt
