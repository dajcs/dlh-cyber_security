#!/bin/bash
head -c "$1" /dev/urandom | base64 | tr -d '\n' | head -c "$1"; echo