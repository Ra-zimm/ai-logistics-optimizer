"""
Batch Simulation Benchmark Runner

Systematically evaluates Static OR-Tools, Dynamic Engine Rerouting, 
and RL Policy architectures over N unique, randomized geographic routing scenarios.
Aggregates standardized operational metrics structurally into a compiled DataFrame/CSV.
"""
import sys
import os
import pandas as pd
import numpy as np

# Bind core routing architectural endpoints
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_ingestion.synthetic import generate_logistics_data
from optimization.or_tools_solver import solve_vrp
from optimization.dynamic_router import DynamicFleetManager
from optimization.rl_agent import evaluate_routing_agent, train_routing_agent
from evaluation.metrics import evaluate_route_plan

def main():
    num_runs = 20
    records = []
    
    print(f"Starting Global Batch Benchmark Simulation for {num_runs} separate environments...\n")
    
    # Supress deep native stable-baselines3 standard out calls entirely while looping
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    
    for run_id in range(num_runs):
        sys.stdout.write(f"\rExecuting Parallel Simulation Event [{run_id+1}/{num_runs}]...")
        sys.stdout.flush()
        
        # 1. Spin up native unique environment matrices for every individual run loop
        data = generate_logistics_data(num_locations=6, num_vehicles=1, random_seed=100 + run_id)
        base_matrix = data["distance_matrix"]
        
        # 2. Extract Baseline Layouts
        baseline_res = solve_vrp(base_matrix, num_vehicles=1, depot=0)
        baseline_ideal_nodes = baseline_res["routes"][0]["route"]
        
        # 3. Formulate heavily penalized dynamic traffic flows using exact engine mechanics
        fleet_manager = DynamicFleetManager(base_matrix, num_vehicles=1, depot=0)
        if len(baseline_ideal_nodes) > 2:
            break_edge = (baseline_ideal_nodes[1], baseline_ideal_nodes[2])
            fleet_manager.trigger_delay_event(break_edge[0], break_edge[1], delay_multiplier=12.0)
            
        traffic_matrix = fleet_manager.sim_engine.get_travel_times()
        
        # --- TEST 1: STATIC BASELINE (BLIND) ---
        blind_cost = fleet_manager._calculate_route_cost(baseline_ideal_nodes, traffic_matrix)
        base_eval = evaluate_route_plan("Static Baseline", blind_cost, 0)
        base_eval["Run_ID"] = run_id
        records.append(base_eval)
        
        # --- TEST 2: DYNAMIC REROUTING MANAGER ---
        reroute_res = fleet_manager.evaluate_and_reroute(threshold_degradation=1.1)
        dynamic_dist = fleet_manager.active_routes[0]["distance"] if reroute_res["recomputed"] else blind_cost
        dyn_delays = 1 if reroute_res["recomputed"] else 0
        
        dyn_eval = evaluate_route_plan("Dynamic Router", dynamic_dist, dyn_delays)
        dyn_eval["Run_ID"] = run_id
        records.append(dyn_eval)
        
        # --- TEST 3: MACHINE LEARNING PPO AGENT ---
        # Short micro-epoch training parameters mapped directly onto the matrix framework
        rl_model, _ = train_routing_agent(base_matrix, total_timesteps=2000)
        rl_res = evaluate_routing_agent(rl_model, base_matrix)
        
        rl_eval = evaluate_route_plan("RL Policy (PPO)", rl_res["total_distance"], 0)
        rl_eval["Run_ID"] = run_id
        records.append(rl_eval)
        
    print("\n\nGlobal Batch Loop Complete. Compiling Structured Targets...")
    
    # Translate python Dictionary structures perfectly into mathematical analytical DataFrames
    df = pd.DataFrame(records)
    
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/processed/benchmark_results.csv'))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ Successfully preserved 60 explicit multi-metric operational records into:\n -> {output_path}")
    
    # Render explicit statistical data aggregates
    summary = df.groupby("method").agg({
        "total_distance_km": "mean",
        "delivery_time_hours": "mean",
        "delays_handled": "mean"
    }).reset_index()
    
    print("\n====== MASTER AGGREGATE MEAN RESULTS (20 Runs) ======")
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
