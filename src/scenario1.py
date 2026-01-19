import traci
from typing import List
import pandas as pd

import utils


def main(path_TAZ: str, args: List[str], n_cars: int, seed: int, gui: bool) -> pd.DataFrame:
    """
    :param path_TAZ: absolute path to the TAZ file, from config file
    :param args: sumo arguments passed to the script
    :param n_cars: from config file
    :param seed: child seed generated from parent seed set in config file
    :param gui: from config file
    :return: pd.dataframe of simulation results
    """

    # append seed to sumo args - seed must be set in both random and sumo
    args = args + ["--seed", str(seed)]

    SUMO_CMD = utils.get_sumo_cmd(args, gui)

    traci.start(SUMO_CMD)

    # get root path to TAZ file
    root_TAZ = utils.get_root_TAZ(path_TAZ)

    # Filter for edges that allow given vehicle type
    veh_type_name = "private"
    danger_zone_name = "Zone_0" # names from ../tmp/TAZ.taz.xml
    safe_zone_name = "Safe_Zone"
    safeTypedRoads, dangerTypedRoads = utils.filter_edges_by_veh_type(root_TAZ, veh_type_name, danger_zone_name, safe_zone_name)

    utils.generate_vehicle_type(veh_type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)

    # initialize n_cars in the sim
    utils.initialize_cars(seed, n_cars, safeTypedRoads, dangerTypedRoads, veh_type_name)

    # initialize dictionary for return
    output = {
        "seed": seed,
        "total_evac_time": -1
    }

    # run and step through sim
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()  # vehicles currently in network
        step += 1
    traci.close()

    output["total_evac_time"] = step
    return pd.DataFrame(output, index=[0])

if __name__ == "__main__":
    abs_path_TAZ = utils.a("../tmp/TAZ.taz.xml")
    sumo_args = [
        "-n", utils.a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
     #   "--no-warnings",
        "-a", abs_path_TAZ + "," + utils.a("../data/rerouter.add.xml"),
    ]

    main(abs_path_TAZ, sumo_args, 1000,42, True)