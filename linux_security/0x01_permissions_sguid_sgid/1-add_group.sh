#!/bin/bash
addgroup "$1"
chown :"$1" "$2"  # chown [option] [owner][:[group]] file
chmod g+rx "$2"
