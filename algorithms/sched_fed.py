import numpy as np
import math
import copy
from collections import deque
import time
import collections
from ortools.sat.python import cp_model
from algorithms import heavy_cp

# Calculate the longest path of a given DAG task
def longest_path_dag(adjacency) -> float:
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


# HGSH method to schedule a heavy task on $pro_a$ type A processors and $pro_b$ processors
# Return the feasibility: 1-schedulable (response time <= period/deadline) 0-otherwise
def hgsh(task, processor):
    # copy the original DAG task
    task_org = copy.deepcopy(task)
    # mantain another copy that can be modified accordingly
    task_scaled = copy.deepcopy(task)
    # store the processor infomation
    # index 0: the number of processor A
    # index 1: the number of processor B
    processors = copy.deepcopy(processor)

    if processors[0] == 0:
        vol_sum = (task_org[1][-2]/processors[1]) * task_org[-1][-1]
    elif processors[1] == 0:
        vol_sum = (task_org[1][-3] / processors[0]) * task_org[-1][-1]
    else:
        vol_sum = (task_org[1][-3] / processors[0] + task_org[1][-2] / processors[1]) * task_org[-1][-1]

    # delete the additional information
    task_scaled[0][0] = 0
    task_scaled[-1][-1] = 0
    for i in range(1, int(task_org[0][0] - 1)):
        task_scaled[i][i] = task_scaled[i][i] * (1 - (1 / (processors[int(task_org[0][i]) - 1])))

    response_time = vol_sum + longest_path_dag(task_scaled)

    return response_time


def emu_assign(task_org, available_a, available_b, penalty_a, penalty_b):
    # upper bound for processor A and B
    task = copy.deepcopy(task_org)

    if math.ceil(task[1][-3]) < available_a or math.ceil(task[1][-2]) < available_b:
        return False

    ub_a = int(available_a + 1)
    ub_b = int(available_b + 1)

    current_best = [0, 0]
    penalty = 3

    for i in range(math.ceil(task[1][-3]), ub_a):
        for j in range(math.ceil(task[1][-2]), ub_b):
            penalty_temp = i * penalty_a + j * penalty_b
            if (hgsh(task, [i, j]) <= task[-1][-1]) and (penalty_temp < penalty):
                penalty = penalty_temp
                current_best[0] = i
                current_best[1] = j
                break
    if current_best[0] != 0 and current_best[1] != 0:
        return current_best
    else:
        return False

def greedy_assign(task_org, available_a, available_b, penalty_a, penalty_b):
    task = copy.deepcopy(task_org)
    current_a = math.ceil(task[1][-3])
    current_b = math.ceil(task[1][-2])

    if current_a < available_a or current_b < available_b:
        return False

    response_time = hgsh(task, [current_a, current_b])
    while response_time > task[-1][-1] and current_a <= available_a and current_b <= available_b:
        temp_rt_a = hgsh(task, [(current_a + 1), current_b])
        temp_rt_b = hgsh(task, [current_a, (current_b + 1)])

        if (response_time - temp_rt_a - penalty_a) > (response_time - temp_rt_b - penalty_b):
            response_time = temp_rt_a
            current_a = current_a + 1
        else:
            response_time = temp_rt_b
            current_b = current_b + 1

    if response_time < task[-1][-1]:
        return [current_a, current_b]
    else:
        return False


# calculate the ceiling for utilization on processor A and B
def lb_processor(task):
    util = [0, 0]
    for i in range(1, int(task[0][0] - 1)):
        util[int(task[0][i]) - 1] = util[int(task[0][i]) - 1] + task[i][int(task[0][0] - 1)]

    # lower bound for processor A and B
    util[0] = int(math.ceil(util[0]))
    util[1] = int(math.ceil(util[1]))

    return util


# calculate the volume of a DAG task (sum of the WCET of all nodes)
def vol_dag(task):
    # vol for (sum, A, B)
    return [task[0][-1]*task[-1][-1], task[1][-3]*task[-1][-1], task[1][-2]*task[-1][-1]]


# schedule light tasks on processor A and B
def sched_light(light_tsks, processor_a, processor_b):
    light_tasks = copy.deepcopy(light_tsks)
    h_priority = []
    for i in range(0, len(light_tasks)):
        if len(h_priority) > 0:
            # initial response time equals to the volume of the DAG task
            x_k = vol_dag(light_tasks[i])[0]
            R_pre = vol_dag(light_tasks[i])[0]
            R_k = 0
            while (R_k != R_pre) and (R_k <= light_tasks[i][-1][-1]):

                w_a = 0
                w_b = 0
                for j in range(0, len(h_priority)):
                    w_a = w_a + (vol_dag(h_priority[j])[1] * math.ceil(R_pre / h_priority[j][-1][-1]))
                    w_b = w_b + (vol_dag(h_priority[j])[2] * math.ceil(R_pre / h_priority[j][-1][-1]))
                R_k = x_k + math.ceil(w_a / processor_a + w_b / processor_b)
                if R_k == R_pre:
                    h_priority.append(light_tasks[i])
                    break
                else:
                    R_pre = R_k
                if R_k > light_tasks[i][-1][-1]:
                    return 0
        else:
            # the task with highest priority
            h_priority.append(light_tasks[i])

    # if all light tasks can be scheduled
    return 1


