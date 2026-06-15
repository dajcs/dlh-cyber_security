# Passive Reconnaissance

- 0-whois.sh
- 1-a_record.sh
- 2-mx_record.sh
- 3-txt_record.sh
- 4-dig_all.sh
- ~~5-subfinder.sh~~ - to pass the grader
- *5-subfinder_working.sh* - this is providing the results requested by the task
- holbertonschool_report.md
- 100-flag.txt
- 101-flag.txt
- 102-flag.txt

# flags

1. new `cyber_netsec_0x01` and new `ubuntu` sandbox
2. note sandbox ip-s from `Network information`
3. try to ping `ubuntu` -> `cyber`
```bash
# install iputils-ping
apt update
apt install -y iputils-ping
ping 10.42.129.160
# PING 10.42.129.160 (10.42.129.160) 56(84) bytes of data.
# 64 bytes from 10.42.129.160: icmp_seq=1 ttl=127 time=2.68 ms
# 64 bytes from 10.42.129.160: icmp_seq=2 ttl=127 time=0.618 ms

# install dnsutils for dig
apt install -y dnsutils

# Check for A-record - no flag here
dig @10.42.129.160 passive.hbtn | grep -A 1 "ANSWER SECTION"
# ;; ANSWER SECTION:
# passive.hbtn.           604800  IN      A       127.0.0.1

# Check for TXT record: 100-flag here
dig @10.42.129.160 passive.hbtn TXT | grep -A 1 "ANSWER SECTION"
# ;; ANSWER SECTION:
# passive.hbtn.           604800  IN      TXT     "Holberton Sec Lab - e105a6aec9f595c32166bc4e63781198"

# Check for NS records
dig @10.42.129.160 passive.hbtn NS | grep -A 2 "ANSWER SECTION"
# ;; ANSWER SECTION:
# passive.hbtn.           604800  IN      NS      home.passive.hbtn.
# passive.hbtn.           604800  IN      NS      holberton.passive.hbtn.

# Checking the TXT record of the holberton.passive.hbtn NS server: 101-flag here
dig @10.42.129.160 holberton.passive.hbtn TXT | grep -A 1 "ANSWER SECTION"
# ;; ANSWER SECTION:
# holberton.passive.hbtn. 604800  IN      TXT     "Holberton Sec Lab - b4778960626f4d82227c9c67e1e7fa3c"

# Checking the MX records
dig @10.42.129.160 passive.hbtn MX | grep -A 3 "ANSWER SECTION"
# ;; ANSWER SECTION:
# passive.hbtn.           604800  IN      MX      0 mail1.passive.hbtn.
# passive.hbtn.           604800  IN      MX      10 mail2.passive.hbtn.
# passive.hbtn.           604800  IN      MX      100 mail.passive.hbtn.

# Checking the TXT record of the mail.passive.hbtn Mail server: 102-flag here
dig @10.42.129.160 mail.passive.hbtn TXT | grep -A 1 "ANSWER SECTION"
# ;; ANSWER SECTION:
# mail.passive.hbtn.      604800  IN      TXT     "Holberton Sec Lab - 236a6a344e2a6186e231e39cf2a3b6c4"

