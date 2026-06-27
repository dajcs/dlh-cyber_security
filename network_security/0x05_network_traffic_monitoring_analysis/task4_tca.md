## 1. Download the PCAP file task4-tcp-analysis.pcap associated with this task.

- click on [pcaps/task4-tcp-analysis.pcap](https://web-80-18-51.cod-eu-west-3.hbtn.io/api/assets/pcaps/task4-tcp-analysis.pcap)


## 2. Open it in Wireshark, **tshark**, or tcpdump.

```bash
tshark -r task4-tcp-analysis.pcap 
#    1   0.000000 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [SYN] Seq=0 Win=8192 Len=0
#    2   0.000152 203.0.113.20 → 192.168.10.5 TCP 40 8080 → 50000 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    3   0.000275 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    4   0.000403 192.168.10.5 → 203.0.113.20 TCP 53 50000 → 8080 [PSH, ACK] Seq=1 Ack=4294965296 Win=8192 Len=13
#    5   0.000642 192.168.10.5 → 203.0.113.20 TCP 40 [TCP Previous segment not captured] 50000 → 8080 [FIN, ACK] Seq=15 Ack=1 Win=8192 Len=0
#    6   0.000761 203.0.113.20 → 192.168.10.5 TCP 40 [TCP ACKed unseen segment] 8080 → 50000 [FIN, ACK] Seq=1 Ack=16 Win=8192 Len=0
#    7   0.000993 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [ACK] Seq=16 Ack=2 Win=8192 Len=0
```


## 3. Filter for TCP traffic.

```bash
tshark -r task4-tcp-analysis.pcap -Y tcp
#    1   0.000000 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [SYN] Seq=0 Win=8192 Len=0
#    2   0.000152 203.0.113.20 → 192.168.10.5 TCP 40 8080 → 50000 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    3   0.000275 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    4   0.000403 192.168.10.5 → 203.0.113.20 TCP 53 50000 → 8080 [PSH, ACK] Seq=1 Ack=4294965296 Win=8192 Len=13
#    5   0.000642 192.168.10.5 → 203.0.113.20 TCP 40 [TCP Previous segment not captured] 50000 → 8080 [FIN, ACK] Seq=15 Ack=1 Win=8192 Len=0
#    6   0.000761 203.0.113.20 → 192.168.10.5 TCP 40 [TCP ACKed unseen segment] 8080 → 50000 [FIN, ACK] Seq=1 Ack=16 Win=8192 Len=0
#    7   0.000993 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [ACK] Seq=16 Ack=2 Win=8192 Len=0

tshark -r task4-tcp-analysis.pcap -Y tcp | wc -l                   
# 7
```

Total packets: `7`

All traffic is TCP traffic.


## 4. Identify and count the SYN packets (connection initiation).

```bash
tshark -r task4-tcp-analysis.pcap -Y "tcp.flags.syn==1"
#    1   0.000000 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [SYN] Seq=0 Win=8192 Len=0
#    2   0.000152 203.0.113.20 → 192.168.10.5 TCP 40 8080 → 50000 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0

tshark -r task4-tcp-analysis.pcap -Y "tcp.flags.syn==1" | wc -l
# 2
```

Nr SYN packets: `2`


## 5. Identify and count the FIN packets (connection termination).

```bash
tshark -r task4-tcp-analysis.pcap -Y "tcp.flags.fin==1"

#    5   0.000642 192.168.10.5 → 203.0.113.20 TCP 40 [TCP Previous segment not captured] 50000 → 8080 [FIN, ACK] Seq=15 Ack=1 Win=8192 Len=0
#    6   0.000761 203.0.113.20 → 192.168.10.5 TCP 40 [TCP ACKed unseen segment] 8080 → 50000 [FIN, ACK] Seq=1 Ack=16 Win=8192 Len=0

tshark -r task4-tcp-analysis.pcap -Y "tcp.flags.fin==1" | wc -l
# 2
```

Nr FIN packets: `2`


## 6. Determine the destination port used for the connection.

```bash
tshark -r task4-tcp-analysis.pcap -Y "tcp.flags.syn==1 && tcp.flags.ack == 0" -T fields -e tcp.dstport
# 8080
```

Destination port: `8080`


## 7. Count the total number of TCP packets in the connection.

```bash
tshark -r task4-tcp-analysis.pcap -Y tcp
#    1   0.000000 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [SYN] Seq=0 Win=8192 Len=0
#    2   0.000152 203.0.113.20 → 192.168.10.5 TCP 40 8080 → 50000 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    3   0.000275 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    4   0.000403 192.168.10.5 → 203.0.113.20 TCP 53 50000 → 8080 [PSH, ACK] Seq=1 Ack=4294965296 Win=8192 Len=13
#    5   0.000642 192.168.10.5 → 203.0.113.20 TCP 40 [TCP Previous segment not captured] 50000 → 8080 [FIN, ACK] Seq=15 Ack=1 Win=8192 Len=0
#    6   0.000761 203.0.113.20 → 192.168.10.5 TCP 40 [TCP ACKed unseen segment] 8080 → 50000 [FIN, ACK] Seq=1 Ack=16 Win=8192 Len=0
#    7   0.000993 192.168.10.5 → 203.0.113.20 TCP 40 50000 → 8080 [ACK] Seq=16 Ack=2 Win=8192 Len=0

tshark -r task4-tcp-analysis.pcap -Y tcp | wc -l                   
# 7
```

Total packets: `7`


## Table format

```bash
tshark -r task4-tcp-analysis.pcap -Y 'tcp' \
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
-e tcp.flags.fin \
-e tcp.len \
| column -t -s $'\t'
frame.number  ip.src        tcp.srcport  ip.dst        tcp.dstport  tcp.flags.syn  tcp.flags.ack  tcp.flags.fin  tcp.len
1             192.168.10.5  50000        203.0.113.20  8080         True           False          False          0
2             203.0.113.20  8080         192.168.10.5  50000        True           True           False          0
3             192.168.10.5  50000        203.0.113.20  8080         False          True           False          0
4             192.168.10.5  50000        203.0.113.20  8080         False          True           False          13
5             192.168.10.5  50000        203.0.113.20  8080         False          True           True           0
6             203.0.113.20  8080         192.168.10.5  50000        False          True           True           0
7             192.168.10.5  50000        203.0.113.20  8080         False          True           False          0
```

Frame 2 has both `SYN` and `ACK`, and frames 5 and 6 have both ACK and FIN.

TCP headers can be: `SYN  ACK  FIN  PSH  RST  URG`. Independently.

Frame 2 has `SYN` + `ACK`. The handshake in Frames 1, 2, 3:

```bash
1  client -> server   SYN        # client: I'd like to have a chat
2  server -> client   SYN, ACK   # server: Me too I'd like to chat. And I ACKnowledge your SYN.
3  client -> server   ACK        # client: I ACKnowledge your SYN as well.
```

Frame 5, 6, 7:

```bash
5  client -> server   FIN, ACK  # client: I'm FINished sending data. And I ACKnowledge stuff from you.
6  server -> client   FIN, ACK  # server: I'm also FINished sending data. And I ACKnowledge your FIN + previous data.
7  client -> server   ACK       # client: I'm ACKnowledging your FIN.
```

The whole capture "translated":

```bash
frame  flags      meaning
1      SYN        Client asks to open connection
2      SYN, ACK   Server accepts and acknowledges client SYN
3      ACK        Client acknowledges server SYN, handshake complete
4      PSH, ACK   Client sends 13 bytes of data - PSH -> Push - deliver data to application ASAP, do not buffer
5      FIN, ACK   Client wants to close its side
6      FIN, ACK   Server wants to close its side and acknowledges
7      ACK        Client acknowledges server FIN, connection closed
```


## Submission Format

- Submit your answer as JSON: `{"syn_packets": X, "fin_packets": X, "destination_port": XXXX, "total_packets": X}`
- put `{"syn_packets": 2, "fin_packets": 2, "destination_port": 8080, "total_packets": 7}` in the textbox
- \ "Submit answer"
- \ result :-(
- maybe we need to count only the initial client SYN <BR>
  put `{"syn_packets": 1, "fin_packets": 2, "destination_port": 8080, "total_packets": 7}` in the textbox
- \ "Submit answer"
- result: `Flag: 487a57e222f023e7842393d6f3d74145`

```bash
echo -n 487a57e222f023e7842393d6f3d74145 > 3-flag.txt

# trust but verify
cat 3-flag.txt
# 487a57e222f023e7842393d6f3d74145
```