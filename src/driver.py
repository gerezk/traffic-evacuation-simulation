import yaml
from pathlib import Path
from typing import List
import random
import pandas as pd

def load_config(path: Path) -> dict:
    with open(path, "r") as f:
        cfg_ = yaml.safe_load(f)

    return cfg_

def generate_seeds(parent_seed, n) -> List[int]:
    # Seed the random number generator with the parent seed
    random.seed(parent_seed)

    # Generate n seeds
    seeds_ = [random.randint(1 << 31, (1 << 32) - 1) for _ in range(n)]

    return seeds_

config_path = Path("config.yaml")
cfg = load_config(config_path)

# overwrite n_sims if gui set to True
if cfg["gui"]:
    cfg["n_sims"] = 1

# generate set of random seeds
seeds = generate_seeds(cfg["seed"], n=cfg["n_sims"])

# collect output from each sim

# combine to single df

# export to csv
