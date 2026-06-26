#!/bin/bash

# >_ Get a sandbox
#    \ cyber_netsec_0x04
#    \ "Network Information"
#     Local IP: (10.42.82.181 in my case)
# >_ Get a Ubuntu sandbox
#     \ ubuntu_2204
# run
# ./7-udp_ping_version.sh 10.42.82.181
sudo nmap -sU -sV -p200-300 $1
