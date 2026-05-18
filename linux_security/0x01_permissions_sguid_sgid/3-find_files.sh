#!/bin/bash
find "$1" -perm /6000 -type f -exec ls {} \; 2>/dev/null
