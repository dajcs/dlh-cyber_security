#!/bin/bash
salt=$(openssl rand -hex 8)
echo -n "$1$salt" | openssl dgst -sha512 > 3_hash.txt
