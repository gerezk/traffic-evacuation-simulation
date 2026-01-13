import traci
from launcher import get_sumo_cmd
import xml.etree.ElementTree as ET
import random
from pathlib import Path

def generate_vehicle_type(type_name, accel, decel, color, length, max_speed):
    traci.vehicletype.copy("DEFAULT_VEHTYPE", type_name)
    traci.vehicletype.setAccel(type_name, accel)
    traci.vehicletype.setDecel(type_name, decel)
    traci.vehicletype.setMaxSpeed(type_name, max_speed)
    traci.vehicletype.setLength(type_name, length)
    traci.vehicletype.setColor(type_name, color)

def generate_car(vehicle_type, position_x, position_y, depart_time=0 ): #didnt decide on how to initialize position yet
    veh_id = traci.vehicle.getIDCount() # no of currently running vehicles, since we start from 0 this gives the new id
    traci.vehicle.add(vehID=veh_id, typeID=vehicle_type, depart=depart_time, routeID="dynamicRoute") # add to simulation
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
        if vehicle_type in allowed or not allowed:  # empty means all types allowed
            allowed_lanes.append(lane_id)
    allowed_edges = []

    allowed_edges = list({traci.lane.getEdgeID(lane_id) for lane_id in allowed_lanes})
    
    return allowed_edges

def blockEdge(edgeID):
    # traci.edge.setAllowed(edgeID, ["none"]) # needs a known vehicle class
    # probably need to use "closed"
    return

def a(path):
    return (Path(__file__).parent / path).resolve()

if __name__ == "__main__":
    args = [
        "-n", a("../data/neulengbach_sumo-webtools-osm.net.xml.gz"),
        "-a", a("../tmp/DangerTAZ.taz.xml"),
    ]

    SUMO_CMD = get_sumo_cmd(args, gui=True)

    traci.start(SUMO_CMD)

    # Load the TAZ file
    taz_file = a("../tmp/DangerTAZ.taz.xml")
    tree = ET.parse(taz_file)
    root = tree.getroot()

    privateVehicleRoads = getEdgesForVehicleType("private")
    dangerRoads = getEdgesFromTaz(root, "Danger_Zone_0")
    safeRoads = getEdgesFromTaz(root, "Safe_Zone")

    safeTypedRoads = list(set(privateVehicleRoads) & set(safeRoads)) # both conditions
    dangerTypedRoads = list(set(privateVehicleRoads) & set(dangerRoads)) # both conditions

    dangerEdge = getRandomEdge(dangerTypedRoads)
    print("Random edge in Danger_Zone_0:", dangerEdge)

    safeEdge = getRandomEdge(safeTypedRoads)
    print("Random edge in Safe_Zone:", safeEdge)

    blockEdge(safeEdge)

    print(traci.vehicle.getIDCount())

    type_name = "car"
    traci.route.add(routeID="dynamicRoute", edges=[dangerEdge, safeEdge]) #these edges are from the rout.xml file, we will try to find a better way of handlimg
    
    generate_vehicle_type(type_name, 2.6, 4.5, (0, 0, 255), 5, 70)
    generate_car(type_name,0,0,0)
    
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()  # vehicles currently on network
        print(vehicle_ids)
        print("Count:" + str(traci.vehicle.getIDCount()))
        step += 1

    traci.close()