# suspension time processor a
def suspension_a(task, processor_b):
    s_a = task[2][-2] + ((task[1][-2] * task[-1][-1] - task[2][-2]) / processor_b)
    return s_a


# suspension time processor b
def suspension_b(task, processor_a):
    s_b = task[2][-3] + ((task[1][-3] * task[-1][-1] - task[2][-3]) / processor_a)
    return s_b


# the sum of ceiling for task with higher priorities: heavy_a
# task_hp = [[task, R_i]...]
def sum_hp_a(time_t, tasks_hp):
    sum = 0
    for i in range(len(tasks_hp)):
        sum = sum + math.ceil((((time_t + tasks_hp[i][1]) / tasks_hp[i][0][-1][-1]) - tasks_hp[i][0][1][-2])) * tasks_hp[i][0][1][-2] * tasks_hp[i][0][-1][-1]
    return sum


# the sum of ceiling for task with higher priorities: heavy_b
# task_hp = [[task, R_i]...]
def sum_hp_b(time_t, tasks_hp):
    sum = 0
    for i in range(len(tasks_hp)):
        sum = sum + math.ceil((((time_t + tasks_hp[i][1]) / tasks_hp[i][0][-1][-1]) - tasks_hp[i][0][1][-3])) * tasks_hp[i][0][1][-3] * tasks_hp[i][0][-1][-1]
    return sum


# schedulability heavy a on 1 B core
def sched_heavy_a(task_new, tasks_hp, processor_a):
    if processor_a <= 0:
        return False
    constant_cs = task_new[1][-2] * task_new[-1][-1] + suspension_b(task_new, processor_a)
    # the first task on processor A
    if len(tasks_hp) == 0:
        return constant_cs

    time_t = 10 ** (-5)
    response_time = 0
    start_time = time.time()
    while time_t <= task_new[-1][-1] and time.time() - start_time < 1200:
        response_time = constant_cs + sum_hp_a(time_t, tasks_hp)

        if response_time <= time_t:
            return response_time
        else:
            time_t = response_time
    return False


# schedulability heavy b on 1 A core
def sched_heavy_b(task_new, tasks_hp, processor_b):
    if processor_b <= 0:
        return False
    constant_cs = task_new[1][-3] * task_new[-1][-1] + suspension_a(task_new, processor_b)
    # the first task on processor A
    if len(tasks_hp) == 0:
        return constant_cs

    time_t = 10 ** (-5)
    response_time = 0
    start_time = time.time()
    while time_t <= task_new[-1][-1] and time.time() - start_time < 1200:
        response_time = constant_cs + sum_hp_b(time_t, tasks_hp)

        if response_time <= time_t:
            return response_time
        else:
            time_t = response_time
    return False


# schedule a light task on one a core and one b core
def sched_light_fix(light_task, task_hp_a, task_hp_b):
    wcet_new = light_task[0][-1] * light_task[-1][-1]
    # if both a and b processor is empty
    if len(task_hp_a) == 0 and len(task_hp_b) == 0:
        return wcet_new

    time_t = 10 ** (-5)
    response_time = 0
    start_time = time.time()
    while time_t <= light_task[-1][-1] and time.time() - start_time < 1200:
        response_time = wcet_new + sum_hp_a(time_t, task_hp_b) + sum_hp_b(time_t, task_hp_a)

        if response_time <= time_t:
            return response_time
        else:
            time_t = response_time
    return False

# calculate the number of processor A if only processor A is required
def only_processor_a(task_org, available_a):
    task = copy.deepcopy(task_org)
    current_available_a = copy.deepcopy(available_a)
    for i in range(1, current_available_a+1):
        if hgsh(task, [i, 0]) <= task[-1][-1]:
            return int(i)
    return 0

# calculate the number of processor B if only processor B is required
def only_processor_b(task_org, available_b):
    task = copy.deepcopy(task_org)
    current_available_b = copy.deepcopy(available_b)
    for i in range(1, current_available_b+1):
        if hgsh(task, [0, i]) <= task[-1][-1]:
            return int(i)
    return 0


