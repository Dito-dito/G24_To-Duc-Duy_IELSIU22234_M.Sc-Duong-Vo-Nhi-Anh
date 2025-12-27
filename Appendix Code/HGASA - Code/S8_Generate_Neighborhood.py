from libs import *
from S1_data_input import *
# from S2_Generate_Population import *
from S2_Generate_Population_VFR import *
from S3_Fitness import *
from S4_Selection_1 import *
from S5_Crossover import *
from S6_Mutation import *
from S7_Select_input_SA import *


# ============================================
# SWAP NEIGHBORHOOD
# ============================================
def generate_neighbor_SA(SA_MS, SA_OS):
    swap_MS = []
    swap_OS = []
    swap_fitness = []

    for i in range(len(SA_MS)):
        MS = SA_MS[i][:]
        OS = SA_OS[i][:]

        # OS swap
        a, b = random.sample(range(len(OS)), 2)
        OS[a], OS[b] = OS[b], OS[a]

        # MS change
        pos = random.randrange(len(MS))
        opname = op_names[pos]
        feasible = machine_options[opname]

        if len(feasible) > 1:
            MS[pos] = random.choice([m for m in feasible if m != MS[pos]])


        _, cost, *_ = decode(MS, OS)

        swap_MS.append(MS)
        swap_OS.append(OS)
        swap_fitness.append(cost)

    return swap_MS, swap_OS, swap_fitness

swap_MS, swap_OS, swap_fitness = generate_neighbor_SA(SA_MS, SA_OS)

# ============================================
# INSERTION NEIGHBORHOOD
# ============================================
def insertion_neighborhood(SA_MS, SA_OS):

    insert_MS = []
    insert_OS = []
    insert_fitness = []

    for i in range(len(SA_MS)):
        # Remain MS
        MS = SA_MS[i][:]

        # Copy OS
        OS = SA_OS[i][:]

        # -------------------------
        # INSERTION NEIGHBORHOOD
        # -------------------------
        a, b = random.sample(range(len(OS)), 2)
        small, large = min(a, b), max(a, b)

        gene = OS.pop(large)
        OS.insert(small, gene)

        # -------------------------
        # FITNESS
        # -------------------------
        _, cost, *_ = decode(MS, OS)

        insert_MS.append(MS)
        insert_OS.append(OS)
        insert_fitness.append(cost)

    return insert_MS, insert_OS, insert_fitness

insert_MS, insert_OS, insert_fitness = insertion_neighborhood(SA_MS, SA_OS)


# ============================================
# CHOOSE GENERATION NEIGHBORHOOD
# ============================================
def SA_choose_swap_or_insert(MS, OS):
    X = random.randint(1, 100)

    if X <= 50:
        # use insertion neighborhood (for a single chromosome)
        nb_MS, nb_OS, nb_fit = insertion_neighborhood([MS], [OS])
    else:
        # use swap neighborhood (for a single chromosome)
        nb_MS, nb_OS, nb_fit = generate_neighbor_SA([MS], [OS])

    # since a list with one element is passed → take index [0]
    return nb_MS[0], nb_OS[0], nb_fit[0]


def SA_choose_swap_or_insert_population(SA_MS, SA_OS):
    new_SA_MS = []
    new_SA_OS = []
    new_SA_fitness = []

    for i in range(len(SA_MS)):
        MS_i = SA_MS[i]
        OS_i = SA_OS[i]

        nb_MS, nb_OS, nb_fit = SA_choose_swap_or_insert(MS_i, OS_i)

        new_SA_MS.append(nb_MS)
        new_SA_OS.append(nb_OS)
        new_SA_fitness.append(nb_fit)

    return new_SA_MS, new_SA_OS, new_SA_fitness

new_SA_MS, new_SA_OS, new_SA_fitness = SA_choose_swap_or_insert_population(SA_MS, SA_OS)

