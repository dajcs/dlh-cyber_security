#!/bin/bash
while read ip; do
    echo "=== $ip ==="
    curl -s "https://internetdb.shodan.io/$ip" | jq 
    echo ""
done < $1
