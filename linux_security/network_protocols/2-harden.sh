#!/bin/bash
find . -type d -perm -0002 -print 2>/dev/null | while read -r dir; do
    echo "$dir"
    chmod o-w "$dir"
done
