## 1. Download the PCAP file task3-dns-analysis.pcap associated with this task.

- click on [pcaps/task3-dns-analysis.pcap](https://web-80-18-51.cod-eu-west-3.hbtn.io/api/assets/pcaps/task3-dns-analysis.pcap)

## 2. Open it in Wireshark, **tshark**, or tcpdump.

```bash
tshark -r task3-dns-analysis.pcap                                         
#    1   0.000000  172.16.0.20 → 1.1.1.1      DNS 64 Standard query 0x0000 A malicious-site.com
#    2   0.000370      1.1.1.1 → 172.16.0.20  DNS 98 Standard query response 0x0000 A malicious-site.com A 192.0.2.100
#    3   0.000993  172.16.0.20 → 1.1.1.1      DNS 65 Standard query 0x0000 A legitimate-site.org
#    4   0.081497      1.1.1.1 → 172.16.0.20  DNS 100 Standard query response 0x0000 A legitimate-site.org A 198.51.100.50
```

## 3. Filter for DNS traffic (UDP port 53).

```bash
#    1   0.000000  172.16.0.20 → 1.1.1.1      DNS 64 Standard query 0x0000 A malicious-site.com
#    2   0.000370      1.1.1.1 → 172.16.0.20  DNS 98 Standard query response 0x0000 A malicious-site.com A 192.0.2.100
#    3   0.000993  172.16.0.20 → 1.1.1.1      DNS 65 Standard query 0x0000 A legitimate-site.org
#    4   0.081497      1.1.1.1 → 172.16.0.20  DNS 100 Standard query response 0x0000 A legitimate-site.org A 198.51.100.50
```

Filtering for DNS traffic is not reducing the workload -- everything is DNS traffic in this pcap.

## 4. Identify all DNS queries and their corresponding responses.

```bash
tshark -r task3-dns-analysis.pcap -Y 'udp.port == 53' \
-T fields \
-E header=y \
-E separator=$'\t' \
-e frame.number \
-e dns.flags.response \
-e ip.src \
-e ip.dst \
-e udp.srcport \
-e udp.dstport \
-e dns.qry.name \
-e dns.a

# frame.number    dns.flags.response      ip.src  ip.dst  udp.srcport     udp.dstport     dns.qry.name    dns.a
# 1       False   172.16.0.20     1.1.1.1 54321   53      malicious-site.com
# 2       True    1.1.1.1 172.16.0.20     53      54321   malicious-site.com      192.0.2.100
# 3       False   172.16.0.20     1.1.1.1 54322   53      legitimate-site.org
# 4       True    1.1.1.1 172.16.0.20     53      54322   legitimate-site.org     198.51.100.50
```

The fields are somewhat mis-aligned, lets fix this with `awk` and `column` magic:

```bash
tshark -r task3-dns-analysis.pcap -Y 'udp.port == 53' \
-T fields \
-E header=y \
-E separator=$'\t' \
-e frame.number \
-e dns.flags.response \
-e udp.srcport \
-e udp.dstport \
-e dns.qry.name \
-e dns.a \
| awk 'BEGIN{FS=OFS="\t"} NR==1{$1="frame";$2="response";$3="sport";$4="dport";$5="domain";$6="answer"} {print}' \
| column -t -s $'\t'

# frame  response  sport  dport  domain               answer
# 1      False     54321  53     malicious-site.com   
# 2      True      53     54321  malicious-site.com   192.0.2.100
# 3      False     54322  53     legitimate-site.org  
# 4      True      53     54322  legitimate-site.org  198.51.100.50
```

## 5. Compare the domain names queried and identify the suspicious domain.

- suspicious domain: `malicious-site.com` - it has a suspicious name :-)

## 6. Find the IP address resolved for the suspicious domain in the DNS response.

- suspicious ip: `192.0.2.100`

## Submission Format

- Submit your answer as JSON: `{"domain": "malicious-site.com", "ip": "192.0.2.100"}`
- put `{"domain": "malicious-site.com", "ip": "192.0.2.100"}` in the textbox
- \ "Submit answer"
- result: `Flag: 314c4cc17b1492ae9610cab35b922329`

```bash
echo -n 314c4cc17b1492ae9610cab35b922329 > 2-flag.txt

# trust but verify
cat 2-flag.txt
# 314c4cc17b1492ae9610cab35b922329
```