import traci
import os
import sys
import time

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("SUMO_HOME not set")

sumoCmd = [
    "sumo-gui",
    "-c", "smart_ambulance.sumocfg",
    "--start"
]

traci.start(sumoCmd)

fog_alert_sent = False

while traci.simulation.getMinExpectedNumber() > 0:

    traci.simulationStep()

    if "A1" in traci.vehicle.getIDList():

        current_edge = traci.vehicle.getRoadID("A1")
        speed = traci.vehicle.getSpeed("A1")
        vehicle_count = traci.edge.getLastStepVehicleNumber(current_edge)

        print(
            f"Step: {traci.simulation.getTime()} | "
            f"Edge: {current_edge} | "
            f"Speed: {speed:.2f} | "
            f"Vehicles: {vehicle_count}"
        )

        # Fog Node Logic
        if vehicle_count >= 3 and not fog_alert_sent:

            print("\n==============================")
            print("FOG ALERT")
            print("Congestion Detected")
            print("Edge:", current_edge)
            print("Vehicle Count:", vehicle_count)
            print("Alternative Route Suggested")
            print("==============================\n")

            fog_alert_sent = True

    time.sleep(0.5)

traci.close()