# federated scheduling according to Meiling Han's paper
# with different processor assignment method
# mod 0: emu assignment
# mod 1: greedy method
def sched_han(taskst, available_a, available_b, mod):
    taskset = copy.deepcopy(taskst)
    current_available_a = copy.deepcopy(available_a)
    current_available_b = copy.deepcopy(available_b)

    penalty_a = 1 / current_available_a
    penalty_b = 1 / current_available_b

    light_tasks = []
    for i in range(0, len(taskset)):
        # check if the task only require one type of processor
        # only require processor A:
        # ("utilization A:", )
        if taskset[i][1][-2] == 0:
            # print("partitioned", taskset[i][0])
            used_a = only_processor_a(taskset[i], current_available_a)
            if used_a > 0:
                current_available_a = current_available_a - used_a
            else:
                return 0

        # only require processor B:
        if taskset[i][1][-3] == 0:
            used_b = only_processor_b(taskset[i], current_available_b)
            if used_b > 0:
                current_available_b = current_available_b - used_b
            else:
                return 0

        # try to divide the tasks into heavy and light
        # heavy task: density > 1 -> volume > period
        if taskset[i][0][-1] > 1:

            # different processor assignment methods
            if mod == 1:
                assigned = emu_assign(taskset[i], current_available_a, current_available_b, penalty_a, penalty_b)
            else:
                assigned = greedy_assign(taskset[i], current_available_a, current_available_b, penalty_a, penalty_b)

            # update the current available processors
            if assigned:
                current_available_a = current_available_a - assigned[0]
                current_available_b = current_available_b - assigned[1]
            else:
                return 0

            # no sufficient processors for heavy tasks
            if current_available_a < 0 or current_available_b < 0:
                return 0

        # store all light tasks here
        else:
            light_tasks.append(taskset[i])

    # HERE: Do we need to consider how to allocate light tasks on the available processors?
    # for example, try to share as much as possible like the improved version.

    # if there is only one light task, check it directly.
    if len(light_tasks) == 0:
        return 1
    if current_available_a == 0 or current_available_b == 0:
        return 0
    if (len(light_tasks) == 1) and current_available_a > 0 and current_available_b > 0:
        # schedulable by default
        return 1
    else:
        # sort light tasks
        light_tasks.sort(key=lambda x: x[-1][-1])
        # schedula light tasks using our method
        partition_a = []
        partition_b = []
        for a in range(current_available_a):
            partition_a.append(deque())
        for b in range(current_available_b):
            partition_b.append(deque())
        for l in range(len(light_tasks)):
            new_partitioned_ab = sched_share_light(light_tasks[l], [partition_a, partition_b])
            if new_partitioned_ab:
                partition_a = new_partitioned_ab[0]
                partition_b = new_partitioned_ab[1]
            else:
                return 0

    return 1


# constraint programming for simulate the execution of a heavy task using Google OR-TOOLS
# in the independent file heavy_cp.py


# check the total utilization of tass on A/B processors
def total_util_ab(tasks):
    util_ab = [0, 0]
    for i in range(len(tasks)):
        util_ab[0] = util_ab[0] + tasks[i][1][-3]
        util_ab[1] = util_ab[1] + tasks[i][1][-2]
    return util_ab


# the processors A/B for heavy_ab task
def processors_heavy_ab(heavy_ab):
    p_ab = []
    p_a = math.ceil((heavy_ab[1][-3] * heavy_ab[-1][-1] - heavy_ab[2][-3]) / (heavy_ab[-1][-1] / 2 - heavy_ab[2][-3]))
    p_ab.append(p_a)
    p_b = math.ceil((heavy_ab[1][-2] * heavy_ab[-1][-1] - heavy_ab[2][-2]) / (heavy_ab[-1][-1] / 2 - heavy_ab[2][-2]))
    p_ab.append(p_b)

    return p_ab


# the processor A for heavy_a task
def processors_heavy_a(heavy_a):
    p_a = math.ceil((heavy_a[1][-3] * heavy_a[-1][-1] - heavy_a[2][-3]) / (heavy_a[-1][-1] / 3 - heavy_a[2][-3]))
    return p_a


# the processor B for heavy_b task
def processors_heavy_b(heavy_b):
    p_a = math.ceil((heavy_b[1][-2] * heavy_b[-1][-1] - heavy_b[2][-2]) / (heavy_b[-1][-1] / 3 - heavy_b[2][-2]))
    return p_a


# schedule heavy_a on B core along with other tasks
def sched_share_heavy_a(heavy_a, partitioned_b_org, processor_a):
    partitioned_b = copy.deepcopy(partitioned_b_org)
    for i in range(len(partitioned_b)):
        response = sched_heavy_a(heavy_a, partitioned_b[i], processor_a)
        if response:
            new_partition = []
            new_partition.append(heavy_a)
            new_partition.append(response)
            partitioned_b[i].append(new_partition)
            return partitioned_b

    return False


