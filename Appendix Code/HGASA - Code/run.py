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
from S9_SA_fitness import *
from S10_cycle import *


# ============================================
# TIMING
# ============================================
start_time = time.time()
def heartbeat(interval=40):
    while True:
        time.sleep(interval)
        elapsed = time.time() - start_time
        print(f"[HEARTBEAT] Still running ... elapsed = {elapsed:.1f} seconds")
        sys.stdout.flush()

heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
heartbeat_thread.start()


# ============================================
# POPULATION GENERATED
# ============================================
pop_rows = []
GA_log = []
Gene_change_log = []

for i in range(pop_size):
    pop_rows.append({
        "Individual": i + 1,
        "Type": population_type[i],
        "MS": str(population_MS[i]),
        "OS": str(population_OS[i]),
        "Fitness_Cmax": population_fitness[i]
    })
df_population = pd.DataFrame(pop_rows)

# ============================================
# TOURNAMENT SELECTION
# ============================================
sel_rows = []
for i in range(pop_size):
    sel_rows.append({
        "New_Individual": i + 1,
        "From_Original": selected_idx[i] + 1,
        "MS": str(selected_MS[i]),
        "OS": str(selected_OS[i]),
        "Fitness": population_fitness[selected_idx[i]]
    })
df_selection = pd.DataFrame(sel_rows)

# ============================================
# CROSSOVER
# ============================================
cross_rows = []
for i in range(len(new_MS)):
    cross_rows.append({
        "Individual": i + 1,
        "MS": str(new_MS[i]),
        "OS": str(new_OS[i]),
        "Crossover_Type": ms_method_list[i],
        "Fitness_Cmax": new_fitness[i]
    })
df_crossover = pd.DataFrame(cross_rows)


# ============================================
# MUTATION RESULT
# ============================================
mut_rows = []
for i in range(len(new_MS)):
    row = {
        "Individual": i + 1,
        "Mutation_Type": mutation_method_list[i],
        "MS_BEFORE": str(new_MS[i])
    }
    if mutation_method_list[i] == "MUTATED":
        MS_after, _, log = mutate_MS(
            new_MS[i][:],
            op_names,
            machine_options,
            p
        )
        row["MS_AFTER"] = str(MS_after)
        row["Mutation_Log"] = str(log)
    else:
        row["MS_AFTER"] = "NO MUTATION"
        row["Mutation_Log"] = ""
    mut_rows.append(row)
df_mutation = pd.DataFrame(mut_rows)

# ============================================
# DECODE RESULT
# ============================================
decode_rows = []
idx = 3 
schedule, Cmax, _, _, idle_energy_pm, total_idle_energy, shutdown_cnt, shutdown_energy_pm, total_shutdown_energy, *_ = \
    decode(Mutate_MS[idx], Mutate_OS[idx])

for opname, job, k, machine, start, finish in schedule:
    decode_rows.append({
        "Operation": opname,
        "Job": job,
        "Op_Index": k,
        "Machine": machine,
        "Start": start,
        "Finish": finish
    })
df_decode = pd.DataFrame(decode_rows)

# ============================================
# ELITE SELECTION FOR SA
# ============================================
elite_rows = []
for i in range(len(SA_MS)):
    elite_rows.append({
        "Elite_Individual": i + 1,
        "MS": str(SA_MS[i]),
        "OS": str(SA_OS[i]),
        "Fitness_Cmax": SA_fitness[i]
    })
df_elite = pd.DataFrame(elite_rows)


# ============================================
# SA CHANGE LOG (ONLY CHANGES) → EXCEL
# ============================================
sa_log_rows = []
for i in range(len(SA_MS)):
    row = {
        "Chromosome": i + 1,
        "OS_BEFORE": str(SA_OS[i]),
        "OS_AFTER": str(new_SA_OS[i]),
        "MS_BEFORE": str(SA_MS[i]),
        "MS_AFTER": str(new_SA_MS[i]),
        "Fitness_BEFORE": SA_fitness[i],
        "Fitness_AFTER": new_SA_fitness[i],
        "Delta_Fitness": new_SA_fitness[i] - SA_fitness[i]
    }


    row["OS_Changed"] = (SA_OS[i] != new_SA_OS[i])
    row["MS_Changed"] = (SA_MS[i] != new_SA_MS[i])

    sa_log_rows.append(row)

df_sa_log = pd.DataFrame(sa_log_rows)


sa_final_rows = []
for i in range(len(SA_MS)):
    sa_final_rows.append({
        "Individual": i + 1,
        "Fitness_Cmax": SA_fitness[i],
        "MS": str(SA_MS[i]),
        "OS": str(SA_OS[i])
    })
df_sa_final = pd.DataFrame(sa_final_rows)


best_idx = SA_fitness.index(min(SA_fitness))

