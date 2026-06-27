## 1. Download the PCAP file `task2-http-analysis.pcap` associated with this task.

click on [pcaps/task2-http-analysis.pcap](https://web-80-18-51.cod-eu-west-3.hbtn.io/api/assets/pcaps/task2-http-analysis.pcap)

## 2. Open it in Wireshark, **tshark**, or tcpdump.

```bash
tshark -r task2-http-analysis.pcap 
#     1   0.000000    10.0.0.50 → 203.0.113.10 HTTP 107 GET /login HTTP/1.1 
#     2   0.000284    10.0.0.50 → 203.0.113.10 TCP 156 [TCP Retransmission] 45678 → 80 [PSH, ACK] Seq=1 Ack=1 Win=8192 Len=116
#     3   0.000516 203.0.113.10 → 10.0.0.50    HTTP 78 HTTP/1.1 200 OK 
```

## 3. Filter for HTTP traffic (port 80).

```bash
# filter for HTTP
tshark -r task2-http-analysis.pcap -Y http
#    1   0.000000    10.0.0.50 → 203.0.113.10 HTTP 107 GET /login HTTP/1.1 
#    3   0.000516 203.0.113.10 → 10.0.0.50    HTTP 78 HTTP/1.1 200 OK 
```

## 4. Inspect the HTTP traffic and locate the Authorization header in the POST packet.

Now we're getting somewhat lost.  <BR>
On the previous HTTP filtering we had a HTTP GET and a HTTP OK. <BR>
There is no sign of HTTP POST... unless it is hidden somehow in that 2nd [TCP Retransmission] frame.

On Wireshark GUI the 2nd frame `tcp.segment_data` shows:

```
0000   45 00 00 9c 00 01 00 00 40 06 34 1f 0a 00 00 32   E.......@.4....2
0010   cb 00 71 0a b2 6e 00 50 00 00 00 00 00 00 00 00   ..q..n.P........
0020   50 18 20 00 0c de 00 00 50 4f 53 54 20 2f 61 70   P. .....POST /ap
0030   69 2f 61 75 74 68 20 48 54 54 50 2f 31 2e 31 0d   i/auth HTTP/1.1.
0040   0a 48 6f 73 74 3a 20 65 78 61 6d 70 6c 65 2e 63   .Host: example.c
0050   6f 6d 0d 0a 41 75 74 68 6f 72 69 7a 61 74 69 6f   om..Authorizatio
0060   6e 3a 20 42 61 73 69 63 20 59 57 52 74 61 57 34   n: Basic YWRtaW4
0070   36 55 32 56 6a 64 58 4a 6c 55 47 46 7a 63 7a 45   6U2VjdXJlUGFzczE
0080   79 4d 79 45 3d 0d 0a 43 6f 6e 74 65 6e 74 2d 4c   yMyE=..Content-L
0090   65 6e 67 74 68 3a 20 30 0d 0a 0d 0a               ength: 0....
```

Let's try to have a deeper look inside this TCP packet with `tshark` examining the `tcp.payload`

```bash
# check tcp.payload
tshark -r task2-http-analysis.pcap -Y 'tcp.dstport == 80 && tcp.payload' \
-T fields -e tcp.payload  
# 474554202f6c6f67696e20485454502f312e310d0a486f73743a206578616d706c652e636f6d0d0a557365722d4167656e743a204d6f7a696c6c612f352e300d0a0d0a
# 504f5354202f6170692f6175746820485454502f312e310d0a486f73743a206578616d706c652e636f6d0d0a417574686f72697a6174696f6e3a2042617369632059575274615734365532566a64584a6c5547467a637a45794d79453d0d0a436f6e74656e742d4c656e6774683a20300d0a0d0a
```
We're getting here the hex dump of the TCP payload from frames 1 and 2.<BR>
Let's convert it back to the original characters:

```bash
tshark -r task2-http-analysis.pcap -Y 'tcp.dstport == 80 && tcp.payload' \
-T fields -e tcp.payload \
| xxd -r -p

# GET /login HTTP/1.1
# Host: example.com
# User-Agent: Mozilla/5.0

# POST /api/auth HTTP/1.1
# Host: example.com
# Authorization: Basic YWRtaW46U2VjdXJlUGFzczEyMyE=
# Content-Length: 0
```
Here we have the first HTTP GET request, and a HTTP POST request hidden inside a TCP Retransmission.<BR>
We're interested mainly in the `Authorization` header:

```bash
tshark -r task2-http-analysis.pcap -Y 'tcp.dstport == 80 && tcp.payload' \
-T fields -e tcp.payload \
| xxd -r -p \
| grep -i '^Authorization:'

# Authorization: Basic YWRtaW46U2VjdXJlUGFzczEyMyE=
```

## 5. Extract and decode the Base64-encoded credentials included in the request.

We're going to Base64-decode the Authorization header:

```bash
tshark -r task2-http-analysis.pcap -Y 'tcp.dstport == 80 && tcp.payload' \
-T fields -e tcp.payload \
| xxd -r -p \
| grep -i '^Authorization:' \
| awk '{print $3}' \
| base64 -d

# admin:SecurePass123!base64: invalid input
```

Almost there.<BR> 
The problem is that the webserver transmission ends with `\r\n` and `awk` removes only the `\n` so we are feeding for base64 decoder the string `YWRtaW46U2VjdXJlUGFzczEyMyE=\r` instead of `YWRtaW46U2VjdXJlUGFzczEyMyE=`.<BR>
Let's fix this by deleting the `\r`:
```bash
tshark -r task2-http-analysis.pcap -Y 'tcp.dstport == 80 && tcp.payload' \
-T fields -e tcp.payload \
| xxd -r -p \
| tr -d '\r' \
| grep -i '^Authorization:' \
| awk '{print $3}' \
| base64 -d

# admin:SecurePass123!
```

## 6. Submission Format

- Submit the credentials in the format: `username:password`
- put `admin:SecurePass123!` in the textbox
- \ "Submit answer"
- result: `Flag: 7b99711ff6bf209949f127f2726ea2f0`

```bash
echo -n 7b99711ff6bf209949f127f2726ea2f0 > 1-flag.txt

# trust but verify
cat 1-flag.txt
# 7b99711ff6bf209949f127f2726ea2f0
```