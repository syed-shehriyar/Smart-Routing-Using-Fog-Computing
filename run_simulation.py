import os
import sys
import time
import traci

# ----------------------------
# Check SUMO
# ----------------------------

if "SUMO_HOME" in os.environ:
    tools = os.path.join(os.environ["SUMO_HOME"], "tools")
    sys.path.append(tools)
else:
    sys.exit("SUMO_HOME not set")

# ----------------------------
# Start SUMO
# ----------------------------

sumoCmd = [
    "sumo-gui",
    "-c",
    "smart_ambulance.sumocfg",
    "--start"
]

traci.start(sumoCmd)

print("\n==========================================")
print(" SMART ROUTING USING FOG COMPUTING")
print(" Simulation Started")
print("==========================================\n")

# ----------------------------
# Variables
# ----------------------------

fog_alert_sent = False
rerouted = False

destination_edge = "61835130#1"

depart_time = {}
arrival_time = {}

# ----------------------------
# Simulation
# ----------------------------

try:

    while traci.simulation.getMinExpectedNumber() > 0:

        traci.simulationStep()

        # Slow down simulation
        time.sleep(0.5)

        vehicle_ids = traci.vehicle.getIDList()

        # ----------------------------
        # Departure Time
        # ----------------------------

        for amb in ["A1", "A2"]:

            if amb in vehicle_ids and amb not in depart_time:

                depart_time[amb] = traci.simulation.getTime()

                print(f"{amb} departed at {depart_time[amb]:.0f} sec")

        # ----------------------------
        # Smart Ambulance Monitoring
        # ----------------------------

        if "A1" in vehicle_ids:

            current_edge = traci.vehicle.getRoadID("A1")
            speed = traci.vehicle.getSpeed("A1")
            vehicle_count = traci.edge.getLastStepVehicleNumber(current_edge)

            print(
                f"Step {traci.simulation.getTime():.0f}"
                f" | Edge: {current_edge}"
                f" | Speed: {speed:.2f}"
                f" | Vehicles: {vehicle_count}"
            )

            # ----------------------------
            # Fog Alert
            # ----------------------------

            if vehicle_count >= 3 and not fog_alert_sent:

                print("\n================================")
                print("FOG ALERT GENERATED")
                print("Congestion Detected")
                print("Edge :", current_edge)
                print("Vehicle Count :", vehicle_count)
                print("================================\n")

                fog_alert_sent = True

            # ----------------------------
            # Dynamic Rerouting
            # ----------------------------

            if current_edge == "-615357552#2" and not rerouted:

                print("\n================================")
                print("PRE-CONGESTION DECISION POINT")
                print("Applying Alternative Route")
                print("================================")

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

                    print("\nDynamic Rerouting Activated\n")

                    rerouted = True

                except Exception as e:

                    print("Route Error :", e)

        # ----------------------------
        # Arrival Detection
        # ----------------------------

        for amb in ["A1", "A2"]:

            if amb in vehicle_ids:

                if amb not in arrival_time:

                    edge = traci.vehicle.getRoadID(amb)
                    speed = traci.vehicle.getSpeed(amb)

                    if edge == destination_edge and speed < 0.1:

                        arrival_time[amb] = traci.simulation.getTime()

                        travel = arrival_time[amb] - depart_time[amb]

                        print("\n================================")
                        print(f"{amb} ARRIVED AT HANIF HOSPITAL")
                        print(f"Travel Time : {travel:.0f} sec")
                        print("================================")

except traci.exceptions.FatalTraCIError:

    print("\nSUMO closed.")

finally:

    print("\n==========================================")
    print("FINAL RESULT")
    print("==========================================")

    for amb in ["A1", "A2"]:

        if amb in arrival_time:

            travel = arrival_time[amb] - depart_time[amb]

            print(f"{amb} Travel Time : {travel:.0f} sec")

        else:

            print(f"{amb} : Arrival Not Detected")

    if "A1" in arrival_time and "A2" in arrival_time:

        a1 = arrival_time["A1"] - depart_time["A1"]
        a2 = arrival_time["A2"] - depart_time["A2"]

        print("------------------------------------------")

        if a1 < a2:

            print("RESULT : Smart Ambulance (A1) arrived earlier.")

        elif a2 < a1:

            print("RESULT : Conventional Ambulance (A2) arrived earlier.")

        else:

            print("RESULT : Both ambulances arrived at the same time.")

        print("------------------------------------------")

    print("\nSimulation Completed Successfully")

    traci.close(False)