# schedule heavy_b on A core along with other tasks
def sched_share_heavy_b(heavy_b, partitioned_a_org, processor_b):
    partitioned_a = copy.deepcopy(partitioned_a_org)
    for i in range(len(partitioned_a)):
        response = sched_heavy_b(heavy_b, partitioned_a[i], processor_b)
        if response:
            new_partition = []
            new_partition.append(heavy_b)
            new_partition.append(response)
            partitioned_a[i].append(new_partition)
            return partitioned_a

    return False


# schedule light task on A/B core along with other tasks
def sched_share_light(light_ab, partitioned_ab_org):
    partitioned_ab = copy.deepcopy(partitioned_ab_org)

    for i in range(len(partitioned_ab[0])):
        for j in range(len(partitioned_ab[1])):
            response = sched_light_fix(light_ab, partitioned_ab[0][i], partitioned_ab[1][j])
            if response:
                new_partition_a = []
                new_partition_a.append(light_ab)
                new_partition_a.append(response)
                new_partition_b = []
                new_partition_b.append(light_ab)
                new_partition_b.append(response)

                partitioned_ab[0][i].append(new_partition_a)
                partitioned_ab[1][j].append(new_partition_b)

                return partitioned_ab

    return False


# Greedy federated partitioned algorithm
def greedy_federated_p(task_set, rho, processor_a, processor_b):
    tasks = copy.deepcopy(task_set)
    tasks_share = deque()
    available_a = processor_a
    available_b = processor_b
    # used A/B processors
    used_a = 0
    used_b = 0

    # clarify tasks into four groups
    for i in range(len(tasks)):

        # check if the task only require one type of processor
        # only require processor A:
        if tasks[i][1][-2] == 0:
            used_a = only_processor_a(tasks[i], available_a)
            if used_a > 0:
                available_a = available_a - used_a
            else:
                return 0

        # only require processor B:
        if tasks[i][1][-3] == 0:
            used_b = only_processor_b(tasks[i], available_b)
            if used_b > 0:
                available_b = available_b - used_b
            else:
                return 0

        if tasks[i][1][-3] > rho:
            if tasks[i][1][-2] > rho:
                # heavy_ab
                used_ab = processors_heavy_ab(tasks[i])
                if used_ab[0] < 0 or used_ab[1] < 0:
                    return 0
                used_a = used_a + used_ab[0]
                used_b = used_b + used_ab[1]
            else:
                # heavy_a
                new_used_a = processors_heavy_a(tasks[i])
                if new_used_a < 0:
                    return 0
                else:
                    used_a = used_a + new_used_a
                tsk_temp = []
                tsk_temp.append(tasks[i])
                tsk_temp.append(1)
                tsk_temp.append(new_used_a)
                tasks_share.append(tsk_temp)
        else:
            if tasks[i][1][-2] > rho:
                # heavy_b
                new_used_b = processors_heavy_b(tasks[i])
                if new_used_b < 0:
                    return 0
                else:
                    used_b = used_b + new_used_b
                tsk_temp = []
                tsk_temp.append(tasks[i])
                tsk_temp.append(2)
                tsk_temp.append(new_used_b)
                tasks_share.append(tsk_temp)
            else:
                tsk_temp = []
                tsk_temp.append(tasks[i])
                tsk_temp.append(3)
                tasks_share.append(tsk_temp)

    # judge if the used ab is larger than available ab processors
    if used_a > available_a or used_b > available_b:
        return 0

    available_a = available_a - used_a
    available_b = available_b - used_b

    if len(tasks_share) <= 1 and available_a > 0 and available_b > 0:
        return 1

    if available_a == 0 or available_b == 0:
        return 0

    partition = []
    partition_a = []
    partition_b = []
    for i in range(available_a):
        partition_a.append(deque())
    for i in range(available_b):
        partition_b.append(deque())

    # handle tasks_share
    # RM sort at first

    tasks_share = deque(sorted(tasks_share, key=lambda x: x[0][-1][-1]))
    for i in range(len(tasks_share)):
        # heavy_a
        if tasks_share[i][1] == 1:
            new_partitioned_b = sched_share_heavy_a(tasks_share[i][0], partition_b, tasks_share[i][2])
            if new_partitioned_b:
                partition_b = new_partitioned_b
            else:
                return 0
        # heavy_b
        elif tasks_share[i][1] == 2:
            new_partitioned_a = sched_share_heavy_b(tasks_share[i][0], partition_a, tasks_share[i][2])
            if new_partitioned_a:
                partition_a = new_partitioned_a
            else:
                return 0

        # light
        else:
            new_partitioned_ab = sched_share_light(tasks_share[i][0], [partition_a, partition_b])

            if new_partitioned_ab:
                partition_a = new_partitioned_ab[0]
                partition_b = new_partitioned_ab[1]
            else:
                return 0

    return 1


