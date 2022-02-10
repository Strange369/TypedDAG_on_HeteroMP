#!/bin/bash
fir='0 1 2'
se='0 2'
prob=0.9
mods='1 2'
for fst in $fir
do
  for sed in $se
  do
    for mod in $modes
    do
      python3 sched_han.py -a 16 -b 16 -q $prob -d $mod -f $fst -s $sed &
      sleep 2
      python3 sched_han.py -a 16 -b 4 -q $prob -d $mod -f $fst -s $sed &
      sleep 2
      python3 sched_han.py -a 32 -b 4 -q $prob -d $mod -f $fst -s $sed &
      sleep 2
    done
  done
done