from libs import *
import colorsys


# ===============================
# LOAD DATA
# ===============================
df = pd.read_excel("GA_Debug_Full.xlsx", sheet_name="Best_Final_Schedule")

df["Start"] = pd.to_numeric(df["Start"])
df["Finish"] = pd.to_numeric(df["Finish"])
df["Machine"] = pd.to_numeric(df["Machine"], downcast="integer")
df["Job"] = pd.to_numeric(df["Job"], downcast="integer")
df["OpIdx"] = pd.to_numeric(df["OpIdx"], downcast="integer")
# ===============================
# HIGHLIGHT JOBS
# ===============================
highlight_jobs = {1, 2, 3}   # just keep color of the first 3 jobs

# ===============================
# AUTO INFER
# ===============================
machines = sorted(df["Machine"].unique())
jobs = sorted(df["Job"].unique())
Cmax = df["Finish"].max()

# ===============================
# FIGURE SCALE (GIỐNG HÌNH)
# ===============================
plt.figure(
    figsize=(
        max(20, Cmax * 0.35),           # scale width
        max(10, len(machines) * 0.9)    # height
    )
)
plt.xlim(0, Cmax * 1.02)


# ===============================
# COLOR BY JOB
# ===============================
job_color = {}

for job in jobs:
    if job in highlight_jobs:
        # pastel for job 1–3
        h = (job - 1) / 10
        s = 0.35
        v = 0.95
        job_color[job] = colorsys.hsv_to_rgb(h, s, v)
    else:
        # be gray for remaining jobs
        job_color[job] = (0.7, 0.7, 0.7)

# ===============================
# DRAW GANTT
# ===============================
min_text_ratio = 0.06

machine_to_y = {m: i for i, m in enumerate(machines)}

for y, m in enumerate(machines):
    df_m = df[df["Machine"] == m].sort_values("Start")

    for _, row in df.iterrows():
        y = machine_to_y[row["Machine"]]

        plt.barh(
            y=y,
            width=row["Finish"] - row["Start"],
            left=row["Start"],
            height=0.7,
            color=job_color[row["Job"]],
            edgecolor="black"
        )

# ===============================
# AXIS FORMAT
# ===============================
plt.yticks(
    range(len(machines)),
    [f"M{m}" for m in machines]
)

plt.xlabel("Time", fontsize=12)
plt.ylabel("Machine", fontsize=12)
plt.title("Gantt Chart – HGASA - 100 Jobs - P0=10", fontsize=14)

plt.grid(axis="x", linestyle="--", alpha=0.4)

# ===============================
# LEGEND
# ===============================
legend_patches = [
    mpatches.Patch(color=job_color[j], label=f"Job {j}")
    for j in jobs
]

plt.legend(
    handles=legend_patches,
    title="Jobs",
    bbox_to_anchor=(1.02, 1),
    loc="upper left",
    fontsize=9
)

plt.tight_layout()
plt.savefig("Gantt_Final_Styled.png", dpi=300, bbox_inches="tight")
plt.show()
