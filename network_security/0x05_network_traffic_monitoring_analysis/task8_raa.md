## 1. Download the PCAP file task7-malicious-traffic.pcap associated with this task.

- click on [pcaps/task7-malicious-traffic.pcap](https://web-80-221-173.cod-eu-west-3.hbtn.io/api/assets/pcaps/task7-malicious-traffic.pcap)


## 2. Open it in Wireshark, **tshark**, or tcpdump.

```bash
tshark -r task8-rdp-analysis.pcap       
#    1   0.000000 192.168.50.200 → 10.10.10.50  TCP 40 50001 → 3389 [SYN] Seq=0 Win=8192 Len=0
#    2   0.000139  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50001 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    3   0.000280 192.168.50.200 → 10.10.10.50  TCP 40 50001 → 3389 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    4   0.000406 192.168.50.200 → 10.10.10.50  TPKT 79 Continuation
#    5   0.000814  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50001 [FIN, ACK] Seq=1 Ack=30 Win=8192 Len=0
#    6   0.000945 192.168.50.200 → 10.10.10.50  TCP 40 50002 → 3389 [SYN] Seq=0 Win=8192 Len=0
#    7   0.001067  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50002 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    8   0.001187 192.168.50.200 → 10.10.10.50  TCP 40 50002 → 3389 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    9   0.001307 192.168.50.200 → 10.10.10.50  TPKT 79 Continuation
#   10   0.001539  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50002 [FIN, ACK] Seq=1 Ack=30 Win=8192 Len=0
#   11   0.001704 192.168.50.200 → 10.10.10.50  TCP 40 50003 → 3389 [SYN] Seq=0 Win=8192 Len=0
#   12   0.001825  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50003 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#   13   0.001947 192.168.50.200 → 10.10.10.50  TCP 40 50003 → 3389 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#   14   0.002068 192.168.50.200 → 10.10.10.50  TPKT 79 Continuation
#   15   0.002298  10.10.10.50 → 192.168.50.200 TPKT 55 Continuation
```


## 3. Filter for RDP traffic on port 3389 (standard RDP port).

```bash
tshark -r task8-rdp-analysis.pcap -Y 'tcp.port == 3389'  

#    1   0.000000 192.168.50.200 → 10.10.10.50  TCP 40 50001 → 3389 [SYN] Seq=0 Win=8192 Len=0
#    2   0.000139  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50001 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    3   0.000280 192.168.50.200 → 10.10.10.50  TCP 40 50001 → 3389 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    4   0.000406 192.168.50.200 → 10.10.10.50  TPKT 79 Continuation
#    5   0.000814  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50001 [FIN, ACK] Seq=1 Ack=30 Win=8192 Len=0
#    6   0.000945 192.168.50.200 → 10.10.10.50  TCP 40 50002 → 3389 [SYN] Seq=0 Win=8192 Len=0
#    7   0.001067  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50002 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    8   0.001187 192.168.50.200 → 10.10.10.50  TCP 40 50002 → 3389 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    9   0.001307 192.168.50.200 → 10.10.10.50  TPKT 79 Continuation
#   10   0.001539  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50002 [FIN, ACK] Seq=1 Ack=30 Win=8192 Len=0
#   11   0.001704 192.168.50.200 → 10.10.10.50  TCP 40 50003 → 3389 [SYN] Seq=0 Win=8192 Len=0
#   12   0.001825  10.10.10.50 → 192.168.50.200 TCP 40 3389 → 50003 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#   13   0.001947 192.168.50.200 → 10.10.10.50  TCP 40 50003 → 3389 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#   14   0.002068 192.168.50.200 → 10.10.10.50  TPKT 79 Continuation
#   15   0.002298  10.10.10.50 → 192.168.50.200 TPKT 55 Continuation
```

- Filtering on RDP port 3389 is not reducing our workload, all 15 frames are RDP 3389
- A more useful table:

```bash
tshark -r task8-rdp-analysis.pcap -Y 'tcp.port == 3389' \
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
-e tcp.flags.push \
-e tcp.len \
| column -t -s $'\t'

# frame.number  ip.src          tcp.srcport  ip.dst          tcp.dstport  tcp.flags.syn  tcp.flags.ack  tcp.flags.fin  tcp.flags.push  tcp.len
# 1             192.168.50.200  50001        10.10.10.50     3389         True           False          False          False           0
# 2             10.10.10.50     3389         192.168.50.200  50001        True           True           False          False           0
# 3             192.168.50.200  50001        10.10.10.50     3389         False          True           False          False           0
# 4             192.168.50.200  50001        10.10.10.50     3389         False          True           False          True            39
# 5             10.10.10.50     3389         192.168.50.200  50001        False          True           True           False           0
# 6             192.168.50.200  50002        10.10.10.50     3389         True           False          False          False           0
# 7             10.10.10.50     3389         192.168.50.200  50002        True           True           False          False           0
# 8             192.168.50.200  50002        10.10.10.50     3389         False          True           False          False           0
# 9             192.168.50.200  50002        10.10.10.50     3389         False          True           False          True            39
# 10            10.10.10.50     3389         192.168.50.200  50002        False          True           True           False           0
# 11            192.168.50.200  50003        10.10.10.50     3389         True           False          False          False           0
# 12            10.10.10.50     3389         192.168.50.200  50003        True           True           False          False           0
# 13            192.168.50.200  50003        10.10.10.50     3389         False          True           False          False           0
# 14            192.168.50.200  50003        10.10.10.50     3389         False          True           False          True            39
# 15            10.10.10.50     3389         192.168.50.200  50003        False          True           False          True            15
```


## 4. Identify the source IP address making multiple connection attempts.

- filtering for initial tcp connection with tcp.syn == 1 && tcp.ack == 0

```bash
tshark -r task8-rdp-analysis.pcap \
-Y 'tcp.dstport == 3389 && tcp.flags.syn == 1 && tcp.flags.ack == 0' \
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
-e tcp.flags.push \
-e tcp.len \
| column -t -s $'\t'

# frame.number  ip.src          tcp.srcport  ip.dst       tcp.dstport  tcp.flags.syn  tcp.flags.ack  tcp.flags.fin  tcp.flags.push  tcp.len
# 1             192.168.50.200  50001        10.10.10.50  3389         True           False          False          False           0
# 6             192.168.50.200  50002        10.10.10.50  3389         True           False          False          False           0
# 11            192.168.50.200  50003        10.10.10.50  3389         True           False          False          False           0
```

- source ip: `192.168.50.200`


## 5. Count the number of connection attempts (SYN packets to port 3389).

```bash
tshark -r task8-rdp-analysis.pcap \
-Y 'tcp.dstport == 3389 && tcp.flags.syn == 1 && tcp.flags.ack == 0' \
| wc -l

# 3
```

- number of connection attempts: `3`


## 5. Extract usernames from RDP authentication packets by viewing the traffic in ASCII format.

- showing payload-bearing packets sent to RDP:

```bash
tshark -r task8-rdp-analysis.pcap \
-Y 'tcp.dstport == 3389 && tcp.payload' \
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

# frame.number  tcp.stream  ip.src          tcp.srcport  ip.dst       tcp.dstport  tcp.payload
# 4             0           192.168.50.200  50001        10.10.10.50  3389         030000130ee00000000000010008000300000061646d696e000000000000000000000000000000
# 9             1           192.168.50.200  50002        10.10.10.50  3389         0300001b0ee00000000000010008000300000061646d696e6973747261746f7200000000000000
# 14            2           192.168.50.200  50003        10.10.10.50  3389         030000110ee000000000000100080003000000726f6f7400000000000000000000000000000000
```

- decoding the payloads from ASCII hex to characters:

```bash
tshark -r task8-rdp-analysis.pcap \
-Y 'tcp.dstport == 3389 && tcp.payload' \
-T fields \
-e tcp.payload \
| xxd -r -p \
| strings

# admin
# administrator
# root
```

Displaying the usernames with frame and stream id:

```bash
tshark -r task8-rdp-analysis.pcap \
-Y 'tcp.dstport == 3389 && tcp.payload' \
-T fields \
-E separator=$'\t' \
-e frame.number \
-e tcp.stream \
-e tcp.payload \
| while IFS=$'\t' read -r frame stream payload; do
    echo "frame=$frame stream=$stream"
    echo "$payload" | xxd -r -p | strings
    echo
  done

# frame=4 stream=0
# admin

# frame=9 stream=1
# administrator

# frame=14 stream=2
# root
```


## 6. Determine which username successfully authenticated by analyzing server response patterns.

```bash
tshark -r task8-rdp-analysis.pcap -Y 'tcp.port == 3389' \
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
-e tcp.flags.push \
-e tcp.stream \
-e tcp.len \
| column -t -s $'\t'

# frame.number  ip.src          tcp.srcport  ip.dst          tcp.dstport  tcp.flags.syn  tcp.flags.ack  tcp.flags.fin  tcp.flags.push  tcp.stream  tcp.len
# 1             192.168.50.200  50001        10.10.10.50     3389         True           False          False          False           0           0
# 2             10.10.10.50     3389         192.168.50.200  50001        True           True           False          False           0           0
# 3             192.168.50.200  50001        10.10.10.50     3389         False          True           False          False           0           0
# 4             192.168.50.200  50001        10.10.10.50     3389         False          True           False          True            0           39
# 5             10.10.10.50     3389         192.168.50.200  50001        False          True           True           False           0           0

# 6             192.168.50.200  50002        10.10.10.50     3389         True           False          False          False           1           0
# 7             10.10.10.50     3389         192.168.50.200  50002        True           True           False          False           1           0
# 8             192.168.50.200  50002        10.10.10.50     3389         False          True           False          False           1           0
# 9             192.168.50.200  50002        10.10.10.50     3389         False          True           False          True            1           39
# 10            10.10.10.50     3389         192.168.50.200  50002        False          True           True           False           1           0

# 11            192.168.50.200  50003        10.10.10.50     3389         True           False          False          False           2           0
# 12            10.10.10.50     3389         192.168.50.200  50003        True           True           False          False           2           0
# 13            192.168.50.200  50003        10.10.10.50     3389         False          True           False          False           2           0
# 14            192.168.50.200  50003        10.10.10.50     3389         False          True           False          True            2           39
# 15            10.10.10.50     3389         192.168.50.200  50003        False          True           False          True            2           15
```

Server response pattern:

```bash
admin           -> server replies FIN, closing the connection
administrator   -> server replies FIN, closing the connection
root            -> server replies with PSH/ACK payload
```

- successful username: `root`


## Submission Format

- Submit your answer as JSON:  or as a simple string: X.X.X.X:N:username****
  `{"rdp_port": 3389, "attacker_ip": "X.X.X.X", "connection_attempts": N, "successful_username": "username"}`
  or as a simple string: `X.X.X.X:N:username`
- put `{"rdp_port": 3389, "attacker_ip": "192.168.50.200", "connection_attempts": 3, "successful_username": "root"}` in the textbox
- \ "Submit answer"
- result: `Flag: ac1c9ccc722c484caeb9607980406347`

```bash
echo -n ac1c9ccc722c484caeb9607980406347 > 7-flag.txt

# trust but verify
cat 7-flag.txt
# ac1c9ccc722c484caeb9607980406347
```
