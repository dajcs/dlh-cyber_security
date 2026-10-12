#!/bin/bash
sudo nmap -sA --reason --max-rtt-timeout 1000ms -p $2 $1
