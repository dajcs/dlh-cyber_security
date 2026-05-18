#!/bin/bash
find "$1" -mtime -1 \(-perm -4000 -o -perm -2000 \) -type f -exec ls -l {} \; 2>/dev/null # -perm /6000
