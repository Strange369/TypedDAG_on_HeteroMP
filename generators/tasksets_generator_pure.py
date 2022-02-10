from __future__ import division
import numpy as np
import generator_pure as gen
import os
import math
import sys
import getopt


def main(argv):
    msets = 100
    processor_a = 16
    processor_b = 16
    pc_prob = 0.9
    mod = 3
    util = 5
    try:
        opts, args = getopt.getopt(argv, "hm:a:b:q:d:u:",
                                   ["msets=", "aprocessor", "bprocessor", "pc_prob=", "mod=", "util="])
    except getopt.GetoptError:
        print ('tasksets_generater.py -n <n tasks for each set> -m <m tasksets> -p <num of processors> -r <num of resources> -s <min length of the critical section> -l <max length of the critical section>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('tasksets_generater.py -n <n tasks for each set> -m <m tasksets> -p <num of processors> -r <num of resources> -s <min length of the critical section>-l <max length of the critical section>')
            sys.exit()
        elif opt in ("-m", "--msets"):
            msets = int(arg)
        elif opt in ("-a", "--aprocessor"):
            processor_a = int(arg)
        elif opt in ("-b", "--bprocessor"):
            processor_b = int(arg)
        elif opt in ("-q", "--pc_prob"):
            pc_prob = float(arg)
        elif opt in ("-d", "--mod"):
            mod = int(arg)
        elif opt in ("-u", "--util"):
            util = int(arg)

    print(mod, util)
    for sp in range(0, 1):
        utili = float(util / 100)
        utilization = utili*(processor_a + processor_b)
        tasksets_name = '../experiments/inputs/tasks_pure/tasksets_pure_m' + str(msets) + '_a' + str(processor_a) + '_b' + str(processor_b) + '_u' + str(utili) + '_q' + str(pc_prob)+ '_d' + str(mod)+ '_s' + str(sp)+'.npy'
        tasksets = gen.generate(msets, processor_a, processor_b, pc_prob, utilization, mod, sp)
        np.save(tasksets_name, tasksets)


if __name__ == "__main__":
    main(sys.argv[1:])
