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


# Generate the type for each node by following different mode.
# mod_1: P_\ell controls the skewness of the skewed tasks
# e.g., 10% nodes for the task is assigned on A core, and others on B core (heavy^b task)
# mod_2: the percentage of heavy^a or heavy^b tasks, e.g., 0%, 75%m, 50%, 25%, and 100%
# mod_3: if allow a task only require one type of processor:
# i.e., 0: not allowed; 1: allowed, the percentage can be defined by mod_2 (if needed)

# def generate(nsets, msets, processors, num_resources, utilization, critical_min, critical_max, mod):
def generate(msets, task_sets_org, processor_a, processor_b, mod_1, mod_2, mod_3):
    tasks_org = copy.deepcopy(task_sets_org)
    threshods = [0.1, 0.05, 0.01]
    percentages = [1, 0.75, 0.5, 0.25, 0]

    threshod_temp = threshods[mod_1]
    percent = percentages[mod_2]

    task_a = copy.deepcopy(task_sets_org)
    task_b = copy.deepcopy(task_sets_org)

    for i in range(msets):
        # number of tasks
        for j in range(len(tasks_org[i])):
            num_nodes = int(tasks_org[i][j][0][0])
            # normal situation, each task require both types of processors
            if mod_3 == 0:
                # heavy^a or heavy^b task
                if random.uniform(0, 1) < percent:
                    # decide if it is heavy^a or heavy^b task
                    if random.uniform(0, 1) < 0.5:
                        # heavy^b
                        threshold = threshod_temp
                    else:
                        threshold = 1 - threshod_temp
                else:
                    # the threshold follows the M_a/(M_a + M_b)
                    threshold = processor_a/(processor_a + processor_b)

            # only allow heavy A when #A >> #B
            elif mod_3 == 1:
                if random.uniform(0, 1) < percent:
                    threshold = 1 - threshod_temp
                else:
                    # the threshold follows the M_a/(M_a + M_b)
                    threshold = processor_a/(processor_a + processor_b)
            # since we assume # processor A > # processor B
            # we only allow task can only require processor A here
            else:
                # Only processor A
                if random.uniform(0, 1) < percent:
                    # all the nodes are assigned on processor A
                    threshold = 1
                else:
                    # follows the threshold percentage
                    threshold = 1 - threshod_temp
            # define the type for each node
            for node in range(1, num_nodes-1):
                if random.uniform(0, 1) < threshold:
                    tasks_org[i][j][0][node] = 1
                    task_a[i][j][0][node] = 1
                    task_b[i][j][0][node] = 1
                else:
                    tasks_org[i][j][0][node] = 2
                    task_a[i][j][0][node] = 2
                    task_b[i][j][0][node] = 2

            # In the following some additional information is calculated for future usage
            # calculate the L_i^a and L_i^b
            task_a[i][j][0][0] = 0
            task_b[i][j][0][0] = 0

            task_a[i][j][-1][-1] = 0
            task_b[i][j][-1][-1] = 0

            for nd in range(1, num_nodes-1):
                if int(tasks_org[i][j][0][nd]) == 1:
                    task_b[i][j][nd][nd] = 0
                else:
                    task_a[i][j][nd][nd] = 0
            L_a = longest_path_dag_gen(task_a[i][j])
            L_b = longest_path_dag_gen(task_b[i][j])

            tasks_org[i][j][2][-3] = L_a
            period = tasks_org[i][j][-1][-1]
            if tasks_org[i][j][2][-3] == period/3 or tasks_org[i][j][2][-3] == period/2:
                tasks_org[i][j][2][-3] = tasks_org[i][j][2][-3] + 10**(-5)

            tasks_org[i][j][2][-2] = L_b
            if tasks_org[i][j][2][-2] == period/3 or tasks_org[i][j][2][-2] == period/2:
                tasks_org[i][j][2][-2] = tasks_org[i][j][2][-2] + 10**(-5)

            acc_util_ab = [0, 0]
            for nd in range (1, num_nodes-1):
                acc_util_ab[int(tasks_org[i][j][0][nd] - 1)] = acc_util_ab[int(tasks_org[i][j][0][nd] - 1)] + tasks_org[i][j][nd][-1]

            tasks_org[i][j][1][-3] = acc_util_ab[0]
            tasks_org[i][j][1][-2] = acc_util_ab[1]

    return tasks_org
