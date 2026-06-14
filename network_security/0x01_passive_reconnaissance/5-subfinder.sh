#!/bin/bash
subfinder -d $1 -silent -active -ip | tee $1.txt | cut -d',' -f1
