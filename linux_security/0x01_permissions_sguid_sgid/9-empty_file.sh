#!/bin/bash
find "$1" -type f -empty -exec ls -l {} \;
