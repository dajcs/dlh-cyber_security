## 1. Download the PCAP file task7-malicious-traffic.pcap associated with this task.

- click on [pcaps/task7-malicious-traffic.pcap](https://web-80-221-173.cod-eu-west-3.hbtn.io/api/assets/pcaps/task7-malicious-traffic.pcap)


## 2. Open it in Wireshark, **tshark**, or tcpdump.

```bash
tshark -r task7-malicious-traffic.pcap          
#    1   0.000000 192.168.50.100 → 93.184.216.34 HTTP 58 GET / HTTP/1.1 
#    2   0.000256 192.168.50.100 → 198.18.0.1   TCP 40 55001 → 4444 [SYN] Seq=0 Win=8192 Len=0
#    3   0.000379   198.18.0.1 → 192.168.50.100 TCP 40 4444 → 55001 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    4   0.000500 192.168.50.100 → 8.8.8.8      DNS 57 Standard query 0x0000 A example.com
#    5   0.000895 192.168.50.100 → 198.18.0.1   TCP 40 55003 → 4444 [SYN] Seq=0 Win=8192 Len=0
#    6   0.001020   198.18.0.1 → 192.168.50.100 TCP 40 4444 → 55003 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    7   0.001144 192.168.50.100 → 198.18.0.1   TCP 69 55004 → 4444 [PSH, ACK] Seq=1 Ack=1 Win=8192 Len=29
```


## 3. Analyze the traffic to identify repeated connections to the same destination (beaconing pattern).

- **Beaconing pattern**: when an internal machine repeatedly contacts the same external destination at regular or semi-regular intervals. In plain terms:

  ```bash
  infected host -> C2 server
  infected host -> C2 server
  infected host -> C2 server
  ...
  ```
  The repeated connection attempt to the same IP and port is a beaconing pattern.

- **C2 server**: means **Command and Control server**

  It is the attacker-controlled server that malware communicates with after infecting a machine.<BR>
  The infected machine, sometimes called a bot, implant, agent, or beacon, contacts the C2 server to:
    - check in
    - receive commands
    - upload stolen data
    - download additional payloads
    - report host information
    - receive configuration updates

All TCP SYN packets:

```bash
tshark -r task7-malicious-traffic.pcap \
-Y 'tcp.flags.syn == 1' \
-T fields \
-E header=y \
-E separator=$'\t' \
-e frame.number \
-e ip.src \
-e tcp.srcport \
-e ip.dst \
-e tcp.dstport \
-e tcp.flags.syn \
-e tcp.flags.ack \
| column -t -s $'\t'

# frame.number  ip.src          tcp.srcport  ip.dst          tcp.dstport  tcp.flags.syn  tcp.flags.ack
# 2             192.168.50.100  55001        198.18.0.1      4444         True           False
# 3             198.18.0.1      4444         192.168.50.100  55001        True           True
# 5             192.168.50.100  55003        198.18.0.1      4444         True           False
# 6             198.18.0.1      4444         192.168.50.100  55003        True           True
```

## 4. Identify the C2 (Command and Control) server IP address and port.

Checking for outgoing TCP connection initiation (tcp.syn == True && tcp.ack == false)

```bash
tshark -r task7-malicious-traffic.pcap \
-Y 'tcp.flags.syn == 1 && tcp.flags.ack == 0' \
-T fields \
-E header=y \
-E separator=$'\t' \
-e ip.src \
-e tcp.srcport \
-e ip.dst \
-e tcp.dstport \
| column -t -s $'\t'

# ip.src          tcp.srcport  ip.dst      tcp.dstport
# 192.168.50.100  55001        198.18.0.1  4444
# 192.168.50.100  55003        198.18.0.1  4444
```

- **bot**: `192.168.50.100:55001`
- **C2**: `198.18.0.1:4444`


## 5. Count the number of beacon connections (SYN packets to the suspicious IP:port).

```bash
tshark -r task7-malicious-traffic.pcap \
-Y 'tcp.flags.syn == 1 && tcp.flags.ack == 0 && ip.dst == 198.18.0.1 && tcp.dstport == 4444' \
| wc -l

# 2
```


## 6. Locate and extract the exfiltration keyword from the data payload sent to the suspicious server.

Decoding the TCP payload sent to C2:

```bash
tshark -r task7-malicious-traffic.pcap \
-Y 'ip.dst == 198.18.0.1 && tcp.dstport == 4444 && tcp.payload' \
-T fields \
-e tcp.payload \
| xxd -r -p

# EXFIL:confidential_data_12345
```


## Submission Format

- Submit the answer as JSON: 
  `{"beacon_ip": "X.X.X.X", "beacon_port": XXXX, "beacon_count": X, "exfil_keyword": "keyword"}`
- put `{"beacon_ip":"198.18.0.1","beacon_port":4444,"beacon_count":2,"exfil_keyword":"EXFIL:confidential_data_12345"}` in the textbox
- \ "Submit answer"
- result: `Flag: 105aad222111e188cea7a515b3b41654`

```bash
echo -n 105aad222111e188cea7a515b3b41654 > 6-flag.txt

# trust but verify
cat 6-flag.txt
# 105aad222111e188cea7a515b3b41654
```