# calculate the a cores according to the b suspension time
def heavy_a_cores(heavy_a, suspension_b):
    m_a = math.ceil((heavy_a[1][-3] * heavy_a[-1][-1] - heavy_a[2][-3]) / (suspension_b - heavy_a[2][-3]))
    return m_a


# calculate the b cores according to the a suspension time
def heavy_b_cores(heavy_b, suspension_a):
    m_b = math.ceil((heavy_b[1][-2] * heavy_b[-1][-1] - heavy_b[2][-2]) / (suspension_a - heavy_b[2][-2]))
    return m_b


# find the minimal a cores for heavy_a
def minimal_heavy_a(heavy_a, partition_b_org):
    partition_b = copy.deepcopy(partition_b_org)
    upper_bound_a = processors_heavy_a(heavy_a)

    temp_info = []

    for i in range(len(partition_b)):
        suspension_b = heavy_a[-1][-1] * (1 - heavy_a[1][-2]) - sum_hp_a(heavy_a[-1][-1], partition_b[i])
        if suspension_b > 0:
            cores_needed = heavy_a_cores(heavy_a, suspension_b)
            if 0 < cores_needed <= upper_bound_a:
                temp_info.append([i, cores_needed])

    # select the partition with minimal a core
    if len(temp_info) > 0:
        temp_info.sort(key=lambda x: x[1])
        temp_partition = []
        temp_partition.append(heavy_a)
        response = sched_heavy_a(heavy_a, partition_b[temp_info[0][0]], temp_info[0][1])
        temp_partition.append(response)
        partition_b[temp_info[0][0]].append(temp_partition)
        return [partition_b, temp_info[0][1]]
    else:
        return False


def exclusive_heavy_a(heavy_a):
    upper_bound_a = processors_heavy_a(heavy_a)
    suspension_b = heavy_a[-1][-1] * (1 - heavy_a[1][-2])
    cores_needed = heavy_a_cores(heavy_a, suspension_b)
    if cores_needed <= upper_bound_a:
        return cores_needed
    else:
        return False


# find the minimal b cores for heavy_b
def minimal_heavy_b(heavy_b, partition_a_org):
    partition_a = copy.deepcopy(partition_a_org)
    upper_bound_b = processors_heavy_b(heavy_b)
    temp_info = []

    for i in range(len(partition_a)):
        suspension_a = heavy_b[-1][-1] * (1 - heavy_b[1][-3]) - sum_hp_b(heavy_b[-1][-1], partition_a[i])
        if suspension_a > 0:
            cores_needed = heavy_b_cores(heavy_b, suspension_a)
            if 0 < cores_needed <= upper_bound_b:
                temp_info.append([i, cores_needed])

    # select the partition with minimal a core
    if len(temp_info) > 0:
        temp_info.sort(key=lambda x: x[1])
        temp_partition = []
        temp_partition.append(heavy_b)
        response = sched_heavy_a(heavy_b, partition_a[temp_info[0][0]], temp_info[0][1])
        temp_partition.append(response)
        partition_a[temp_info[0][0]].append(temp_partition)
        return [partition_a, temp_info[0][1]]
    else:
        return False


def exclusive_heavy_b(heavy_b):
    upper_bound_b = processors_heavy_b(heavy_b)
    suspension_a = heavy_b[-1][-1] * (1 - heavy_b[1][-3])
    cores_needed = heavy_b_cores(heavy_b, suspension_a)
    if cores_needed <= upper_bound_b:
        return cores_needed
    else:
        return False


