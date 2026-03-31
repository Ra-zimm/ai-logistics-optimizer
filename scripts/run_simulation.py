"""
Logistics Simulation Main Pipeline

Creates an active logistics network, assigns baseline Vehicle Routes via 
OR-Tools, injects a severe roadblock event, and tests the dynamic 
minimal-recomputation rerouter.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_ingestion.synthetic import generate_logistics_data
from optimization.dynamic_router import DynamicFleetManager

def main():
    print("--------------------------------------------------")
    print("1. Generating Synthetic Delivery Network...")
    print("--------------------------------------------------")
    # Using a fixed seed for explicit roadblock replication testing
    data = generate_logistics_data(num_locations=12, num_vehicles=2, random_seed=42)
    
    print("\n--------------------------------------------------")
    print("2. Initializing Fleet & Calculating Baseline Routes...")
    print("--------------------------------------------------")
    fleet_manager = DynamicFleetManager(
        initial_distance_matrix=data["distance_matrix"], 
        num_vehicles=data["num_vehicles"], 
        depot=0
    )
    
    # Intentionally finding a node pair that is currently utilized in the live plan
    example_path_edge = (None, None)
    for r in fleet_manager.active_routes:
        print(f"Vehicle {r['vehicle_id']} Baseline: {r['route']} | Distance: {r['distance']}km")
        if len(r['route']) > 2 and example_path_edge[0] is None:
            example_path_edge = (r['route'][1], r['route'][2])
    
    print("\n--------------------------------------------------")
    print(f"3. Simulating Major Roadblock on active edge {example_path_edge[0]} <-> {example_path_edge[1]}")
    print("--------------------------------------------------")
    fleet_manager.trigger_delay_event(example_path_edge[0], example_path_edge[1], delay_multiplier=15.0)
    
    print("\n--------------------------------------------------")
    print("4. Evaluating Route Degradation against 20% Tolerance...")
    print("--------------------------------------------------")
    # Will mathematically only trigger computationally heavy OR-Tools
    # if the new matrix degradation disrupts the baseline expectation by 20%.
    reroute_results = fleet_manager.evaluate_and_reroute(threshold_degradation=1.2)
    
    if reroute_results["recomputed"]:
        print(">>> REROUTE TRIGGERED! System identified a massive penalty bottleneck.")
        for report in reroute_results["reports"]:
            if report["changed"]:
                print(f"\n[Vehicle {report['vehicle_id']} Adapted Target Plan]")
                print(f"   Old Node Plan: {report['old_route']}")
                print(f"      Cost trapped in traffic : {report['old_cost_under_traffic']} km expected")
                print(f"   New Node Plan: {report['new_route']}")
                print(f"      Cost actively rerouted  : {report['new_optimized_cost']} km optimal")
            else:
                print(f"\n[Vehicle {report['vehicle_id']} Maintained Plan]")
                print("   Roadblock did not intersect their path.")
    else:
        print(">>> No re-route needed. Delay was mathematically insignificant to global optimal.")

if __name__ == "__main__":
    main()
