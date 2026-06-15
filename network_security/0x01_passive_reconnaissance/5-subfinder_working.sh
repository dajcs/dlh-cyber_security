#!/bin/bash
subfinder -silent -d $1 -active -ip | cut -d',' -f1,2 | tee $1.txt | cut -d',' -f1