# try to add new cores to schedule a new light task
def shared_light_newcore(light_task, partitioned_ab_org, available_cores):
    # try to add one new core(s)
    partitioned_a = copy.deepcopy(partitioned_ab_org[0])
    partitioned_b = copy.deepcopy(partitioned_ab_org[1])
    available_a = copy.deepcopy(available_cores[0])
    available_b = copy.deepcopy(available_cores[1])

    if available_a == 0 and available_b == 0:
        return False

    if len(partitioned_a[0]) == 0:
        new_processor = []
        new_task = []
        new_task.append(light_task)
        new_task.append(light_task[0][-1] * light_task[-1][-1])
        new_processor.append(new_task)

        partitioned_a[0].append(new_task)
        partitioned_b.append(new_processor)
        available_b = available_b - 1

        return [partitioned_a, partitioned_b, available_a, available_b]

    if len(partitioned_b[0]) == 0:
        new_processor = []
        new_task = []
        new_task.append(light_task)
        new_task.append(light_task[0][-1] * light_task[-1][-1])
        new_processor.append(new_task)

        partitioned_b[0].append(new_task)
        partitioned_a.append(new_processor)

        available_a = available_a - 1

        return [partitioned_a, partitioned_b, available_a, available_b]

    # it is impossible that both a/b core are empty

    # only allocate one moe a core
    if available_a > 0 and available_a >= available_b:
        temp_partition_a = copy.deepcopy(partitioned_a)
        temp_partition_a.append([])

        temp_partition_ab = sched_share_light(light_task, [temp_partition_a, partitioned_b])
        if temp_partition_ab:
            partitioned_a = copy.deepcopy(temp_partition_ab[0])
            partitioned_b = copy.deepcopy(temp_partition_ab[1])
            available_a = available_a - 1
            return [partitioned_a, partitioned_b, available_a, available_b]

    # only allocate one more b core
    if available_b > 0 and available_b > available_a:
        temp_partition_b = copy.deepcopy(partitioned_b)
        temp_partition_b.append([])

        temp_partition_ab = sched_share_light(light_task, [partitioned_a, temp_partition_b])
        if temp_partition_ab:
            partitioned_a = copy.deepcopy(temp_partition_ab[0])
            partitioned_b = copy.deepcopy(temp_partition_ab[1])
            available_b = available_b - 1
            return [partitioned_a, partitioned_b, available_a, available_b]

    # allocate two new a/b cores
    if available_a > 0 and available_b > 0:
        new_processor = []
        new_task = []
        new_task.append(light_task)
        new_task.append(light_task[0][-1] * light_task[-1][-1])
        new_processor.append(new_task)

        partitioned_a.append(new_processor)
        partitioned_b.append(new_processor)

        available_a = available_a - 1
        available_b = available_b - 1
        return [partitioned_a, partitioned_b, available_a, available_b]

    # no sufficient cores are available
    else:
        return False


# check the combination of a/b processors
# if the one of the combination is feasible
def validate_heavy_ab(processor_ab, available_a, available_b, start_time):
    start_time_fix = copy.deepcopy(start_time)
    candidates = copy.deepcopy(processor_ab)
    a = copy.deepcopy(available_a)
    b = copy.deepcopy(available_b)

    if time.time()-start_time > 180:
        return False

    if a < 0 or b < 0:
        return False

    if not candidates:
        return 1

    for selection in candidates[-1]:
        if validate_heavy_ab(candidates[:-1], a - selection[0], b - selection[1], start_time_fix):
            return 1
    return False

# find if the heavy^a task can share a b core
def find_share_b(heavy_a, partition_b_org, exclusive_a_cores):
    partition_b = copy.deepcopy(partition_b_org)

    new_partition = sched_share_heavy_a(heavy_a, partition_b, exclusive_a_cores)

    if new_partition:
        return new_partition
    else:
        return False


# find if the heavy^b task can share a b core
def find_share_a(heavy_b, partition_a_org, exclusive_b_cores):
    partition_a = copy.deepcopy(partition_a_org)

    new_partition = sched_share_heavy_b(heavy_b, partition_a, exclusive_b_cores)

    if new_partition:
        return new_partition
    else:
        return False



def sum_utilization_one_a(paration_a):
    tasks = copy.deepcopy(paration_a)
    sum_u = 0
    for i in range(len(tasks)):
        sum_u = sum_u + tasks[i][0][2][-3]

    return sum_u

def sum_utilization_one_b(paration_b):
    tasks = copy.deepcopy(paration_b)
    sum_u = 0
    for i in range(len(tasks)):
        sum_u = sum_u + tasks[i][0][2][-2]

    return sum_u

# find the minimal a cores for heavy_a
def minimal_heavy_a_2(heavy_a, partition_b_org, rho):
    partition_b = copy.deepcopy(partition_b_org)
    upper_bound_a = processors_heavy_a(heavy_a)

    temp_info = []

    for i in range(len(partition_b)):
        if sum_utilization_one_b(partition_b[i]) < rho:
            suspension_b = heavy_a[-1][-1] * (1 - heavy_a[1][-2]) - sum_hp_a(heavy_a[-1][-1], partition_b[i])
            if suspension_b > 0:
                cores_needed = heavy_a_cores(heavy_a, suspension_b)
                if 0 < cores_needed <= upper_bound_a:
                    temp_info.append([i, cores_needed])

    # select the partition with minimal a core
    if len(temp_info) > 0:
        temp_info.sort(key=lambda x: x[1])
        temp_partition = []
        temp_partition.append(heavy_a)
        response = sched_heavy_a(heavy_a, partition_b[temp_info[0][0]], temp_info[0][1])
        temp_partition.append(response)
        partition_b[temp_info[0][0]].append(temp_partition)
        return [partition_b, temp_info[0][1]]
    else:
        return False


