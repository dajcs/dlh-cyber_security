#!/bin/bash

# >_ Get a sandbox
#    \ cyber_netsec_0x04
#    \ "Network Information"
#     Local IP: (10.42.82.181 in my case)
# run
# ./7-udp_ping_version.sh 10.42.82.181
sudo nmap -PU53,161,162 -sn $1
