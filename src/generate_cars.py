import traci
from traci import constants
from launcher import get_sumo_cmd
import xml.etree.ElementTree as ET
import random
from pathlib import Path

def generate_vehicle_type(type_name, accel, decel, color, length, max_speed, veh_class):
    traci.vehicletype.copy("DEFAULT_VEHTYPE", type_name)
    traci.vehicletype.setAccel(type_name, accel)
    traci.vehicletype.setDecel(type_name, decel)
    traci.vehicletype.setMaxSpeed(type_name, max_speed)
    traci.vehicletype.setLength(type_name, length)
    traci.vehicletype.setColor(type_name, color)
    traci.vehicletype.setVehicleClass(type_name, veh_class)

def generate_car(veh_id, vehicle_type, route_id, depart_time=0 ): #didnt decide on how to initialize position yet
    # using veh id did not work cause it only counts cars that are currently driving
    traci.vehicle.add(vehID=veh_id, typeID=vehicle_type, depart=depart_time, routeID=route_id) # add to simulation
    #traci.vehicle.setRoutingMode(i, constants.ROUTING_MODE_IGNORE_TRANSIENT_PERMISSIONS)
    return veh_id

def getEdgesFromTaz(xmlRoot, zone):
    # Find the Danger_Zone_0 TAZ
    danger_taz = xmlRoot.find(".//taz[@id='" + zone + "']")
    if danger_taz is None:
        raise ValueError("TAZ Danger_Zone_0 not found")

    # Get all edges
    edges = danger_taz.attrib.get("edges", "").split()
    return edges

def getRandomEdge(edges):
    if not edges:
        raise ValueError(f"No edges defined in {zone}")

    # Pick a random edge
    random_edge = random.choice(edges)

    return random_edge



def getEdgesForVehicleType(vehicle_type: str):
    """
    Seems like the default type for car is called "private"
    """
    allowed_lanes = []

    # Get all lane IDs in the network
    all_lanes = traci.lane.getIDList()  # returns list of lane IDs

    for lane_id in all_lanes:
        allowed = traci.lane.getAllowed(lane_id)  # list of allowed vehicle types
        disallowed = traci.lane.getDisallowed(lane_id)  # list of allowed vehicle types
        if ((vehicle_type in allowed) or (not allowed)) and (vehicle_type not in disallowed):  # empty means all types allowed
            allowed_lanes.append(lane_id)
    allowed_edges = []

    allowed_edges = list({traci.lane.getEdgeID(lane_id) for lane_id in allowed_lanes})
    
    return allowed_edges

def blockEdge(edgeID, vehicleType):
    traci.edge.setDisallowed(edgeID, vehicleType)

def a(path):
    return str((Path(__file__).parent / path).resolve())

def isRoutePossible(from_edge, to_edge, vtype="car"):
    try:
        route = traci.simulation.findRoute(from_edge, to_edge, vType=vtype)
        return len(route.edges) > 0
    except traci.exceptions.TraCIException:
        return False

if __name__ == "__main__":
    args = [
        "-n", a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
        "-a", a("../tmp/DangerTAZ.taz.xml") + "," + a("../data/rerouter.add.xml"),
    ]

    SUMO_CMD = get_sumo_cmd(args, gui=True)

    traci.start(SUMO_CMD)

    # Load the TAZ file
    taz_file = a("../tmp/DangerTAZ.taz.xml")
    tree = ET.parse(taz_file)
    root = tree.getroot()

    veh_type_name = "private"
    privateVehicleRoads = getEdgesForVehicleType(veh_type_name)
    dangerRoads = getEdgesFromTaz(root, "Danger_Zone_0")
    safeRoads = getEdgesFromTaz(root, "Safe_Zone")

    safeTypedRoads = list(set(privateVehicleRoads) & set(safeRoads)) # both conditions
    dangerTypedRoads = list(set(privateVehicleRoads) & set(dangerRoads)) # both conditions

    generate_vehicle_type(veh_type_name, 2.6, 4.5, (0, 0, 255), 5, 70, veh_type_name)

    for i in range(500):
        dangerEdge = getRandomEdge(dangerTypedRoads)
        print("Random edge in Danger_Zone_0:", dangerEdge)

        safeEdge = getRandomEdge(safeTypedRoads)
        print("Random edge in Safe_Zone:", safeEdge)

        if not isRoutePossible(dangerEdge, safeEdge, veh_type_name):
            continue  # pick new edges
        
        route_id = "dynamicRoute" + str(i)
        traci.route.add(routeID=route_id, edges=[dangerEdge, safeEdge]) #these edges are from the rout.xml file, we will try to find a better way of handlimg

        generate_car(i, veh_type_name, route_id, 0)
        
        # temporary obstructions: https://sumo.dlr.de/docs/Simulation/Routing.html#handling_of_temporary_obstructions
        # will reroute only when at the blocked road

        # blockEdge(safeEdge)

    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()  # vehicles currently on network
        print(vehicle_ids)
        print("Count:" + str(traci.vehicle.getIDCount()))
        step += 1

    traci.close()
