#!/bin/bash
fir='0 1 2'
se='0 2'
prob=0.9
for fst in $fir
do
  for sed in $se
  do
    for pob in $prob
    do
      python3 sched_improved_new.py -a 16 -b 16 -q $pob -f $fst -s $sed &
      sleep 2
      python3 sched_improved_new.py -a 16 -b 4 -q $pob -f $fst -s $sed &
      sleep 2
      python3 sched_improved_new.py -a 32 -b 4 -q $pob -f $fst -s $sed &
      sleep 2
    done
  done
done