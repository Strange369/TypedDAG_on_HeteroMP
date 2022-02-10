#!/bin/bash
util='5 10 15 20 25 30 35 40 45 50 55 60'
f1='0 1 2'
s1='0 2'
for ut in $util
do
  for f in $f1
  do
    for s in $s1
    do
      python3 tasksets_convertor.py -a 16 -b 16 -q 0.9 -d 0 -u $ut -f $f -s $s -o 0 &
      sleep 1
      python3 tasksets_convertor.py -a 16 -b 4 -q 0.9 -d 0 -u $ut -f $f -s $s -o 0 &
      sleep 1
      python3 tasksets_convertor.py -a 32 -b 4 -q 0.9 -d 0 -u $ut -f $f -s $s -o 0 &
      sleep 1
    done
  done
done
