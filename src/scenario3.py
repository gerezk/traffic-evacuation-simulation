import traci
import sumolib
from typing import List
import pandas as pd
import xml.etree.ElementTree as ET

import utils

TRIGGER_STEPS = 3
OUT_FILE = "../data/rerouter.add.xml"
NETWORK_FILE =  '../data/neulengbach_sumo-webtools-osm.net.xml.gz'
def configure_rerouter(network_file, blocked_edges, additional_config):
    net = sumolib.net.readNet(network_file)
    trigger_edges = set()
    for i in range(len(blocked_edges)):
        blocked = blocked_edges[i]
        print("blocked"+str(blocked))
        neighbors = utils.get_adjacent_edges(blocked, TRIGGER_STEPS, net)
        trigger_edges.update(neighbors)
        
        #Check for edge in other direction
        if blocked.startswith("-"):
            opposite = blocked[1:]
        else:
            opposite = "-" + blocked

        if net.hasEdge(opposite):
            blocked_edges.add(opposite)
            print(f"added {opposite} to blocked_edges as opposite")
            neighbors = utils.get_adjacent_edges(blocked, TRIGGER_STEPS, net)
            trigger_edges.update(neighbors)


    tree = ET.parse(additional_config)
    root = tree.getroot()

    #additional = ET.Element("additional")
    additional = root
    rerouter_id = "rerouter"

    rerouter = additional.find(f"./rerouter[@id='{rerouter_id}']")

    if rerouter is not None:
        additional.remove(rerouter)

    rerouter = ET.SubElement(
        additional,
        "rerouter",
        {
            "id": "rerouter",
            "edges": " ".join(sorted(trigger_edges))
        }
    )

    interval = ET.SubElement(
        rerouter,
        "interval",
        {
            "begin": "0",
            "end": "1000000"
        }
    )

    for edge in blocked_edges:
        ET.SubElement(
            interval,
            "closingReroute",
            {"id": edge} 
        )


    #tree = ET.ElementTree(additional)
    #tree.write(OUT_FILE)

    tree.write(additional_config, encoding="utf-8", xml_declaration=True)

def main(path_TAZ: str, args: List[str], n_cars: int, blocked_edges: List[str], seed: int, gui: bool) -> pd.DataFrame:
    """
    :param path_TAZ: absolute path to the TAZ file, from config file
    :param args: sumo arguments passed to the script
    :param n_cars: from config file
    :param seed: child seed generated from parent seed set in config file
    :param gui: from config file
    :return: pd.dataframe of simulation results
    """

    # append seed to sumo args - seed must be set in both random and sumo
    abs_path_TAZ = utils.a("../tmp/TAZ.taz.xml")
    configure_rerouter(NETWORK_FILE, blocked_edges, abs_path_TAZ)

    args = args + ["--seed", str(seed)]
    #args = args + ["-a", str(OUT_FILE)]

    SUMO_CMD = utils.get_sumo_cmd(args, gui)    

    traci.start(SUMO_CMD)

    # get root path to TAZ file
    root_TAZ = utils.get_root_TAZ(path_TAZ)

    # define vehicle
    veh_type_name = "private"
    utils.generate_vehicle_type(veh_type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)

    # Filter for edges that allow given vehicle type
    safe_zone_name, danger_zone_name = utils.get_zone_names()
    safeTypedRoads, dangerTypedRoads = utils.filter_edges_by_veh_type(root_TAZ, veh_type_name, safe_zone_name, danger_zone_name)

    # get danger zone polygon from TAZ
    danger_polygon = utils.getPolygonFromTaz(root_TAZ, danger_zone_name)

    # initialize n_cars in the sim
    utils.initialize_cars(seed, n_cars, safeTypedRoads, dangerTypedRoads, veh_type_name)


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
     #   "--no-warnings",
        "-a", abs_path_TAZ# + "," + utils.a("../data/rerouter.add.xml")
    ]
    blocked_roads = ["489244165#0", "-489244165#1"]

    main(abs_path_TAZ, sumo_args, 100, blocked_roads, 42, True)