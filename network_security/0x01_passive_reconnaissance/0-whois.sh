#!/bin/bash
whois "$1" | awk -F': ' '/^(Registrant|Admin|Tech) (Name|Organization|Street|City|State\/Province|Postal Code|Country|Phone|Phone Ext|Fax|Fax Ext|Email)/ {gsub(/Ext$/,"Ext:",$1); printf "%s,%s\n", $1, ($2=="")?"":$2}' | head -c -1 > "$1.csv"
