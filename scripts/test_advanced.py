import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_ingestion.synthetic_advanced import generate_cvrptw_data
from optimization.or_tools_cvrptw import solve_cvrptw

def main():
    print("---------------------------------------------------------")
    print("Generating CVRPTW Constraint Scenario Map...")
    print("---------------------------------------------------------")
    
    # Intentionally utilizing constraints that force trucks to balance capacity and clock timers.
    data = generate_cvrptw_data(
        num_locations=6, 
        num_vehicles=2, 
        vehicle_capacity=40, # Cannot accept more demand than this universally
        random_seed=42
    )
    
    print("\n--- Package Payload Demands per Target ---")
    for idx, d in enumerate(data["demands"]):
        print(f"Node {idx:<2}: {d:<3} kg demand")
        
    print("\n--- Shift Working Delivery Time Windows (Minutes) ---")
    for idx, tw in enumerate(data["time_windows"]):
        print(f"Node {idx:<2}: Opens strictly at min {tw[0]:<3} | Closes absolutely at min {tw[1]:<3}")
        
    print("\n\n---------------------------------------------------------")
    print("Solving Heavy CVRPTW Network routing arrays...")
    print("---------------------------------------------------------")
    res = solve_cvrptw(data)
    
    if res.get("status") == "success":
        print(">>> SUCCESS! Route arrays natively structured bypassing ALL payload limits & chronological time-outs safely!\n")
        
        for r in res["routes"]:
            print(f"[{'='*40}]")
            print(f" VEHICLE {r['vehicle_id']} MANIFEST TRACKER")
            print(f"[{'='*40}]")
            print(f" Total Traversed: {r['distance']} km")
            
            # Warn if limits reached bounds closely safely evaluating capacities
            load_stat = f"{r['total_cargo_load']} / 40 kg Used"
            if r['total_cargo_load'] >= 35:
                load_stat += " ⚠️ (Heavy Load Expected)"
            print(f" Capacity Draw  : {load_stat}\n")
            
            print(f"  {'Action':<15} | {'Minute':<8} | {'Payload Action'}")
            print(f"  {'-'*45}")
            
            for node in r["route_timeline"]:
                node_name = f"Depot {node['node_index']}" if node['node_index'] == 0 else f"Target {node['node_index']}"
                print(f"  Arrived {node_name:<7} | At M {node['arrival_minute']:<5} | Unloaded {node['demand_unloaded']} kg")
            print("\n")
    else:
        print(f"\n[!] ALERT: ENGINE FAILURE! ")
        print(f"Reason: {res.get('error')}")

if __name__ == "__main__":
    main()