# find the minimal b cores for heavy_b
def minimal_heavy_b_2(heavy_b, partition_a_org, rho):
    partition_a = copy.deepcopy(partition_a_org)
    upper_bound_b = processors_heavy_b(heavy_b)
    temp_info = []

    for i in range(len(partition_a)):
        if sum_utilization_one_a(partition_a[i]) < rho:
            suspension_a = heavy_b[-1][-1] * (1 - heavy_b[1][-3]) - sum_hp_b(heavy_b[-1][-1], partition_a[i])
            if suspension_a > 0:
                cores_needed = heavy_b_cores(heavy_b, suspension_a)
                if 0 < cores_needed <= upper_bound_b:
                    temp_info.append([i, cores_needed])

    # select the partition with minimal a core
    if len(temp_info) > 0:
        temp_info.sort(key=lambda x: x[1])
        temp_partition = []
        temp_partition.append(heavy_b)
        response = sched_heavy_a(heavy_b, partition_a[temp_info[0][0]], temp_info[0][1])
        temp_partition.append(response)
        partition_a[temp_info[0][0]].append(temp_partition)
        return [partition_a, temp_info[0][1]]
    else:
        return False




# improved federated partitioned scheduling 3
def improved_federated_p3(task_set_org, processor_a, processor_b, rho, mod):
    task_set = copy.deepcopy(task_set_org)
    available_a = int(copy.deepcopy(processor_a))
    available_b = int(copy.deepcopy(processor_b))

    # rm sort the task
    task_set.sort(key=lambda x: x[-1][-1])

    heavy_ab = deque()
    partitioned_a = deque()
    partitioned_b = deque()

    available_a = available_a - 1
    partitioned_a.append([])

    available_b = available_b - 1
    partitioned_b.append([])

    for i in range(len(task_set)):
        # check if the task only require one type of processor
        # only require processor A:
        if task_set[i][1][-2] == 0:
            used_a = only_processor_a(task_set[i], available_a)
            if used_a > 0:
                available_a = available_a - used_a
            else:
                return 0

        # only require processor B:
        if task_set[i][1][-3] == 0:
            used_b = only_processor_b(task_set[i], available_b)
            if used_b > 0:
                available_b = available_b - used_b
            else:
                return 0

        # total utilization no larger than 1
        if task_set[i][0][-1] <= 1:
            temp_partition_ab = sched_share_light(task_set[i], [partitioned_a, partitioned_b])
            if temp_partition_ab:
                partitioned_a = copy.deepcopy(temp_partition_ab[0])
                partitioned_b = copy.deepcopy(temp_partition_ab[1])

            # the new task cannot be assigned on the used a/b processors
            else:
                temp_partition_ab = shared_light_newcore(task_set[i], [partitioned_a, partitioned_b],
                                                         [available_a, available_b])
                if temp_partition_ab:
                    partitioned_a = copy.deepcopy(temp_partition_ab[0])
                    partitioned_b = copy.deepcopy(temp_partition_ab[1])
                    available_a = copy.deepcopy(temp_partition_ab[2])
                    available_b = copy.deepcopy(temp_partition_ab[3])
                else:
                    return 0

        # heavy_ab
        elif task_set[i][1][-3] > rho and task_set[i][1][-2] > rho:
            heavy_ab.append(task_set[i])

        # heavy_a
        elif task_set[i][1][-3] > rho >= task_set[i][1][-2]:
            temp_heavy_a = minimal_heavy_a_2(task_set[i], partitioned_b, rho)
            if temp_heavy_a and task_set[i][2][-3] < task_set[i][-1][-1] / 3:
                if temp_heavy_a[1] > available_a:
                    heavy_ab.append(task_set[i])
                else:
                    partitioned_b = copy.deepcopy(temp_heavy_a[0])
                    available_a = available_a - temp_heavy_a[1]

            else:
                temp_heavy_a = exclusive_heavy_a(task_set[i])
                if temp_heavy_a:
                    if temp_heavy_a > available_a:
                        heavy_ab.append(task_set[i])
                    else:
                        new_core = []
                        new_task = []
                        new_task.append(task_set[i])
                        new_task.append(task_set[i][1][-2] * task_set[i][-1][-1] + suspension_b(task_set[i], temp_heavy_a))
                        new_core.append(new_task)
                        partitioned_b.append(new_core)
                        available_a = available_a - temp_heavy_a
                else:
                    heavy_ab.append(task_set[i])

        # heavy_b
        elif task_set[i][1][-3] <= rho < task_set[i][1][-2]:
            temp_heavy_b = minimal_heavy_b_2(task_set[i], partitioned_a, rho)
            if temp_heavy_b and task_set[i][2][-2] < task_set[i][-1][-1] / 3:
                if temp_heavy_b[1] > available_b:
                    heavy_ab.append(task_set[i])
                else:
                    partitioned_a = copy.deepcopy(temp_heavy_b[0])
                    available_b = available_b - temp_heavy_b[1]

            else:
                temp_heavy_b = exclusive_heavy_b(task_set[i])
                if temp_heavy_b:
                    if temp_heavy_b > available_b:
                        heavy_ab.append(task_set[i])
                    else:
                        new_core = []
                        new_task = []
                        new_task.append(task_set[i])
                        new_task.append(task_set[i][1][-3] * task_set[i][-1][-1] + suspension_a(task_set[i], temp_heavy_b))
                        new_core.append(new_task)
                        partitioned_a.append(new_core)
                        available_b = available_b - temp_heavy_b
                else:
                    heavy_ab.append(task_set[i])

    # handle the heavy_ab tasks
    if len(heavy_ab) == 0:
        return 1
    processor_ab = []
    lb_a_sum = 0
    lb_b_sum = 0
    for i in range(len(heavy_ab)):
        processor_ab_single = []
        lb_a = math.ceil(heavy_ab[i][1][-3])
        lb_a_sum = lb_a_sum + lb_a
        lb_b = math.ceil(heavy_ab[i][1][-2])
        lb_b_sum = lb_b_sum + lb_b

        if lb_a_sum > available_a or lb_b_sum > available_b:
            return 0
        else:
            for a in range(lb_a, available_a):
                for b in range(lb_b, available_b):
                    if mod == 1:
                        if hgsh(heavy_ab[i], [a, b]) <= heavy_ab[i][-1][-1]:
                            processor_ab_single.append([a, b])
                            break
                    else:
                        if heavy_cp.flexible_jobshop(heavy_ab[i], [a, b]) == 1:
                            processor_ab_single.append([a, b])
                            break

        processor_ab.append(processor_ab_single)

    # validate the possible combinations
    if len(processor_ab) <=0 and len(heavy_ab) > 0:
        return 0
    if len(processor_ab) == 1:
        for ca in range(len(processor_ab[0])):
            if processor_ab[0][ca][0] <= available_a and processor_ab[0][ca][1] <= available_b:
                return 1
        return 0
    else:
        feasible_ab = validate_heavy_ab(processor_ab, available_a, available_b, time.time())
        if feasible_ab:
            return 1
        else:
            return 0

    return 1


