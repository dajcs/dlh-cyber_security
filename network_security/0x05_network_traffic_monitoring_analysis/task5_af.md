## 1. Download the PCAP file task4-tcp-analysis.pcap associated with this task.

- click on [pcaps/task5-advanced-filtering.pcap](https://web-80-221-173.cod-eu-west-3.hbtn.io/api/assets/pcaps/task5-advanced-filtering.pcap)


## 2. Open it in Wireshark, **tshark**, or tcpdump.

```bash
tshark -r task5-advanced-filtering.pcap     
#    1   0.000000    10.1.1.50 → 203.0.113.5  HTTP 68 GET /index.html HTTP/1.1 
#    2   0.000282    10.1.1.50 → 203.0.113.5  TCP 40 40002 → 443 [SYN] Seq=0 Win=8192 Len=0
#    3   0.000404    10.1.1.50 → 8.8.8.8      DNS 56 Standard query 0x0000 A google.com
#    4   0.000804    10.1.1.50 → 8.8.8.8      ICMP 28 Echo (ping) request  id=0x0000, seq=0/0, ttl=64
#    5   0.001059    10.1.1.50 → 203.0.113.15 FTP 54 Request: USER ftpuser
#    6   0.001307    10.1.1.50 → 203.0.113.15 TCP 61 [TCP Retransmission] 40003 → 21 [PSH, ACK] Seq=1 Ack=1 Win=8192 Len=21
#    7   0.001549    10.1.1.50 → 203.0.113.5  HTTP 68 GET /about.html HTTP/1.1 
#    8   0.001784    10.1.1.50 → 8.8.8.8      DNS 56 Standard query 0x0000 A github.com
```


## 3. The capture contains mixed traffic: HTTP, HTTPS, DNS, ICMP, and FTP.


Filtering for TCP and displaying useful TCP fields:

```bash
tshark -r task5-advanced-filtering.pcap  \
-T fields \
-E header=y \
-E separator=$'\t' \
-e frame.number \
-e ip.src \
-e tcp.srcport \
-e udp.srcport \
-e ip.dst \
-e tcp.dstport \
-e udp.dstport \
-e frame.protocols\
| column -t -s $'\t'

# frame.number  ip.src     tcp.srcport  udp.srcport  ip.dst        tcp.dstport  udp.dstport  frame.protocols
# 1             10.1.1.50  40001                     203.0.113.5   80                        raw:ip:tcp:http
# 2             10.1.1.50  40002                     203.0.113.5   443                       raw:ip:tcp
# 3             10.1.1.50               50001        8.8.8.8                    53           raw:ip:udp:dns
# 4             10.1.1.50                            8.8.8.8                                 raw:ip:icmp
# 5             10.1.1.50  40003                     203.0.113.15  21                        raw:ip:tcp:ftp
# 6             10.1.1.50  40003                     203.0.113.15  21                        raw:ip:tcp
# 7             10.1.1.50  40004                     203.0.113.5   80                        raw:ip:tcp:http
# 8             10.1.1.50               50002        8.8.8.8                    53           raw:ip:udp:dns
```

That's right. We have here all the protocols listed: HTTP, HTTPS, DNS, ICMP, and FTP.


## 4. Apply filters to isolate FTP traffic (TCP port 21).


Showing TCP conversations:

```bash
tshark -r task5-advanced-filtering.pcap -Y ftp
#    5   0.001059    10.1.1.50 → 203.0.113.15 FTP 54 Request: USER ftpuser
```

Filtering for FTP gets us only one message. <BR>
This is probably because the other FTP message is a TCP retransmission.
Let's give it a try filtering for tcp.port == 21 might bring us more to the table.

```bash
tshark -r task5-advanced-filtering.pcap -Y "tcp.port==21"
#    5   0.001059    10.1.1.50 → 203.0.113.15 FTP 54 Request: USER ftpuser
#    6   0.001307    10.1.1.50 → 203.0.113.15 TCP 61 [TCP Retransmission] 40003 → 21 [PSH, ACK] Seq=1 Ack=1 Win=8192 Len=21
```

Much better. Now we have 2 frames to examine further.


## 5. Locate the FTP PASS command in the traffic.

- We have to find the `PASS` string in the payload.
- The `PASS` string expressed in ASCII hex: `50 41 53 53`

```bash
tshark -r task5-advanced-filtering.pcap \
-Y 'tcp.payload contains 50:41:53:53' \
-T fields \
-E header=y \
-E separator=$'\t' \
-e frame.number \
-e tcp.stream \
-e ip.src \
-e tcp.srcport \
-e ip.dst \
-e tcp.dstport \
-e tcp.payload \
| column -t -s $'\t'

# frame.number  tcp.stream  ip.src     tcp.srcport  ip.dst        tcp.dstport  tcp.payload
# 6             2           10.1.1.50  40003        203.0.113.15  21           50415353 53656372657446545032303234210d0a
```

## 6. Extract the FTP password from the command.

- Decoding the matching PASS command, coverting the ASCII hex to characters:

```bash
tshark -r task5-advanced-filtering.pcap \
# -Y 'tcp.payload contains 50:41:53:53' \
# -T fields \
# -e tcp.payload \
# | xxd -r -p
# PASS SecretFTP2024!
```

## 7. Submission Format

- Submit the FTP password as a plain text string
- put `SecretFTP2024!` in the textbox
- \ "Submit answer"
- result: `Flag: 564d209156442acfc2eafac661a9bfd2`

```bash
echo -n 564d209156442acfc2eafac661a9bfd2 > 4-flag.txt

# trust but verify
cat 4-flag.txt
# 564d209156442acfc2eafac661a9bfd2
```