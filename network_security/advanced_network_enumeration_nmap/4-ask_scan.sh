#!/bin/bash
sudo nmap -sA --reason --host-timeout 1000ms -p $2 $1
