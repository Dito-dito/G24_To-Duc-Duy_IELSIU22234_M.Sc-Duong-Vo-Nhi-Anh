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



def SA_accept_population(
    SA_MS, SA_OS, SA_fitness,
    new_SA_MS, new_SA_OS, new_SA_fitness,
    T0
):
    """
    Perform Step 11 & Step 12 of SA for the entire SA population
    """

    updated_MS = []
    updated_OS = []
    updated_fitness = []

    accept_log = []   # optional, very useful for debugging

    for i in range(len(SA_MS)):
        cur_MS = SA_MS[i][:]
        cur_OS = SA_OS[i][:]
        cur_fit = SA_fitness[i]

        nb_MS = new_SA_MS[i][:]
        nb_OS = new_SA_OS[i][:]
        nb_fit = new_SA_fitness[i]

        # =========================
        # Step 11: ΔE
        # =========================
        delta_E = nb_fit - cur_fit

        # =========================
        # Step 12.1: Better solution
        # =========================
        if delta_E < 0:
            updated_MS.append(nb_MS)
            updated_OS.append(nb_OS)
            updated_fitness.append(nb_fit)

            accept_log.append({
                "idx": i,
                "delta_E": delta_E,
                "accepted": True,
                "reason": "BETTER"
            })

        # =========================
        # Step 12.2: Worse solution
        # =========================
        else:
            if T0 <= 1e-8:
                P = 0
            else:
                P = math.exp(-delta_E / T0)
            x = random.random()

            if x < P:
                updated_MS.append(nb_MS)
                updated_OS.append(nb_OS)
                updated_fitness.append(nb_fit)

                accept_log.append({
                    "idx": i,
                    "delta_E": delta_E,
                    "accepted": True,
                    "reason": "PROB_ACCEPT",
                    "P": P,
                    "x": x
                })
            else:
                updated_MS.append(cur_MS)
                updated_OS.append(cur_OS)
                updated_fitness.append(cur_fit)

                accept_log.append({
                    "idx": i,
                    "delta_E": delta_E,
                    "accepted": False,
                    "reason": "REJECT",
                    "P": P,
                    "x": x
                })

    return updated_MS, updated_OS, updated_fitness, accept_log



def SA_cooling(T0, alpha, Tf):

    T_new = alpha * T0
    stop_flag = (T_new < Tf)

    return T_new, stop_flag




def run_SA(SA_MS, SA_OS, SA_fitness, T0, alpha, Tf):

    T0 = T0
    sa_iter = 0

    while True:
        sa_iter += 1

        new_SA_MS, new_SA_OS, new_SA_fitness = SA_choose_swap_or_insert_population(
            SA_MS, SA_OS
        )

        SA_MS, SA_OS, SA_fitness, _ = SA_accept_population(
            SA_MS, SA_OS, SA_fitness,
            new_SA_MS, new_SA_OS, new_SA_fitness,
            T0
        )

        T0, stop_flag = SA_cooling(T0, alpha, Tf)
        if stop_flag:
            break

    return SA_MS, SA_OS, SA_fitness, sa_iter

