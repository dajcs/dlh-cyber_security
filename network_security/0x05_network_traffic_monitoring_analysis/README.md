
# Network Traffic Monitoring & Analysis


## 0. Basic Packet Analysis

### Get a cyber_netsec_0x05 Sandbox

1.    \>_ Get a sandbox
2.    \ Europe (Paris)
3.    \ cyber_netsec_0x05
4.    \ "Network Information"
5.    \ "🌏︎ HTTP - Port 80" - this opens a new webpage ([https://web-80-18-51.cod-eu-west-3.hbtn.io/](https://web-80-18-51.cod-eu-west-3.hbtn.io/) in my case)
6.    Download the PCAP file from the "Basic Packet Analysis" [**pcaps/task1-basic-analysis.pcap**](https://web-80-18-51.cod-eu-west-3.hbtn.io/api/assets/pcaps/task1-basic-analysis.pcap)<BR>
 ([https://web-80-18-51.cod-eu-west-3.hbtn.io/api/assets/pcaps/task1-basic-analysis.pcap](https://web-80-18-51.cod-eu-west-3.hbtn.io/api/assets/pcaps/task1-basic-analysis.pcap) in my case)


## Play around with `tshark`

```bash
# tshark - the terminal version of the Wireshark GUI
# -r    read the provided .pcap file (instead of live traffic)
# -q    quiet - suppressing packet-by-packet output
# -z    run stats module
#       io,phs    Input/Output Protocol Hierarchy Statistics
tshark -r task1-basic-analysis.pcap
#     1   0.000000 192.168.1.100 → 93.184.216.34 TCP 40 54321 → 80 [SYN] Seq=0 Win=8192 Len=0
#     2   0.000279 93.184.216.34 → 192.168.1.100 TCP 40 80 → 54321 [SYN, ACK] Seq=0 Ack=0 Win=8192 Len=0
#     3   0.000422 192.168.1.100 → 8.8.8.8      DNS 57 Standard query 0x0000 A example.com
#     4   0.000886 192.168.1.100 → 8.8.8.8      ICMP 28 Echo (ping) request  id=0x0000, seq=0/0, ttl=64
#     5   0.001202 192.168.1.100 → 142.250.185.14 TCP 40 54322 → 443 [SYN] Seq=0 Win=8192 Len=0
                                                                                                                                                                                                                  
# ┌──(kali㉿kali)-[~/dlh-cyber_security/network_security/0x05_network_traffic_monitoring_analysis]
# └─$ 
tshark -r task1-basic-analysis.pcap -q
                                                                                                                                                                                                                  
# ┌──(kali㉿kali)-[~/dlh-cyber_security/network_security/0x05_network_traffic_monitoring_analysis]
# └─$ 
tshark -r task1-basic-analysis.pcap -q -z io,phs


# ===================================================================
# Protocol Hierarchy Statistics
# Filter: 
# 
# frame                                    frames:5 bytes:205
#   raw                                    frames:5 bytes:205
#     ip                                   frames:5 bytes:205
#       tcp                                frames:3 bytes:120
#       udp                                frames:1 bytes:57
#         dns                              frames:1 bytes:57
#       icmp                               frames:1 bytes:28
# ===================================================================
                                                                                                                                                                                                                  

#┌──(kali㉿kali)-[~/dlh-cyber_security/network_security/0x05_network_traffic_monitoring_analysis]
#└─$ 
tshark -r task1-basic-analysis.pcap -z io,phs 

#     1   0.000000 192.168.1.100 → 93.184.216.34 TCP 40 54321 → 80 [SYN] Seq=0 Win=8192 Len=0
#     2   0.000279 93.184.216.34 → 192.168.1.100 TCP 40 80 → 54321 [SYN, ACK] Seq=0 Ack=0 Win=8192 Len=0
#     3   0.000422 192.168.1.100 → 8.8.8.8      DNS 57 Standard query 0x0000 A example.com
#     4   0.000886 192.168.1.100 → 8.8.8.8      ICMP 28 Echo (ping) request  id=0x0000, seq=0/0, ttl=64
#     5   0.001202 192.168.1.100 → 142.250.185.14 TCP 40 54322 → 443 [SYN] Seq=0 Win=8192 Len=0
# 
# ===================================================================
# Protocol Hierarchy Statistics
# Filter: 
# 
# frame                                    frames:5 bytes:205
#   raw                                    frames:5 bytes:205
#     ip                                   frames:5 bytes:205
#       tcp                                frames:3 bytes:120
#       udp                                frames:1 bytes:57
#         dns                              frames:1 bytes:57
#       icmp                               frames:1 bytes:28
# ===================================================================
```

## `tshark` - Extract specific fields

```bash
# -T fields     Output: Field extraction mode
# -e ip.src     Export: source IP address
# -e ip.dst     Export: destination IP address
# -e tcp.srcport        TCP source port
# -e tcp.dstport        TCP destination port

tshark -r task1-basic-analysis.pcap -T fields -e ip.src
# 192.168.1.100
# 93.184.216.34
# 192.168.1.100
# 192.168.1.100
# 192.168.1.100
```

## Display filter

```bash
# -Y    apply display filter
# -Y http   show only HTTP packets
# -Y dns   show only DNS packets
# -Y "tcp.dstport == 80"    show only packets where tcp.dstport == 80
tshark -r task1-basic-analysis.pcap -Y "tcp.dstport == 80"
#    1   0.000000 192.168.1.100 → 93.184.216.34 TCP 40 54321 → 80 [SYN] Seq=0 Win=8192 Len=0
```

## Instruction 3: Identify all protocols present in the capture (HTTP, DNS, ICMP, HTTPS, etc.).

```bash
# export fields with frame number and frame protocols
tshark -r task1-basic-analysis.pcap -T fields -e frame.number -e frame.protocols 
# 1       raw:ip:tcp
# 2       raw:ip:tcp
# 3       raw:ip:udp:dns
# 4       raw:ip:icmp
# 5       raw:ip:tcp


# getting unique protocol names:
tshark -r task1-basic-analysis.pcap -T fields -e frame.protocols \
| tr ':' '\n' \
| sort \
| uniq
# dns
# icmp
# ip
# raw
# tcp
# udp
```

## Instruction 4: Determine the source IP address that appears in multiple packets.

```bash
tshark -r task1-basic-analysis.pcap -T fields -e ip.src
# 192.168.1.100
# 93.184.216.34
# 192.168.1.100
# 192.168.1.100
# 192.168.1.100
```
- source_ip: 192.168.1.100

## Instruction 5: Find the HTTP destination port (standard port for HTTP traffic).

There is no HTTP traffic, but the standard port for HTTP traffic is 80.
```bash
tshark -r task1-basic-analysis.pcap -Y "tcp.dstport == 80" -T fields \
-e ip.src -e tcp.srcport \
-e ip.dst -e tcp.dstport

# 192.168.1.100   54321   93.184.216.34   80

tshark -r task1-basic-analysis.pcap -Y "tcp.dstport == 80"
#     1   0.000000 192.168.1.100 → 93.184.216.34 TCP 40 54321 → 80 [SYN] Seq=0 Win=8192 Len=0

```
There is one TCP SYN packet to the port 80

## Submission Format: Submit your answer as JSON: {"source_ip": "X.X.X.X", "http_port": XX}

- put `{"source_ip": "192.168.1.100", "http_port": 80}` in the textbox
- \ "Submit answer"
- result: `Flag: 97914afe006c7292c693a2298ea9b153`

```bash
echo -n 97914afe006c7292c693a2298ea9b153 > 0-flag.txt

# trust but verify
cat 0-flag.txt
# 97914afe006c7292c693a2298ea9b153
```