#!/bin/bash
curl -X -H "Host: $1" -d "$3" "$2"
