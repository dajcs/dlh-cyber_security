#!/bin/bash
john --format=nt --wordlist=/usr/share/wordlists/rockyou.txt "$1"; john --format=nt --show "$1" | head -n -2 | cut -d: -f2 > 5-password.txt
