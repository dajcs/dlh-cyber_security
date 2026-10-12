#!/bin/bash
sudo nmap -sM -vv -p 21,22,23,http,443 $1
