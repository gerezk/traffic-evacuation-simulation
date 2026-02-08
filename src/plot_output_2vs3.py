import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import pandas as pd


# read in results
results_dir = Path("../results") # assumed to already exist
csv_files = ["2_500_oberehofstatt_10_42.csv",
             "2_1000_oberehofstatt_10_42.csv",
             "3_500_oberehofstatt_10_42.csv",
             "3_1000_oberehofstatt_10_42.csv"]
selected_csv = csv_files[0]

# extract configs
config = selected_csv.split("_")
scenario = config[0]
n_cars = config[1]
n_sims = config[2]

# collect dfs and extract configs
dfs = []
configs = []
for csv_file in csv_files:
    configs.append(csv_file.split("_"))
    dfs.append(pd.read_csv(results_dir / csv_file, index_col=0))

# create legend labels
labels = []
for config in configs:
    scenario = config[0]
    n_cars = config[1]
    labels.append(f"Scenario {scenario}, {n_cars} cars")

# plot data
colors = sns.color_palette("colorblind", n_colors=4)
fig, ax = plt.subplots()
for i in range(len(dfs)):
    sns.histplot(dfs[i]["total_evac_time"] / 60, bins=20, ax=ax, kde=False, alpha=0.4, # convert from s to min
                 label=labels[i],
                 color=colors[i])
    plt.axvline(dfs[i]["total_evac_time"].mean() / 60, linestyle="--",
                color=colors[i])
ax.set_title("Histogram of Total Evacuation Time for Various Scenarios")
ax.set_xlabel("Total Evacuation Time (min)")
ax.legend()
plt.tight_layout()

#plt.show()
plt.savefig(results_dir / 'total_evac_time_2vs3.png')