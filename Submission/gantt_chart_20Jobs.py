from libs import *
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
# AUTO INFER
# ===============================
machines = sorted(df["Machine"].unique())
jobs = sorted(df["Job"].unique())
Cmax = df["Finish"].max()

# ===============================
# FIGURE SCALE
# ===============================
plt.figure(
    figsize=(
        max(20, Cmax * 0.15),           # width
        max(10, len(machines) * 0.6)
    )
)

# ===============================
# COLOR BY JOB
# ===============================
cmap = plt.cm.get_cmap("tab20", len(jobs))
job_color = {job: cmap(i) for i, job in enumerate(jobs)}

# ===============================
# DRAW GANTT
# ===============================
for y, m in enumerate(machines):
    df_m = df[df["Machine"] == m].sort_values("Start")

    for _, row in df_m.iterrows():
        start, finish = row["Start"], row["Finish"]
        job, opidx = row["Job"], row["OpIdx"]

        plt.barh(
            y=y,
            width=finish - start,
            left=start,
            height=0.7,
            color=job_color[job],
            edgecolor="black",
            linewidth=0.6
        )

        # Jx-Oy
        plt.text(
            start + (finish - start) / 2,
            y,
            f"J{job}-O{opidx}",
            ha="center",
            va="center",
            fontsize=8,
            color="black"
        )

# ===============================
# AXIS FORMAT
# ===============================
plt.yticks(
    range(len(machines)),
    [f"M{m}" for m in machines],
    fontsize=11
)

plt.xlabel("Time", fontsize=12)
plt.ylabel("Machine", fontsize=12)
plt.title("Gantt Chart – HGASA - 20 Jobs", fontsize=14)

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
