from libs import *
from S1_data_input import *
# from S2_Generate_Population import *
from S2_Generate_Population_VFR import *
from S3_Fitness import *
from S4_Selection_1 import *
from S5_Crossover import *

# ============================================
# MS MUTATION: Machine Assignment Mutation (or Heuristic Best-machine Mutation)
# ============================================
def mutate_MS(MS, op_names, machine_options, p, mutation_rate=0.05):
    before_MS = MS.copy()
    log = []

    num_genes = len(MS)
    num_mut = max(1, int(num_genes * mutation_rate))
    mutate_positions = random.sample(range(num_genes), num_mut)

    for pos in mutate_positions:
        opname = op_names[pos]
        feasible = machine_options[opname]

        if len(feasible) <= 1:
            continue

        sorted_machines = sorted(feasible, key=lambda m: p[(opname, m)])
        best = sorted_machines[0]
        second_best = sorted_machines[1] if len(sorted_machines) >= 2 else best
        current_m = MS[pos]

        if random.random() < 0.30:
            # explore: randomly select a feasible machine different from the current one
            candidates = [m for m in feasible if m != current_m]
            new_m = random.choice(candidates) if candidates else current_m
            reason = "Random-feasible"
        else:
            # exploit: move to best / second-best as before
            if current_m != best:
                new_m = best
                reason = "Move-to-best"
            else:
                new_m = second_best
                reason = "Move-to-second-best"

        MS[pos] = new_m
        # SAVE LOG
        log.append({
            "pos": pos,
            "op": opname,
            "before": current_m,
            "after": new_m,
            "reason": reason
        })
    return MS, before_MS, log



def mutate_OS(OS, mutation_rate=0.05):

    before_OS = OS.copy()
    log = []
    num_genes = len(OS)
    # number of swaps (smaller than MS because OS is more sensitive)
    num_swaps = max(1, int(num_genes * mutation_rate))

    for _ in range(num_swaps):
        # select two different positions
        i, j = random.sample(range(num_genes), 2)
        job_i = OS[i]
        job_j = OS[j]
        # swap
        OS[i], OS[j] = OS[j], OS[i]
        # log
        log.append({
            "pos_1": i,
            "pos_2": j,
            "job_1_before": job_i,
            "job_2_before": job_j,
            "job_1_after": OS[i],
            "job_2_after": OS[j],
            "reason": "Swap"
        })

    return OS, before_OS, log

# ============================================
# MUTATION (PAIRWISE STYLE – BUT UNARY LOGIC)
# Each chromosome mutates independently
# ============================================
def mutation_pairwise(new_MS, new_OS, mutation_rate=0.10):

    Mutate_MS = []
    Mutate_OS = []
    mutation_method_list = []
    new_fitness = []

    pop_size = len(new_MS)

    for i in range(pop_size):
        MS = new_MS[i][:]
        OS = new_OS[i][:]

        if random.random() <= mutation_rate:
            # APPLY MUTATION
            MS, _, _ = mutate_MS(
                MS,
                op_names,
                machine_options,
                p
            )
            OS, _, _ = mutate_OS(OS)

            method = "MUTATED"
        else:
            # NO MUTATION
            method = "NO-MUTATION"

        Mutate_MS.append(MS)
        Mutate_OS.append(OS)
        mutation_method_list.append(method)

###########################################
        # FITNESS
        _, Cmax, *_ = decode(MS, OS)
        new_fitness.append(Cmax)
###########################################
    return Mutate_MS, Mutate_OS, mutation_method_list, new_fitness
    
Mutate_MS, Mutate_OS, mutation_method_list, new_fitness = mutation_pairwise(new_MS, new_OS)