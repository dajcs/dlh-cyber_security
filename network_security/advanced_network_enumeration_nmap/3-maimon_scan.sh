#!/bin/bash
sudo nmap -sM -vv -p 21,22,23,80,443 $1
