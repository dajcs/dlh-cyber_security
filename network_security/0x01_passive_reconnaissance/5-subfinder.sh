#!/bin/bash
subfinder -d $1 -silent -active -ip | cut -d',' -f1,2 | tee $1.txt | cut -d',' -f1
