import yaml
from pathlib import Path
from utils import a
import random
import pandas as pd
import generate_TAZs

# load config
config_path = Path("config.yaml")
with open(config_path, "r") as f:
    cfg = yaml.safe_load(f)

# overwrite n_sims if gui set to True
if cfg["gui"]:
    cfg["n_sims"] = 1

# set sumo args
sumo_args = [
    "-n", a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
    "-a", a("../tmp/TAZ.taz.xml") + "," + a("../data/rerouter.add.xml"),
]

# if TAZ.tax.xml not in ../tmp, create file
generate_TAZs.main()

# generate set of random seeds
random.seed(cfg["seed"])
seeds = [random.randint(1 << 31, (1 << 32) - 1) for _ in range(cfg["n_sims"])]

# run and collect output from n_sims


# combine output to single df

# export to csv
