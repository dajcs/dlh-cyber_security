#!/bin/bash
find "$1" -size 0 -exec ls -l {} \;
