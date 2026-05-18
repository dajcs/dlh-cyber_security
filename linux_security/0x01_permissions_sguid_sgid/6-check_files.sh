#!/bin/bash
find "$1" -mtime -1 -perm /6000 -type f -exec ls -l {} \; 2>/dev/null
