#!/bin/bash
util='5 10 15 20 25 30 35 40 45 50 55 60'
for ut in $util
do
  python3 tasksets_generator_pure.py -a 16 -b 16 -d 0 -u $ut &
  sleep 1
  python3 tasksets_generator_pure.py -a 16 -b 4 -d 0 -u $ut &
  sleep 1
  python3 tasksets_generator_pure.py -a 32 -b 4 -d 0 -u $ut &
  sleep 1
done
