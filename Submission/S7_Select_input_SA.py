from libs import *
from S1_data_input import *
# from S2_Generate_Population import *
from S2_Generate_Population_VFR import *
from S3_Fitness import *
from S4_Selection_1 import *
from S5_Crossover import *
from S6_Mutation import *



# ============================================
# SELECT TOP 20% BEST CHROMOSOMES FOR SA
# (USING EXISTING pop_size)
# ============================================

def select_elite_for_SA(population_MS, population_OS, population_fitness, pop_size, SA_choosen_ration=0.2):

    elite_n = max(1, int(pop_size * SA_choosen_ration))

    # sort indices according to ascending fitness values (minimizing objective)
    sorted_idx = sorted(
        range(pop_size),
        key=lambda i: population_fitness[i]
    )

    elite_idx = sorted_idx[:elite_n]

    SA_MS = [population_MS[i][:] for i in elite_idx]
    SA_OS = [population_OS[i][:] for i in elite_idx]
    SA_fitness = [population_fitness[i] for i in elite_idx]

    return SA_MS, SA_OS, SA_fitness, elite_idx

SA_MS, SA_OS, SA_fitness, elite_idx = select_elite_for_SA(population_MS, population_OS, population_fitness, pop_size, )