df_sa_best = pd.DataFrame([{
    "Best_Individual": best_idx + 1,
    "Best_Cmax": SA_fitness[best_idx],
    "MS": str(SA_MS[best_idx]),
    "OS": str(SA_OS[best_idx])
}])


schedule, Cmax, _, _, idle_energy_pm, total_idle_energy, shutdown_cnt, shutdown_energy_pm, total_shutdown_energy, *_ = \
    decode(SA_MS[best_idx], SA_OS[best_idx])



sa_sched_rows = []
for opname, job, k, machine, start, finish in schedule:
    sa_sched_rows.append({
        "Operation": opname,
        "Job": job,
        "Op_Index": k,
        "Machine": machine,
        "Start": start,
        "Finish": finish
    })
df_sa_schedule = pd.DataFrame(sa_sched_rows)

# ============================================
# CALL OUT THE GA-SA CYCLE
# ============================================
population_MS, population_OS, population_fitness, GA_log, Gene_change_log = GA_SA_cycle(
    population_MS,
    population_OS,
    population_fitness,
    pop_size,
    Gmax,
    T0,
    alpha,
    Tf
)


best_idx = population_fitness.index(min(population_fitness))
best_MS = population_MS[best_idx]
best_OS = population_OS[best_idx]
######## best_Cmax = population_fitness[best_idx]


(
    best_schedule,
    best_Cmax,              
    _,
    _,
    idle_energy_pm,
    total_idle_energy,
    shutdown_count,
    shutdown_energy_pm,
    total_shutdown_energy,
    best_total_energy,        
    production_time_pm,
    production_energy_pm,
    total_production_energy,
    common_energy
) = decode(best_MS, best_OS)

# ==============================
# FINAL ENERGY SUMMARY
# ==============================

total_machine_energy = (
    total_production_energy
    + total_idle_energy
    + total_shutdown_energy
)

final_total_energy = total_machine_energy + common_energy

best_energy_rows = []

for m in idle_energy_pm.keys():
    best_energy_rows.append({
        "Machine": m,
        "Production_Energy": production_energy_pm[m],
        "Idle_Energy": idle_energy_pm[m],
        "Shutdown_Count": shutdown_count[m],
        "Shutdown_Energy": shutdown_energy_pm[m],
        "Total_Energy": (
            production_energy_pm[m]
            + idle_energy_pm[m]
            + shutdown_energy_pm[m]
        )
    })

df_best_energy = pd.DataFrame(best_energy_rows)

df_best_energy.loc["TOTAL"] = {
    "Machine": "TOTAL",
    "Production_Energy": total_production_energy,
    "Idle_Energy": total_idle_energy,
    "Shutdown_Count": sum(shutdown_count.values()),
    "Shutdown_Energy": total_shutdown_energy,
    "Total_Energy": final_total_energy
}


df_best_schedule = pd.DataFrame(
    best_schedule,
    columns=["Operation","Job","OpIdx","Machine","Start","Finish"]
)

df_GA_log = pd.DataFrame(GA_log)
df_gene_change = pd.DataFrame(Gene_change_log)


end_time = time.time()
total_time = end_time - start_time
print(f"\n=== FINISHED ===")
print(f"Total runtime: {total_time:.2f} seconds")
# ============================================
# OUTPUT FOR EXCEL
# ============================================  

with pd.ExcelWriter("GA_Debug_Full.xlsx", engine="openpyxl") as writer:

    # ===== Population summary =====
    pop_rows = []
    for i in range(len(population_MS)):
        pop_rows.append({
            "Individual": i+1,
            "Type": population_type[i],
            "Fitness_Cmax": population_fitness[i]
        })

    df_pop = pd.DataFrame(pop_rows)
    df_pop.to_excel(writer, sheet_name="Population", index=False)
    df_GA_log.to_excel(writer, sheet_name="GA_Iterations", index=False)
    df_gene_change.to_excel(writer, sheet_name="SA_Gene_Changes", index=False)

    df_best_info = pd.DataFrame([{
        "Best_Individual": best_idx + 1,
        "Best_Cmax": best_Cmax,
        "MS": str(best_MS),
        "OS": str(best_OS)
    }])
    df_best_schedule.to_excel(writer, sheet_name="Best_Final_Schedule", index=False)

    df_best_info.to_excel(writer, sheet_name="Best_Final_Solution", index=False)

    df_best_energy.to_excel(
        writer,
        sheet_name="Best_Energy_Breakdown",
        index=False
    )


print("✅ Exported file GA_Debug_Full.xlsx")

print("===== ENERGY SUMMARY =====")
print(f"Total production energy : {total_production_energy}")
print(f"Total idle energy       : {total_idle_energy}")
print(f"Total shutdown energy   : {total_shutdown_energy}")
print(f"Best Cmax (makespan)    : {best_Cmax}")
print(f"Common power (P0)       : {common_power}")
print(f"Common energy           : {common_energy}")
print(f"FINAL TOTAL ENERGY      : {final_total_energy}")
