import yaml
from pathlib import Path
from utils import a
import random
import pandas as pd

import generate_TAZs
import scenario1


# load config
config_path = a(Path("config.yaml"))
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)

# overwrite n_sims if gui set to True
if cfg["gui"]:
    cfg["n_sims"] = 1

# set sumo args
abs_path_TAZ_str = a(cfg["rel_path_TAZ"])
sumo_args = [
    "-n", a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
    "--no-warnings",
    "-a", abs_path_TAZ_str + "," + a("../data/rerouter.add.xml"),
]

# if TAZ.tax.xml not in ../tmp/, create file
path_TAZ = Path(abs_path_TAZ_str)
if not path_TAZ.is_file():
    generate_TAZs.main()

# generate set of random seeds
random.seed(cfg["parent_seed"])
SUMO_MAX_SEED = 2_147_483_647 # 32-bit int limit
seeds = [random.randint(0, SUMO_MAX_SEED) for _ in range(cfg["n_sims"])] # sample only positive seeds

# run and collect output from n_sims
for i in range(cfg["n_sims"]):
    scenario1.main(abs_path_TAZ_str, sumo_args, cfg["n_cars"], seeds[i], cfg["gui"])

# combine output to single df

# export to csv
