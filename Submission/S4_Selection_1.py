from libs import *
from S1_data_input import *
# from S2_Generate_Population import *
from S2_Generate_Population_VFR import *
from S3_Fitness import *

# ============================================
# TOURNAMENT SELECTION FOR GA MODEL
# ============================================

def tournament_selection(population_MS, population_OS, fitness, k=k):
    selected_MS = []
    selected_OS = []
    selected_indices = []
    pop_size = len(fitness)

    for _ in range(pop_size):
        # randomly select k candidate individuals (tournament selection)
        candidates = random.sample(range(pop_size), k)

        # select the individual with the minimum fitness value (Cmax minimization)
        best_idx = min(candidates, key=lambda idx: fitness[idx])

        selected_MS.append(population_MS[best_idx])
        selected_OS.append(population_OS[best_idx])
        selected_indices.append(best_idx)

    return selected_MS, selected_OS, selected_indices, pop_size

selected_MS, selected_OS, selected_idx, pop_size = tournament_selection(
    population_MS, population_OS, population_fitness
    )