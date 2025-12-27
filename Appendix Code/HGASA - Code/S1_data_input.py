from libs import *



common_power = 10
k = 5
crossover_rate = 0.7
T0 = 1000
alpha = 0.95
Tf = 1e-3
Gmax = 200
pop_size = int(input("Input the population size: "))




EXCEL_FILE = "input_data.xlsx"
SHEET = "CP"

df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET, header=None)


#=====================================
#JOBS
#=====================================
jobs = {}

row = 12              # Excel row 13
current_job = None
op_counter = {}

while row < len(df) and not pd.isna(df.iloc[row, 3]):  # Row D: operation
    job_cell = df.iloc[row, 2]   # col C
    op_idx   = df.iloc[row, 3]   # col D (1,2,3,...)

    # If have the new operation
    if not pd.isna(job_cell):
        current_job = int(job_cell)
        jobs[current_job] = []
        op_counter[current_job] = 1
    else:
        op_counter[current_job] += 1

    opname = f"O{current_job}{op_counter[current_job]}"
    jobs[current_job].append(opname)

    row += 1

#=====================================
#PROCESSING TIME AND MACHINE OPTIONS
#=====================================
p = {}
machine_options = {}

machine_start_col = 4   # col E = index 4
op_row = 12             # E13

for j in jobs:
    for opname in jobs[j]:
        machine_options[opname] = []

        for m in range(machine_start_col, df.shape[1]):
            val = df.iloc[op_row, m]

            if not pd.isna(val):   # blank cell == no available
                machine_id = m - machine_start_col + 1
                p[(opname, machine_id)] = float(val)
                machine_options[opname].append(machine_id)

        op_row += 1


#=====================================
# ENERGY 
#=====================================
production_power = {}
idle_power = {}
shutdown_energy = {}

for m in range(machine_start_col, df.shape[1]):
    machine_id = m - machine_start_col + 1

    production_power[machine_id] = float(df.iloc[9, m])   # row 10
    idle_power[machine_id]       = float(df.iloc[8, m])   # row 9
    shutdown_energy[machine_id]  = float(df.iloc[7, m])   # row 8


#=====================================
# SHUTDOWN BREAK EVEN 
#=====================================
shutdown_threshold = {}

for m in idle_power:
    shutdown_threshold[m] = shutdown_energy[m] / idle_power[m]