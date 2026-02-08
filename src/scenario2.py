import traci
import xml.etree.ElementTree as ET
from typing import List
import pandas as pd

import utils


def main(path_TAZ: str, args: List[str], n_cars: int, blocked_edges: List[str], seed: int, gui: bool) -> pd.DataFrame:

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
    safeTypedRoads, dangerTypedRoads = utils.filter_edges_by_veh_type(root_TAZ, veh_type_name, safe_zone_name, danger_zone_name)

    utils.generate_vehicle_type(veh_type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)

    # get danger zone polygon from TAZ
    danger_polygon = utils.getPolygonFromTaz(root_TAZ, danger_zone_name)

    # get reachable danger edges given blocked road
    dangerTypedRoads = utils.get_reachable_danger_edges(safeTypedRoads, dangerTypedRoads, veh_type_name)

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

    # structures to keep track of individual vehicles
    evacuation_time = {}  # vehID -> time
    was_inside = {}  # vehID -> bool

    # run sim and collect data
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        t = traci.simulation.getTime()

        # get set of vehicles that have not yet evacuated
        vehicles_still_inside = set(traci.vehicle.getIDList()) # all vehicles in the sim at current time step
        vehicles_still_inside = vehicles_still_inside.difference(set(evacuation_time.keys()))

        # terminate sim if all cars evacuated, even if there are cars left still driving to their destinations
        if len(vehicles_still_inside) == 0:
            break

        # iterate over all vehicles still inside and check if they crossed into the safe zone
        for veh_id in vehicles_still_inside:
            x, y = traci.vehicle.getPosition(veh_id)
            inside = utils.point_in_polygon(x, y, danger_polygon)

            if veh_id not in was_inside:
                was_inside[veh_id] = inside
                continue

            # mark vehicle's first exit from the danger zone
            if was_inside[veh_id] and not inside:
                evacuation_time[veh_id] = t
                # print(f"Vehicle {veh_id} evacuated at {t:.1f}s")

            was_inside[veh_id] = inside

    traci.close()

    output["total_evac_time"] = max(evacuation_time.values())
    return pd.DataFrame(output, index=[0])

if __name__ == "__main__":
    abs_path_TAZ = utils.a("../tmp/TAZ.taz.xml")
    sumo_args = [
        "-n", utils.a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
        "-a", utils.a("../tmp/TAZ.taz.xml"),
    ]
    blocked_roads = ["489244165#0", "-489244165#1"]
  #  blocked_roads = ["-708937627#0", "1097648611"]

    main(abs_path_TAZ, sumo_args, 100, blocked_roads, 42, True)