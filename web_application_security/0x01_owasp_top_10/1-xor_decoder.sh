#!/bin/bash

# Bash strict mode:
#
# -e:
#   Exit when a command fails with a non-zero exit status.
#
# -u:
#   Treat an unset variable as an error.
#
# -o pipefail:
#   Make a pipeline fail when any command in it fails, rather than only
#   checking the exit status of the final command.
#
# This catches many silent scripting errors. It is useful, but it is not
# a complete error-handling system.
set -euo pipefail


# The script expects exactly one positional argument.
#
# Example:
#   ./1-xor_decoder.sh '{xor}KzosKw=='
#
# $# contains the number of positional arguments.
if [[ $# -ne 1 ]]; then
    printf 'Usage: %s "{xor}<base64_data>"\n' "$0" >&2
    exit 1
fi


# $1 contains the supplied WebSphere value.
input=$1


# WebSphere XOR-encoded values normally start with:
#
#   {xor}
#
# This prefix identifies the encoding algorithm. It is metadata and is
# not part of the actual Base64 payload.
#
# "${input#\{xor\}}" removes "{xor}" from the beginning of the string.
# The backslashes prevent Bash from interpreting the braces specially.
encoded="${input#\{xor\}}"
# ${variable#pattern} removes the shortest match of pattern from the beginning of the string.
# ${variable%pattern} removes the shortest match of pattern from the end of the string.
# ${variable##pattern} removes the longest match of pattern from the beginning of the string.
# ${variable%%pattern} removes the longest match of pattern from the end of the string.

# Check that the input actually had the expected prefix.
#
# Without this check, the script would try to Base64-decode any supplied
# string, even when it was not marked as WebSphere XOR data.
if [[ "$encoded" == "$input" ]]; then
    printf 'Error: input must begin with "{xor}"\n' >&2
    exit 1
fi


# Decode the Base64 data.
#
# For the example:
#
#   KzosKw==
#
# Base64 decoding produces the bytes:
#
#   2b 3a 2c 2b
#
# These bytes are not yet plaintext. Each byte still needs to be XORed
# with WebSphere's fixed XOR key, 0x5f.
#
# We convert the binary output to hexadecimal using xxd because Bash
# variables cannot safely store arbitrary binary data, especially null
# bytes.
hex_data="$(
    printf '%s' "$encoded" |
        base64 --decode 2>/dev/null |
        xxd -p |
        tr -d '\n'
)" || {
    printf 'Error: invalid Base64 data\n' >&2
    exit 1
}


# Verify that Base64 decoding produced complete bytes.
#
# Each byte requires exactly two hexadecimal characters. An odd-length
# hexadecimal string would indicate malformed data.
if (( ${#hex_data} % 2 != 0 )); then
    printf 'Error: decoded data is malformed\n' >&2
    exit 1
fi


# Process the hexadecimal string two characters at a time.
#
# Example:
#
#   "2b" becomes the numeric byte 0x2b
#
# XOR it with 0x5f:
#
#   0x2b XOR 0x5f = 0x74
#
# 0x74 is the ASCII value for "t".
for ((i = 0; i < ${#hex_data}; i += 2)); do
    # Extract one hexadecimal byte, such as "2b".
    hex_byte="${hex_data:i:2}"

    # Convert the hexadecimal byte to an integer and XOR it with 0x5f.
    decoded_byte=$((16#$hex_byte ^ 0x5f))

    # printf's \ooo notation expects an octal value.
    #
    # First convert the byte to a three-digit octal escape, then print
    # the character represented by that escape.
    printf "\\$(printf '%03o' "$decoded_byte")"
done


# Print a final newline so the shell prompt appears on the next line.
printf '\n'