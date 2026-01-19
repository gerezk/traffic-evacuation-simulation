import traci
import xml.etree.ElementTree as ET
from typing import List
import pandas as pd

import utils


def main(path_TAZ: str, args: List[str], n_cars: int, blocked_edges: List[str], seed: int, gui: bool) -> pd.DataFrame:
    args = [
        "-n", utils.a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
        "--no-warnings",
        "-a", utils.a("../tmp/TAZ.taz.xml"),
    ]

    # append seed to sumo args - seed must be set in both random and sumo
    args = args + ["--seed", str(seed)]

    SUMO_CMD = utils.get_sumo_cmd(args, gui)

    traci.start(SUMO_CMD)

    # get root path to TAZ file
    root_TAZ = utils.get_root_TAZ(path_TAZ)

    # block roads
    veh_type_name = "private"
    for edge in blocked_edges:
        utils.blockEdge(edge,"private")

    # filter for edges that allow given vehicle type - duplicated code wih scenario1.py
    safe_zone_name, danger_zone_name = utils.get_zone_names()
    safeTypedRoads, dangerTypedRoads = utils.filter_edges_by_veh_type(root_TAZ, veh_type_name, danger_zone_name, safe_zone_name)

    utils.generate_vehicle_type(veh_type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)

    # initialize n_cars in the sim
    utils.initialize_cars(seed, n_cars, safeTypedRoads, dangerTypedRoads, veh_type_name)

    # temporary obstructions: https://sumo.dlr.de/docs/Simulation/Routing.html#handling_of_temporary_obstructions
    # will reroute only when at the blocked road
    # traci.vehicle.setRoutingMode(carID, constants.ROUTING_MODE_IGNORE_TRANSIENT_PERMISSIONS)

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
        "-a", utils.a("../tmp/TAZ.taz.xml"),
    ]
    blocked_edges = ["489244165#0", "-489244165#1"]

    main(abs_path_TAZ, sumo_args, 1000, blocked_edges, 42, True)