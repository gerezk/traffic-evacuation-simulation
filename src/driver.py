import yaml
from pathlib import Path
from utils import a
import random
import pandas as pd

import generate_TAZs


# load config
config_path = a(Path("config.yaml"))
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)

# overwrite n_sims if gui set to True
if cfg["gui"]:
    cfg["n_sims"] = 1

# check cfg input - need to check if blocked_edge in danger zone
assert cfg["scenario"] in [1, 2, 3], "scenario must be 1, 2, 3"
assert cfg["n_cars"] > 0, "n_cars must be > 0"
assert cfg["n_sims"] > 0, "n_sims must be > 0"
assert isinstance(cfg["gui"], bool), "gui must be True or False"

# create results directory and check if results already exist; ask to overwrite or not
results_dir = Path("../results")
results_dir.mkdir(parents=True, exist_ok=True)
csv_file_name = f"{cfg["scenario"]}_{cfg["n_cars"]}_{cfg["n_sims"]}_{cfg["parent_seed"]}.csv"
if Path(results_dir / csv_file_name).is_file():
    answer = input("Results for the given config.yaml already exist. Do you want to continue? (y/n) ")
    if answer in ["y", "Y", "Yes", "yes"]:
        print("Writing results to file...")
    elif answer in ["n", "N", "No", "no"] :
        exit()
    else:
        print("Invalid answer. Exiting.")
        exit()

# if TAZ.tax.xml not in ../tmp/, create file
abs_path_TAZ_str = a(cfg["rel_path_TAZ"])
path_TAZ = Path(abs_path_TAZ_str)
if not path_TAZ.is_file():
    generate_TAZs.main()

# generate set of random seeds
random.seed(cfg["parent_seed"])
SUMO_MAX_SEED = 2_147_483_647 # 32-bit int limit
seeds = [random.randint(0, SUMO_MAX_SEED) for _ in range(cfg["n_sims"])] # sample only positive seeds

# set sumo args - can be stored in a separate config file instead
sumo_args = [
    "-n", a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
    "--no-warnings",
    "-a", abs_path_TAZ_str + "," + a("../data/rerouter.add.xml"),
]

# import correct scenario.py given cfg
scenario_name = f"scenario{cfg["scenario"]}"
scenario_module = __import__(scenario_name)

# run n_sims and collect
dfs = [None] * cfg["n_sims"]
for i in range(cfg["n_sims"]):
    if cfg["scenario"] == 1:
        sim_output = scenario_module.main(abs_path_TAZ_str, sumo_args, cfg["n_cars"], seeds[i], cfg["gui"])
    elif cfg["scenario"] == 2 or cfg["scenario"] == 3: # extra arg needed for marking edge/road to block:
        sim_output = scenario_module.main(abs_path_TAZ_str, sumo_args, cfg["n_cars"], cfg["blocked_edge"], seeds[i], cfg["gui"])
    else:
        assert False, "Scenario must be 1, 2 or 3; issue not caught in earlier assert."

    dfs[i] = sim_output

# combine output into single df
results_df = pd.concat(dfs, ignore_index=True)

# export to csv
results_df.to_csv(results_dir / csv_file_name, index=False)
