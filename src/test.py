import traci
import sumolib

SUMO_BINARY = "sumo-gui"

vehicle_exit_times = {}
vehicle_depart_times = {}

def run_simulation():
    traci.start([SUMO_BINARY, "-n", "./data/neulengbach_sumo-webtools-osm.net.xml.gz", "-r", "./data/routes.rou.xml"])
    # do something with sumolib
    traci.close()


if __name__ == "__main__":
    print("Running simulation")
    run_simulation()