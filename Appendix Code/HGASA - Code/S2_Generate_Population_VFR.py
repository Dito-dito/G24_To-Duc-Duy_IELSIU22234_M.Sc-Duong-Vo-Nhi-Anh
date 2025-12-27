from libs import *
from S1_data_input import *

# ============================================
# BUILD opId[j][k] → q MAPPING (global operation indexing)
# ============================================

opId = {}
op_names = []
q = 0

for j in jobs:
    opId[j] = []
    for k, opname in enumerate(jobs[j], start=1):
        opId[j].append(q)    # save q (0-based)
        op_names.append(opname)
        q += 1

No = q        # total number of operations

machine_set = set()
for op, machines in machine_options.items():
    for m in machines:
        machine_set.add(m)

M = max(machine_set)

# ============================================
# RANDOM GENERATION
# ============================================

def random_MS():
    """Random machine selection vector"""
    MS = []
    for opname in op_names:
        MS.append(random.choice(machine_options[opname]))
    return MS

def random_OS():
    """Random job sequence vector"""
    OS = []
    for j in jobs:
        OS += [j] * len(jobs[j])
    random.shuffle(OS)
    return OS

# ============================================
# GLOBAL GENERATION (SPT-style)
# ============================================
def global_MS():
    """
    Global MS generation:
    - Schedule-aware
    - Use machine load (Earliest Completion Time)
    - Follow op_names, jobs, machine_options, p
    """

    # 1. Create load for each machine
    machine_load = {m: 0 for m in range(1, M + 1)}

    # 2. Create empty MS
    MS = [None] * No

    # 3. Random jobs order
    job_order = list(jobs.keys())
    random.shuffle(job_order)

    # 4. Select job → operation
    for j in job_order:
        for k, opname in enumerate(jobs[j]):
            op_index = opId[j][k]   # index in MS

            best_machine = None
            best_completion = float("inf")

            # 5. Try the available set of machine
            for m in machine_options[opname]:
                completion_time = machine_load[m] + p[(opname, m)]

                if completion_time < best_completion:
                    best_completion = completion_time
                    best_machine = m

            # 6. Assign the machine and update load
            MS[op_index] = best_machine
            machine_load[best_machine] += p[(opname, best_machine)]

    return MS


def global_OS():
    """OS will be randomly assigned, do not follow any rules """
    OS = []
    for j in jobs:
        OS += [j] * len(jobs[j])
    random.shuffle(OS)
    return OS

# ============================================
# LOCAL GENERATION (Machine Selection Local)
# ============================================

def local_MS():
    """
    Local Hybrid Machine Selection:
    - Consider about machine load (ECT)
    - Keep diversity of GA
    """

    # 1. Create load for each machine
    machine_load = {m: 0 for m in range(1, M + 1)}

    # 2. Empty MS
    MS = [None] * No

    # 3. Select the operation baseds on the orders op_names
    for idx, opname in enumerate(op_names):

        # Calculate completion time for each available nmachine
        completion_list = []
        for m in machine_options[opname]:
            completion_time = machine_load[m] + p[(opname, m)]
            completion_list.append((m, completion_time))

        # Arrange based on completion time
        completion_list.sort(key=lambda x: x[1])

        # Take top 2 best machines (Similar with Local Generation)
        top_k = completion_list[:2] if len(completion_list) >= 2 else completion_list

        # Randomly select in top-k
        chosen_m = random.choice(top_k)[0]

        # Assign machine anf update loadGán machine & cập nhật load
        MS[idx] = chosen_m
        machine_load[chosen_m] += p[(opname, chosen_m)]

    return MS

def local_OS():
    """Local job ordering: SPT based on the first operation"""
    # Calculate for the first operation in each job
    first_op = {}
    for j in jobs:
        opname = jobs[j][0]  # first operation
        best_pt = min(p[(opname, m)] for m in machine_options[opname])
        first_op[j] = best_pt

    # sort base on processing time of the first operation
    sorted_jobs = sorted(first_op, key=lambda x: first_op[x])

    OS = []
    for j in sorted_jobs:
        OS += [j] * len(jobs[j])
    return OS

# ============================================
# MAIN GENERATOR WITH 60% GLOBAL -- 30% LOCAL -- 10% RANDOM
# ============================================

def generate_individual():
    r = random.randint(1, 100)

    if r <= 60:
        MS = global_MS()
        OS = global_OS()
        type_flag = "GLOBAL"

    elif r <= 90:
        MS = local_MS()
        OS = local_OS()
        type_flag = "LOCAL"

    else:
        MS = random_MS()
        OS = random_OS()
        type_flag = "RANDOM"

    return MS, OS, type_flag