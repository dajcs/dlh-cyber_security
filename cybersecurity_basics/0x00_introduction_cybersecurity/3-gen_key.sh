#!/bin/bash
ssh-keygen -t rsa -b 4096 -f "$1" -N ""
# -t rsa → RSA key type
# -b 4096 → 4096-bit key size
# -f "$1" → output filename (your argument, e.g. new_key)
# -N "" → empty passphrase (non-interactive, required for scripts)