import traci
import xml.etree.ElementTree as ET
import random

import utils


def main(cfg: dict, seed: int):
    args = [
        "-n", utils.a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
        "-a", utils.a("../tmp/TAZ.taz.xml") + "," + utils.a("../data/rerouter.add.xml"),
    ]

    SUMO_CMD = utils.get_sumo_cmd(args, cfg["gui"])

    traci.start(SUMO_CMD)

    # Load the TAZ file
    taz_file = utils.a("../tmp/TAZ.taz.xml")
    tree = ET.parse(taz_file)
    root = tree.getroot()

    veh_type_name = "private"
    privateVehicleRoads = utils.getEdgesForVehicleType(veh_type_name)
    dangerRoads = utils.getEdgesFromTaz(root, "Zone_0")
    safeRoads = utils.getEdgesFromTaz(root, "Safe_Zone")

    # Sort lists after to ensure order consistent across runs
    safeTypedRoads = sorted(list(set(privateVehicleRoads) & set(safeRoads)))  # both conditions
    dangerTypedRoads = sorted(list(set(privateVehicleRoads) & set(dangerRoads)))  # both conditions

    utils.generate_vehicle_type(veh_type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)

    random.seed(seed) # ensure reproducibility in using utils.getRandomEdge
    for i in range(cfg["n_cars"]):
        dangerEdge = utils.getRandomEdge(dangerTypedRoads, zone="Zone_0")
        print("Random edge in Zone_0:", dangerEdge)

        safeEdge = utils.getRandomEdge(safeTypedRoads, zone="Safe_Zone")
        print("Random edge in Safe_Zone:", safeEdge)

        if not utils.isRoutePossible(dangerEdge, safeEdge, veh_type_name):
            continue  # pick new edges

        route_id = "dynamicRoute" + str(i)
        traci.route.add(routeID=route_id, edges=[dangerEdge,
                                                 safeEdge])  # these edges are from the rout.xml file, we will try to find a better way of handling

        utils.generate_car(i, veh_type_name, route_id, 0)

        # temporary obstructions: https://sumo.dlr.de/docs/Simulation/Routing.html#handling_of_temporary_obstructions
        # will reroute only when at the blocked road

        # utils.blockEdge(safeEdge)

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()  # vehicles currently on network
        print(vehicle_ids)
        print("Count:" + str(traci.vehicle.getIDCount()))
        step += 1

    traci.close()

if __name__ == "__main__":
    config_scenario1 = {'n_cars': 1000,
              'gui': True}

    main(config_scenario1, 42)