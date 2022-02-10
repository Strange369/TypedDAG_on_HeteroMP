import numpy as np
import sys
sys.path.append('../')
from algorithms import sched_fed
import sys
import getopt

def main(argv):
    msets = 100
    processor_a = 16
    processor_b = 16
    pc_prob = 0.4
    mod = 1
    imod = 1
    rho_all = [1/7.25, 0.3, 0.5]
    rho_id = 0
    mod_1 = 0
    mod_2 = 0
    mod_3 = 0
    try:
        opts, args = getopt.getopt(argv, "hm:a:b:q:d:r:f:s:o:",
                                   ["msets=", "aprocessor", "bprocessor", "pc_prob=", "mod", "rho=", "mod_1", "mod_2", "mod_3"])
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
        elif opt in ("-r", "--rho"):
            rho_id = int(arg)
        elif opt in ("-f", "--mod_1"):
            mod_1 = int(arg)
        elif opt in ("-s", "--mod_2"):
            mod_2 = int(arg)
        elif opt in ("-o", "--mod_3"):
            mod_3 = int(arg)


    rho = rho_all[rho_id]
    for sparse in range(0, 2):
        accept_all = []
        for i in range(5, 65, 5):
            utili = float(i / 100)
            data_name = 'inputs/tasks_new/tasksets_m' + str(msets) + '_a' + str(
            processor_a) + '_b' + str(processor_b) + '_u' + str(utili) + '_q' + str(pc_prob) + '_f' + str(mod_1) + '_s' + str(mod_2) + '_m' + str(mod_3) + '_s' + str(sparse)+'.npy'
            data = np.load(data_name, allow_pickle=True)
            accept = sched_fed.schedulability_greedy_federated(data, msets, processor_a, processor_b, rho)
            accept_all.append(accept)
            print('Accepted: ', accept_all)
        results_name = 'outputs/results/results_greedy_m' + str(msets) + '_a' + str(processor_a) + '_b' + str(processor_b) + '_q' + str(pc_prob) + '_d' + str(mod) + '_r' + str(rho_id) + '_f' + str(mod_1) + '_s' + str(mod_2) + '_m' + str(mod_3) + '_s' + str(sparse)+'.npy'
        np.save(results_name, accept_all)


if __name__ == "__main__":
    main(sys.argv[1:])
