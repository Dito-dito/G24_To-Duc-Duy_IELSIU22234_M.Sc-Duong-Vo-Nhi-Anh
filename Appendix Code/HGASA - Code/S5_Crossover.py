from libs import *
from S1_data_input import *
# from S2_Generate_Population import *
from S2_Generate_Population_VFR import *
from S3_Fitness import *
from S4_Selection_1 import *


# ============================================
# MS CROSSOVER: TWO-POINT CROSSOVER FOR MS
# ============================================
def two_point_crossover_MS(p1_MS, p2_MS):
    n = len(p1_MS)
    c1, c2 = sorted(random.sample(range(n), 2))

    child1 = p1_MS[:c1] + p2_MS[c1:c2] + p1_MS[c2:]
    child2 = p2_MS[:c1] + p1_MS[c1:c2] + p2_MS[c2:]

    return child1, child2


# ============================================
# MS CROSSOVER: UNIFORM CROSSOVER (5% swap)
# ============================================
def uniform_crossover_MS(p1_MS, p2_MS, rate=0.2):
    n = len(p1_MS)

    child1 = p1_MS.copy()
    child2 = p2_MS.copy()

    for i in range(n):
        if random.random() < rate:
            child1[i], child2[i] = child2[i], child1[i]

    return child1, child2


# ============================================
# OS CROSSOVER: JOB-BASED ORDER CROSSOVER
# ============================================
def job_based_ox(p1_OS, p2_OS, jobs):
    n = len(p1_OS)

    # 1) Select two cut points
    c1, c2 = sorted(random.sample(range(n), 2))

    # 2) Copy the segment from Parent 1
    child = [None] * n
    child[c1:c2] = p1_OS[c1:c2]

    # 3) Count the required number of occurrences for each job
    job_required = {}
    for j in jobs:
        job_required[j] = len(jobs[j])

    # 4) Count job occurrences in the copied segment
    job_count_child = {j: 0 for j in jobs}
    for x in child[c1:c2]:
        if x is not None:
            job_count_child[x] += 1

    # 5) Traverse Parent 2 and fill in missing jobs
    insert_pos = list(range(0, c1)) + list(range(c2, n))
    k = 0

    for job in p2_OS:
        if job_count_child[job] < job_required[job]:
            child[insert_pos[k]] = job
            job_count_child[job] += 1
            k += 1

    return child


def crossover_OS_pair(p1_OS, p2_OS, jobs):
    c1_OS = job_based_ox(p1_OS, p2_OS, jobs)
    c2_OS = job_based_ox(p2_OS, p1_OS, jobs)
    return c1_OS, c2_OS


# ============================================
# PAIRWISE CROSSOVER: (1,2), (3,4), (5,6), ...
# ============================================
def crossover_pairwise(selected_MS, selected_OS, crossover_rate=crossover_rate):
    new_MS = []
    new_OS = []
    new_fitness = []
    ms_method_list = []

    pop_size = len(selected_MS)

    # --------------------------------
    # HANDLE ODD NUMBER OF INDIVIDUALS
    # --------------------------------
    last_individual_kept = None
    if pop_size % 2 != 0:
        last_individual_kept = (
            selected_MS[-1],
            selected_OS[-1]
        )
        pop_size -= 1  # Eliminate the out-of-range

    # --------------------------------
    # CROSSOVER LOOP
    # --------------------------------
    for i in range(0, pop_size, 2):
        p1_MS = selected_MS[i]
        p2_MS = selected_MS[i+1]

        p1_OS = selected_OS[i]
        p2_OS = selected_OS[i+1]

        if random.random() > crossover_rate:
            c1_MS = p1_MS[:]
            c2_MS = p2_MS[:]
            c1_OS = p1_OS[:]
            c2_OS = p2_OS[:]
            method = "NO-CROSSOVER"

        else:
            if random.random() < 0.5:
                c1_MS, c2_MS = two_point_crossover_MS(p1_MS, p2_MS)
                method = "TWO-POINT"
            else:
                c1_MS, c2_MS = uniform_crossover_MS(p1_MS, p2_MS)
                method = "UNIFORM"

            c1_OS, c2_OS = crossover_OS_pair(p1_OS, p2_OS, jobs)

        new_MS.append(c1_MS); new_OS.append(c1_OS); ms_method_list.append(method)
        new_MS.append(c2_MS); new_OS.append(c2_OS); ms_method_list.append(method)

############################
        _, Cmax1, *_ = decode(c1_MS, c1_OS)
        _, Cmax2, *_ = decode(c2_MS, c2_OS)
############################


        new_fitness.append(Cmax1)
        new_fitness.append(Cmax2)

    # ----------------------------------------
    # ADD LAST INDIVIDUAL IF POP SIZE WAS ODD
    # ----------------------------------------
    if last_individual_kept is not None:
        last_MS, last_OS = last_individual_kept
        
        new_MS.append(last_MS)
        new_OS.append(last_OS)
        ms_method_list.append("NO-CROSSOVER-KEPT")

        ####################################
        _, Cmax_last, *_ = decode(last_MS, last_OS)
        ####################################
        new_fitness.append(Cmax_last)

    return new_MS, new_OS, ms_method_list, new_fitness

new_MS, new_OS, ms_method_list, new_fitness = crossover_pairwise(selected_MS, selected_OS)
