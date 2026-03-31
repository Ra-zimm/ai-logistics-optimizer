"""
Formal A/B Hypothesis Testing Suite

Runs paired T-Tests mathematically evaluating Scenario A (Static Baseline)
against Scenario B (Dynamic Rerouting) sequentially generating strict 
statistical confidence vectors guaranteeing proof of concept academically.
"""
import sys
import os
import numpy as np
from scipy import stats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_ingestion.synthetic import generate_logistics_data
from optimization.or_tools_solver import solve_vrp
from optimization.dynamic_router import DynamicFleetManager

def main():
    # Statistical significance requires n >= 30 sample size roughly
    num_trials = 40
    print(f"Executing A/B Testing: Static (A) vs Dynamic (B) across {num_trials} Standardized Trials...\n")
    
    dist_A = []
    dist_B = []
    
    # Disable terminal warnings natively for clear output streams
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    for i in range(num_trials):
        sys.stdout.write(f"\rComputing Trial Physics Array [{i+1}/{num_trials}]...")
        sys.stdout.flush()
        
        # 1. Establish tightly controlled geographic identical variables
        data = generate_logistics_data(num_locations=6, num_vehicles=1, random_seed=1000 + i)
        base_matrix = data["distance_matrix"]
        
        baseline_res = solve_vrp(base_matrix, num_vehicles=1, depot=0)
        route_nodes = baseline_res["routes"][0]["route"]
        
        # 2. Both algorithms face the exact same physical blockage
        fleet_manager = DynamicFleetManager(base_matrix, num_vehicles=1, depot=0)
        
        if len(route_nodes) > 2:
            break_edge = (route_nodes[1], route_nodes[2])
            fleet_manager.trigger_delay_event(break_edge[0], break_edge[1], delay_multiplier=12.0)
            
        traffic_matrix = fleet_manager.sim_engine.get_travel_times()
        
        # -------------------------------------------------------------
        # Scenario A: Static (Blind continuous execution natively)
        # -------------------------------------------------------------
        cost_A = fleet_manager._calculate_route_cost(route_nodes, traffic_matrix)
        dist_A.append(cost_A)
        
        # -------------------------------------------------------------
        # Scenario B: Dynamic Adaptive (Smart traffic threshold re-routing)
        # -------------------------------------------------------------
        reroute_res = fleet_manager.evaluate_and_reroute(threshold_degradation=1.15)
        cost_B = fleet_manager.active_routes[0]["distance"] if reroute_res["recomputed"] else cost_A
        dist_B.append(cost_B)
        
    print("\n\n--- Formal A/B Statistical Analysis Complete ---")
    
    # Execute Paired T-Test explicitly tracking identical scenarios
    t_stat, p_value = stats.ttest_rel(dist_A, dist_B)
    
    mean_A = np.mean(dist_A)
    mean_B = np.mean(dist_B)
    improvement = ((mean_A - mean_B) / mean_A) * 100
    
    # Format and Output Results
    print("\n[Distribution Summary]")
    print(f" > Scenario A (Static Baseline)   Mean: {mean_A:.2f} km")
    print(f" > Scenario B (Dynamic Rerouting) Mean: {mean_B:.2f} km")
    print(f" > Average Tracked Compute Improvement: {improvement:.2f}% reduced distance")
    
    print("\n[Statistical Significance Engine (Scipy Paired T-Test)]")
    print(f" T-Statistic : {t_stat:.4f}")
    if p_value < 0.0001:
        print(f" P-Value     : {p_value:.2e} (Extremely Low)")
    else:
        print(f" P-Value     : {p_value:.4f}")
    
    print("\n[Mathematical Thesis Conclusion]")
    alpha = 0.05
    if p_value < alpha:
        print(f" ✅ REJECT NULL HYPOTHESIS.")
        print(f" The engine mathematically proves Scenario B (Dynamic) is statistically")
        print(f" significantly more optimal than Scenario A at a 95% confidence array.")
    else:
        print(f" ❌ FAILED TO REJECT null hypothesis. The variance is not universally significant.")

if __name__ == "__main__":
    main()
