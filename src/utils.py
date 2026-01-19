from pathlib import Path
import shutil
import traci
import random


def a(path):
    """
    Return absolute path given a relative path
    """
    return str((Path(__file__).parent / path).resolve())

# --------------------------------
# Sumo related functions below
# --------------------------------

# Needed to support use of the flatpack version of sumo
def get_sumo_cmd(base_args, gui=True):
    """
    base_args: list of SUMO arguments, e.g.
      ["-n", "net.xml", "-r", "routes.rou.xml", "--step-length", "0.1"]
    """
    binary = "sumo-gui" if gui else "sumo"

    if shutil.which(binary):
        return [binary] + base_args

    flatpak_id = "org.eclipse.sumo"
    return ["flatpak", "run", flatpak_id] + base_args

def run_sim():
    """
    Run simulation and collect results.
    :return:
    """
    step = 0
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()
        vehicle_ids = traci.vehicle.getIDList()  # vehicles currently on network
        print(vehicle_ids)
        print("Count:" + str(traci.vehicle.getIDCount()))
        step += 1

    traci.close()

def generate_car(veh_id, vehicle_type, route_id, depart_time=0 ): # didn't decide on how to initialize position yet
    # using veh id did not work cause it only counts cars that are currently driving
    traci.vehicle.add(vehID=veh_id, typeID=vehicle_type, depart=depart_time, routeID=route_id) # add to simulation
    #traci.vehicle.setRoutingMode(i, constants.ROUTING_MODE_IGNORE_TRANSIENT_PERMISSIONS)
    return veh_id

def generate_vehicle_type(type_name, accel, decel, color, length, max_speed, veh_class):
    traci.vehicletype.copy("DEFAULT_VEHTYPE", type_name)
    traci.vehicletype.setAccel(type_name, accel)
    traci.vehicletype.setDecel(type_name, decel)
    traci.vehicletype.setMaxSpeed(type_name, max_speed)
    traci.vehicletype.setLength(type_name, length)
    traci.vehicletype.setColor(type_name, color)
    traci.vehicletype.setVehicleClass(type_name, veh_class)

def getEdgesFromTaz(xmlRoot, zone):
    # Find the Zone_0 TAZ (Danger)
    danger_taz = xmlRoot.find(".//taz[@id='" + zone + "']")
    if danger_taz is None:
        raise ValueError("TAZ Danger_Zone_0 not found")

    # Get all edges
    edges = danger_taz.attrib.get("edges", "").split()
    return edges

def getRandomEdge(edges, zone):
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
        if ((vehicle_type in allowed) or (not allowed)) and (
                vehicle_type not in disallowed):  # empty means all types allowed
            allowed_lanes.append(lane_id)

    allowed_edges = list({traci.lane.getEdgeID(lane_id) for lane_id in allowed_lanes})

    return allowed_edges

def blockEdge(edgeID, vehicleType):
    """
    Used for scenario 2 & 3
    The config file sets the edgeID
    """
    traci.edge.setDisallowed(edgeID, vehicleType)

def isRoutePossible(from_edge, to_edge, vtype="car"):
    try:
        route = traci.simulation.findRoute(from_edge, to_edge, vType=vtype)
        return len(route.edges) > 0
    except traci.exceptions.TraCIException:
        return False
