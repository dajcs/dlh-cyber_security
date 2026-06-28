## 1. Download the PCAP file task6-tcp-stream-reconstruction.pcap associated with this task.

- click on [pcaps/task6-tcp-stream-reconstruction.pcap](https://web-80-221-173.cod-eu-west-3.hbtn.io/api/assets/pcaps/task6-tcp-stream-reconstruction.pcap)


## 2. Open it in Wireshark, **tshark**, or tcpdump.

```bash
tshark -r task6-tcp-stream-reconstruction.pcap                  
#    1   0.000000  172.20.5.10 → 198.51.100.25 TCP 40 60000 → 9999 [SYN] Seq=0 Win=8192 Len=0
#    2   0.000153 198.51.100.25 → 172.20.5.10  TCP 40 9999 → 60000 [SYN, ACK] Seq=0 Ack=1 Win=8192 Len=0
#    3   0.000280  172.20.5.10 → 198.51.100.25 TCP 40 60000 → 9999 [ACK] Seq=1 Ack=1 Win=8192 Len=0
#    4   0.000401  172.20.5.10 → 198.51.100.25 TCP 50 60000 → 9999 [PSH, ACK] Seq=1 Ack=4294957296 Win=8192 Len=10
#    5   0.000686  172.20.5.10 → 198.51.100.25 TCP 52 [TCP Previous segment not captured] 60000 → 9999 [PSH, ACK] Seq=13 Ack=4294957296 Win=8192 Len=12
#    6   0.000924  172.20.5.10 → 198.51.100.25 TCP 44 [TCP Previous segment not captured] 60000 → 9999 [PSH, ACK] Seq=26 Ack=4294957296 Win=8192 Len=4
#    7   0.001155  172.20.5.10 → 198.51.100.25 TCP 40 60000 → 9999 [FIN, ACK] Seq=30 Ack=1 Win=8192 Len=0
#    8   0.001276 198.51.100.25 → 172.20.5.10  TCP 40 [TCP ACKed unseen segment] 9999 → 60000 [FIN, ACK] Seq=1 Ack=31 Win=8192 Len=0
#    9   0.001474  172.20.5.10 → 198.51.100.25 TCP 40 60000 → 9999 [ACK] Seq=31 Ack=2 Win=8192 Len=0
```


## 3. Identify the TCP connection (look for the three-way handshake).

TCP traffic compact view:

```bash
tshark -r task6-tcp-stream-reconstruction.pcap -Y 'tcp' \
-T fields \
-E header=y \
-E separator=$'\t' \
-e frame.number \
-e ip.src \
-e tcp.srcport \
-e ip.dst \
-e tcp.dstport \
-e tcp.stream \
-e tcp.flags.syn \
-e tcp.flags.ack \
-e tcp.flags.fin \
-e tcp.payload \
| column -t -s $'\t'

# frame.number  ip.src         tcp.srcport  ip.dst         tcp.dstport  tcp.stream  tcp.flags.syn  tcp.flags.ack  tcp.flags.fin  tcp.payload
# 1             172.20.5.10    60000        198.51.100.25  9999         0           True           False          False          
# 2             198.51.100.25  9999         172.20.5.10    60000        0           True           True           False          
# 3             172.20.5.10    60000        198.51.100.25  9999         0           False          True           False          
# 4             172.20.5.10    60000        198.51.100.25  9999         0           False          True           False          464c41475f444154415f
# 5             172.20.5.10    60000        198.51.100.25  9999         0           False          True           False          455846494c5452415445445f
# 6             172.20.5.10    60000        198.51.100.25  9999         0           False          True           False          32303234
# 7             172.20.5.10    60000        198.51.100.25  9999         0           False          True           True           
# 8             198.51.100.25  9999         172.20.5.10    60000        0           False          True           True           
# 9             172.20.5.10    60000        198.51.100.25  9999         0           False          True           False          
```

- All frames are TCP traffic.
- All frames are in the same tcp.stream `0`
- The initial SYN (syn=True & ack=False) from client to server is in frame 1
- The handshake happens in the frames 1..3

```bash
tshark -r task6-tcp-stream-reconstruction.pcap \
-Y 'tcp.stream == 0 && tcp.flags.syn == 1 || tcp.stream == 0 && frame.number <= 3' \
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
-e tcp.len \
| column -t -s $'\t'

# frame.number  ip.src         tcp.srcport  ip.dst         tcp.dstport  tcp.flags.syn  tcp.flags.ack  tcp.len
# 1             172.20.5.10    60000        198.51.100.25  9999         True           False          0
# 2             198.51.100.25  9999         172.20.5.10    60000        True           True           0
# 3             172.20.5.10    60000        198.51.100.25  9999         False          True           0
```

The handshake cleaned:

```bash
client -> server: SYN
server -> client: SYN, ACK
client -> server: ACK
```

## 4. Reconstruct the TCP stream to see the complete data flow.

Reconstructing the TCP stream with `-z follow,tcp,ascii,<tcp.stream>`

```bash
tshark -r task6-tcp-stream-reconstruction.pcap -q -z follow,tcp,ascii,0

===================================================================
Follow: tcp,ascii
Filter: tcp.stream eq 0
Node 0: 172.20.5.10:60000
Node 1: 198.51.100.25:9999
10
FLAG_DATA_
34
[2 bytes missing in capture file].
12
EXFILTRATED_
34
[1 bytes missing in capture file].
4
2024
===================================================================
```

We have 2 bytes / 1 bytes missing in capture file, but concatenating the chunks 
`FLAG_DATA_`, `EXFILTRATED_`, `2024` we're getting `FLAG_DATA_EXFILTRATED_2024` 
which looks pretty complete to me.

Double checking with `tcp.seq`, `tcp.nxtseq`, `tcp.len` why tshark thinks something is missing:

```bash
tshark -r task6-tcp-stream-reconstruction.pcap \
-Y 'tcp.stream == 0 && tcp.payload' \
-T fields \
-E header=y \
-E separator=$'\t' \
-e frame.number \
-e tcp.seq \
-e tcp.nxtseq \
-e tcp.len \
-e tcp.payload \
| column -t -s $'\t'
frame.number  tcp.seq  tcp.nxtseq  tcp.len  tcp.payload
4             1        11          10       464c41475f444154415f
5             13       25          12       455846494c5452415445445f
6             26       30          4        32303234
```

Indeed frame 5 should have tcp.seq 11, so 2 bytes are missing, and frame 6 should have tcp.seq 25.

`¯\_(ツ)_/¯`


## 5. Extract the secret message that was fragmented across multiple data packets.

We already extracted the secret message in the previous step.

Just to make sure we're doing another extraction by simply converting the ASCII hex to characters:

```bash
tshark -r task6-tcp-stream-reconstruction.pcap \
-Y 'tcp.stream == 0 && tcp.payload' \
-T fields \
-e tcp.payload \
| xxd -r -p

# FLAG_DATA_EXFILTRATED_2024
```



## Submission Format

- Submit the complete secret message as a plain text string.
- put `FLAG_DATA_EXFILTRATED_2024` in the textbox
- \ "Submit answer"
- result: `Flag: 3e8e2285742f7e97d8e398c1ba2e68c7`

```bash
echo -n 3e8e2285742f7e97d8e398c1ba2e68c7 > 5-flag.txt

# trust but verify
cat 5-flag.txt
# 3e8e2285742f7e97d8e398c1ba2e68c7
```