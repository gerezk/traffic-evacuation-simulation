import traci
from launcher import get_sumo_cmd

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


if __name__ == "__main__":
    args = [
        "-n", "./data/neulengbach_sumo-webtools-osm.net.xml.gz",
    ]

    SUMO_CMD = get_sumo_cmd(args, gui=True)

    traci.start(SUMO_CMD)
    print(traci.vehicle.getIDCount())

    type_name = "car"
    traci.route.add(routeID="dynamicRoute", edges=["-29306230", "29306230", "-4681513#1"]) #these edges are from the rout.xml file, we will try to find a better way of handlimg
    generate_vehicle_type(type_name, 2.6, 4.5, (0,0,1), 5, 70)
    generate_car(type_name,0,0,0)
    for _ in range(1): # car gets created at departer time (aftter in simulation step)
        traci.simulationStep()
    print(traci.vehicle.getIDCount())
