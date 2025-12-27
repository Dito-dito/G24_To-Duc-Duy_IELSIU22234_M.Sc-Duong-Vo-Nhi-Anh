from libs import *
from S1_data_input import *
# from S2_Generate_Population import *
from S2_Generate_Population_VFR import *

# ============================================
# DECODE USING opId + opCounter
# ============================================

def decode(MS, OS):

    production_time_per_machine = {m: 0.0 for m in range(1, M+1)}
    production_energy_per_machine = {m: 0.0 for m in range(1, M+1)}

    shutdown_count = {m: 0 for m in range(1, M+1)}
    shutdown_intervals = {m: [] for m in range(1, M+1)}

    idle_energy_per_machine = {m: 0.0 for m in range(1, M+1)}
    shutdown_energy_per_machine = {m: 0.0 for m in range(1, M+1)}


    opCounter = {j: 0 for j in jobs}
    lastFinishJob = {j: 0 for j in jobs}
    lastFinishMachine = {m: 0 for m in range(1, M+1)}

    schedule = []

    # NEW: idle time tracking
    idle_time_per_machine = {m: 0.0 for m in range(1, M+1)}
    idle_intervals = {m: [] for m in range(1, M+1)}

    for job in OS:
        opCounter[job] += 1
        k = opCounter[job]

        q = opId[job][k-1]
        opname = op_names[q]
        machine = MS[q]

        proc = p[(opname, machine)]

        start = max(lastFinishJob[job], lastFinishMachine[machine])

        finish = start + proc
        prod_time = finish - start
        production_time_per_machine[machine] += prod_time


        lastFinishJob[job] = finish
        lastFinishMachine[machine] = finish

        schedule.append((opname, job, k, machine, start, finish))

    Cmax = max(finish for *_, finish in schedule)

    common_energy = Cmax * common_power


    machine_ops = defaultdict(list)
    # Group operations by machine
    for opname, job, k, m, start, finish in schedule:
        machine_ops[m].append((start, finish))


    # STANDARD IDLE / SHUTDOWN CALCULATION
    for m, ops in machine_ops.items():

        ops.sort(key=lambda x: x[0])

        # Only consider if there are at least 2 operations
        if len(ops) < 2:
            continue

        for i in range(len(ops) - 1):
            finish_i = ops[i][1]
            start_next = ops[i + 1][0]

            idle_time = start_next - finish_i

            if idle_time <= 0:
                continue

            # IDLE
            if idle_time < shutdown_threshold[m]:
                idle_energy_per_machine[m] += idle_time * idle_power[m]

            # SHUTDOWN (only when there is a subsequent operation)
            else:
                shutdown_count[m] += 1
                shutdown_energy_per_machine[m] += shutdown_energy[m]


    total_idle_energy = sum(idle_energy_per_machine.values())
    total_shutdown_energy = sum(shutdown_energy_per_machine.values())


    for m, prod_time in production_time_per_machine.items():
        production_energy_per_machine[m] = prod_time * production_power[m]

    total_production_energy = sum(production_energy_per_machine.values())


# ===========================================
# SINGLE OBJECTIVE: ENERGY
# ===========================================

    total_energy = (
        total_production_energy
        + total_idle_energy
        + total_shutdown_energy
        + common_energy
    )

    return (
        schedule,
        Cmax,
        idle_time_per_machine,
        idle_intervals,
        idle_energy_per_machine,
        total_idle_energy,
        shutdown_count,
        shutdown_energy_per_machine,
        total_shutdown_energy,
        total_energy,
        production_time_per_machine,
        production_energy_per_machine,
        total_production_energy,
        common_energy
    )


def create_population(pop_size):
    population_MS = []
    population_OS = []
    population_fitness = []
    population_type = []  # NEW

    for _ in range(pop_size):
        # Use generate_individual() instead of random generation
        MS, OS, type_flag = generate_individual()

        ############################################
        *_, total_energy = decode(MS, OS)
        ############################################

        population_MS.append(MS)
        population_OS.append(OS)
        population_fitness.append(total_energy)
        population_type.append(type_flag)  # NEW

    return population_MS, population_OS, population_fitness, population_type


population_MS, population_OS, population_fitness, population_type = create_population(pop_size)
