import copy

from drs import drs
import numpy as np
import random


# Calculate the longest path of a given DAG task
def longest_path_dag_gen(adjacency) -> float:
    cost = np.zeros(adjacency.shape)
    num_nodes = adjacency.shape[0]
    for k in range(num_nodes):
        for i in range(num_nodes):
            if k == 0:
                cost[i, :] = (adjacency.diagonal()[i] + adjacency.diagonal()[:]) * adjacency[i, :]
                cost[np.triu_indices(num_nodes)] = -np.inf
            else:
                cost[i, :] = np.maximum(cost[i, :], cost[i, k] + cost[k, :] - adjacency[k, k])
    return max(max(adjacency.diagonal()), cost.max())


# calculate the utilization of a given task on both types of procesors
def accu_util_ab(task, num_nodes):
    accu_util = [0, 0]
    for i in range(1, num_nodes):
        accu_util[int(task[0][i] - 1)] = accu_util[int(task[0][i] - 1)] + task[i][-1]

    return accu_util


# Generates sets of DAG tasks
# Two type of processors, i.e., type A and type B
# For each type the number of available processors M_A/M_B \in {4, 8, 16}
# For each set of tasks, the total utilization U_s \in [0, M] with step 5%xM, where M=M_A + M_B
# DRS package for allocating utilization for tasks, and nodes.
# Utilization for each task, the utilization U_{\tau} \in (0, U_s),
# in order to be possible to generate task with relatively high utilization.
# Number of nodes $N$ for each task is randomly selected \in [0.5(M_A +M_B), 2M_{max}], e.g., [4, 80]
# Additional 2 are added as common general starting node and ending node with 0 utilization.
# G(N, p) method is used to constructed the structure inside a DAG task,
# $p$ is the possibility that two nodes have precedence constraints \in [0.1, 0.9] or it can be set as [lb, lb+0.4]
# Period $T$ for each task \in [100, 1000]
# Number of tasks for each set can have three modes, denoted by sparse id.

def generate(msets, processor_a, processor_b, pc_prob, utilization, mod, sparse):
    dtype = np.float64
    tasksets = []
    threshold = 0.2
    for i in range(msets):
        taskset = []
        if sparse == 2:
            num_tasks = random.randint(0.25 * (processor_a + processor_b), (processor_a + processor_b))
        if sparse == 1:
            num_tasks = random.randint((processor_a + processor_b), 2 * (processor_a + processor_b))
        if sparse == 0:
            num_tasks = random.randint(0.5 * max(processor_a, processor_b), 2 * max(processor_a, processor_b))
        util_tasks = drs(num_tasks, utilization)
        j = 0
        while j < num_tasks:
            # +2 since one common source node and on common end  node
            num_nodes = random.randint(0.5 * (processor_a + processor_b), 5 * max(processor_a, processor_b)) + 2
            # num_nodes = random.randint(2 * min(processor_a, processor_b), 5 * max(processor_a, processor_b)) + 2
            # num_nodes = random.randint(8, 80)
            period = random.randint(100, 1000)
            util_nodes = drs(num_nodes, util_tasks[j])

            task = np.zeros((num_nodes, num_nodes), dtype=dtype)

            # store the task utilization on task[0][-1]
            task[0][-1] = util_tasks[j]

            # G(n, q) method to generate the precedence constraints
            if mod == 0:
                pc_q = random.uniform(0.1, 0.9)
            else:
                pc_q = random.uniform(pc_prob, pc_prob + 0.4)
            for row in range(1, num_nodes):
                for column in range(1, row):
                    if random.uniform(0, 1) < pc_q:
                        task[row][column] = 1

            # check the connection to general source node
            for row in range(1, num_nodes):
                if sum(task[row]) == 0:
                    task[row][0] = 1

            # check the connection to general end node
            column_sum = np.sum(task, axis=0)
            for column in range(1, num_nodes):
                if column_sum[column] == 0:
                    task[num_nodes - 1][column] = 1

            # write down the execution time for each node
            for n in range(1, num_nodes - 1):
                task[n][n] = period * util_nodes[n - 1]
                # the utilization for each node is stored in the last column of task matrix
                task[n][-1] = util_nodes[n - 1]

            # check the longest path
            if longest_path_dag_gen(task) <= period:

                # store the critical path len(G) in task[3][-2]
                task[3][-2] = longest_path_dag_gen(task)

                # store the period of task in the end node (not the execution time here)
                # please not the execution time for the general source node and end node is 0 for all tasks!
                task[num_nodes - 1][num_nodes - 1] = period

                # store the number of nodes for each task in the source node (speed up the execution)
                task[0][0] = int(num_nodes)

                # append tasks to task set
                taskset.append(task)
                # add the index of # tasks
                j = j + 1

        # append each set to a utilization specified big set
        tasksets.append(taskset)
    return tasksets