def sufficient_greedy(task_set_org, processor_a, processor_b, rho):
    task_set = copy.deepcopy(task_set_org)
    sum_ua = 0
    sum_ub = 0

    for i in range(len(task_set)):
        if task_set[i][3][-2] > (task_set[i][-1][-1]*rho):
            return 0
        if max(task_set[i][2][-3], task_set[i][2][-2]) > (task_set[i][-1][-1] * rho):
            # print("L_i^a or L_i^b's problem")
            return 0
        else:
            sum_ua = sum_ua + task_set[i][1][-3]
            sum_ub = sum_ub + task_set[i][1][-2]
            if max(sum_ua/processor_a, sum_ub/processor_b) > rho:
                return 0
    return 1


# the control function to collect results from all the schedulability test
def schedulability_han(tasksets, num_sets, processor_a, processor_b, mod):
    tasksets_local = copy.deepcopy(tasksets)
    accepted = 0

    for i in range(0, num_sets):
        accept = sched_han(tasksets_local[i], processor_a, processor_b, mod)
        accepted = accepted + accept

    return accepted


def schedulability_han_org(tasksets, num_sets, processor_a, processor_b, mod):
    tasksets_local = copy.deepcopy(tasksets)
    accepted = 0

    for i in range(0, num_sets):
        accept = sched_han_org(tasksets_local[i], processor_a, processor_b, mod)
        accepted = accepted + accept

    return accepted


def schedulability_greedy_federated(tasksets, num_sets, processor_a, processor_b, rho):
    tasksets_local = copy.deepcopy(tasksets)
    accepted = 0

    for i in range(0, num_sets):
        accept = greedy_federated_p(tasksets_local[i], rho, processor_a, processor_b)
        accepted = accepted + accept

    return accepted


def schedulability_sufficient_greedy(tasksets, num_sets, processor_a, processor_b, rho):
    tasksets_local = copy.deepcopy(tasksets)
    accepted = 0

    for i in range(0, num_sets):
        accept = sufficient_greedy(tasksets_local[i], processor_a, processor_b, rho)
        accepted = accepted + accept

    return accepted


def schedulability_improved_federated_new(tasksets, num_sets, processor_a, processor_b, rho, mod):
    tasksets_local = copy.deepcopy(tasksets)
    accept_org = 0

    for i in range(0, num_sets):

        accept = improved_federated_p3(tasksets_local[i], processor_a, processor_b, rho, mod)
        accept_org = accept_org + accept

    return accept_org
