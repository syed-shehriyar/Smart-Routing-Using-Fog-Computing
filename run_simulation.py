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

# Simulation start time
start_time = traci.simulation.getTime()

fog_alert_sent = False
rerouted = False

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

        # -----------------------------
        # Fog Alert
        # -----------------------------
        if vehicle_count >= 3 and not fog_alert_sent:

            print("\n==============================")
            print("FOG ALERT")
            print("Congestion Detected")
            print("Edge:", current_edge)
            print("Vehicle Count:", vehicle_count)
            print("Alternative Route Suggested")
            print("==============================\n")

            fog_alert_sent = True

        # -----------------------------
        # Dynamic Rerouting
        # -----------------------------
        if current_edge == "-615357552#2" and not rerouted:

            print("\n==============================")
            print("PRE-CONGESTION ALERT")
            print("Ambulance approaching congested area")
            print("Attempting reroute...")
            print("==============================")

            new_route = [
                "-615357552#2",
                "60825792#2",
                "60825792#3",
                "-895066327#0",
                "-61835139#1",
                "-61835139#0",
                "61835130#1"
            ]

            try:

                traci.vehicle.setRoute("A1", new_route)

                print("\n==============================")
                print("DYNAMIC REROUTING ACTIVATED")
                print("New Route Applied")
                print("==============================\n")

                rerouted = True

            except Exception as e:

                print("\n==============================")
                print("ROUTE ERROR")
                print(e)
                print("==============================\n")

    time.sleep(0.5)

arrival_time = traci.simulation.getTime()

print("\n====================")
print("AMBULANCE ARRIVED")
print("Total Travel Time:", arrival_time - start_time, "seconds")
print("====================")

traci.close()
