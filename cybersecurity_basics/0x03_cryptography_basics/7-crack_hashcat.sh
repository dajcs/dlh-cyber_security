#!/bin/bash
hashcat -m 0 -a 0 "$1" /usr/share/wordlists/rockyou.txt; hashcat -m 0 -a 0 hash7.txt /usr/share/wordlists/rockyou.txt --show | cut -d ':' -f 2 > 7-password.txt
