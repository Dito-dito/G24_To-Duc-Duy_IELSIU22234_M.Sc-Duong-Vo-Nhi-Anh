from libs import *
from S1_data_input import *
# from S2_Generate_Population import *
from S2_Generate_Population_VFR import *
from S3_Fitness import *
from S4_Selection_1 import *
from S5_Crossover import *
from S6_Mutation import *
from S7_Select_input_SA import *
from S8_Generate_Neighborhood import *
from S9_SA_fitness import*





def keep_elites(population_MS, population_OS, population_fitness, elite_keep=2):
    """
    Keep top-k best chromosomes (elitism)
    """
    # sort index theo fitness tăng dần (minimize)
    idx_sorted = sorted(
        range(len(population_fitness)),
        key=lambda i: population_fitness[i]
    )

    elite_idx = idx_sorted[:elite_keep]

    elite_MS = [population_MS[i][:] for i in elite_idx]
    elite_OS = [population_OS[i][:] for i in elite_idx]
    elite_fit = [population_fitness[i] for i in elite_idx]

    return elite_MS, elite_OS, elite_fit


def GA_SA_cycle(
    population_MS,
    population_OS,
    population_fitness,
    pop_size,
    Gmax,
    T0_init,
    alpha,
    Tf
):

    GA_log = []
    Gene_change_log = []

     # ==============================
    # GLOBAL BEST MEMORY (VERY IMPORTANT)
    # ==============================
    global_best_fit = float("inf")
    global_best_MS = None
    global_best_OS = None

    no_improve_counter = 0
    RESTART_LIMIT = 10        # if no improvement for 10 generations → restart
    RESTART_RATIO = 0.2       # restart 20% of the population

    for gen in range(Gmax):
        GA_generation = gen + 1

        # ==============================
        # 0. UPDATE GLOBAL BEST
        # ==============================
        gen_best_idx = population_fitness.index(min(population_fitness))
        gen_best_fit = population_fitness[gen_best_idx]

        if gen_best_fit < global_best_fit:
            global_best_fit = gen_best_fit
            global_best_MS = population_MS[gen_best_idx][:]
            global_best_OS = population_OS[gen_best_idx][:]
            no_improve_counter = 0
        else:
            no_improve_counter += 1

        # ==============================
        # 1. ELITISM (KEEP TOP 2 INDIVIDUALS)
        # ==============================
        elite_MS_keep, elite_OS_keep, elite_fit_keep = keep_elites(
            population_MS, population_OS, population_fitness, elite_keep=2
        )

        # ==============================
        # 2. GA OPERATORS
        # ==============================
        selected_MS, selected_OS, _, _ = tournament_selection(
            population_MS, population_OS, population_fitness
        )

        new_MS, new_OS, _, _ = crossover_pairwise(
            selected_MS, selected_OS
        )

        population_MS, population_OS, _, population_fitness = mutation_pairwise(
            new_MS, new_OS
        )

        # ==============================
        # 3. RESTORE ELITES (Prevent  eliminating the good solutions)
        # ==============================
        worst_idx_sorted = sorted(
            range(len(population_fitness)),
            key=lambda i: population_fitness[i],
            reverse=True
        )
        for k in range(len(elite_fit_keep)):
            wi = worst_idx_sorted[k]
            population_MS[wi] = elite_MS_keep[k][:]
            population_OS[wi] = elite_OS_keep[k][:]
            population_fitness[wi] = elite_fit_keep[k]

        # ==============================
        # 4. SA ON ELITES
        # ==============================
        SA_MS, SA_OS, SA_fitness, elite_idx = select_elite_for_SA(
            population_MS, population_OS, population_fitness,
            pop_size, SA_choosen_ration=0.2
        )

        SA_MS_before = [ms[:] for ms in SA_MS]
        SA_OS_before = [os[:] for os in SA_OS]
        SA_fit_before = SA_fitness[:]

        SA_MS, SA_OS, SA_fitness, sa_iters = run_SA(
            SA_MS, SA_OS, SA_fitness,
            T0_init, alpha, Tf
        )

        # ==============================
        # 5. LOG SA GENE CHANGES
        # ==============================
        for i, ga_idx in enumerate(elite_idx):
            Gene_change_log.append({
                "GA_Generation": GA_generation,
                "GA_Index": ga_idx,
                "Fitness_Before": SA_fit_before[i],
                "Fitness_After": SA_fitness[i],
                "Delta": SA_fitness[i] - SA_fit_before[i],
                "MS_Changed": SA_MS_before[i] != SA_MS[i],
                "OS_Changed": SA_OS_before[i] != SA_OS[i],
            })

        # ==============================
        # 6. MEMETIC INJECTION (SA → GA)
        # ==============================
        best_SA_idx = SA_fitness.index(min(SA_fitness))
        best_SA_MS = SA_MS[best_SA_idx]
        best_SA_OS = SA_OS[best_SA_idx]
        best_SA_fit = SA_fitness[best_SA_idx]

        replace_n = max(1, int(0.1 * pop_size))
        worst_idx = sorted(
            range(pop_size),
            key=lambda i: population_fitness[i],
            reverse=True
        )[:replace_n]

        for i in worst_idx:
            population_MS[i] = best_SA_MS[:]
            population_OS[i] = best_SA_OS[:]
            population_fitness[i] = best_SA_fit

        # ==============================
        # 7. CONTROLLED RESTART (DESTROY ATTRACTOR)
        # ==============================
        if no_improve_counter >= RESTART_LIMIT:
            restart_n = max(1, int(RESTART_RATIO * pop_size))
            worst_idx = sorted(
                range(pop_size),
                key=lambda i: population_fitness[i],
                reverse=True
            )[:restart_n]

            for i in worst_idx:
                MS, OS, _ = generate_individual()
                #########################################
                """
                _, fit = decode(MS, OS)
                """
                _, fit, *_ = decode(MS, OS)
                #########################################
                population_MS[i] = MS
                population_OS[i] = OS
                population_fitness[i] = fit

            no_improve_counter = 0

        # ==============================
        # 8. LOG
        # ==============================
        GA_log.append({
            "GA_Generation": GA_generation,
            "Best_of_Generation": min(population_fitness),
            "Best_So_Far": global_best_fit,
            "Avg_Fitness": sum(population_fitness) / pop_size,
            "SA_Iterations": sa_iters
        })

    return population_MS, population_OS, population_fitness, GA_log, Gene_change_log
