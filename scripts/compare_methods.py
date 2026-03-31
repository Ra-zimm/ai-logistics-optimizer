"""
Cross-domain routing algorithm comparison suite.

Calculates identical node graphs across baseline exact solvers, 
dynamic reaction handlers, and neural network reinforcement agents.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_ingestion.synthetic import generate_logistics_data
from optimization.or_tools_solver import solve_vrp
from optimization.dynamic_router import DynamicFleetManager
from optimization.rl_agent import evaluate_routing_agent, train_routing_agent
from evaluation.metrics import evaluate_route_plan, print_comparison_report

def main():
    evaluations = []
    
    print("\n[Step 1] Initializing Universal Sandbox Scenario...")
    data = generate_logistics_data(num_locations=6, num_vehicles=1, random_seed=42)
    base_matrix = data["distance_matrix"]
    
    # ---------------------------------------------------------
    # System A: Baseline OR-Tools (Static)
    # ---------------------------------------------------------
    print("[Step 2] Processing Baseline OR-Tools...")
    baseline_res = solve_vrp(base_matrix, num_vehicles=1, depot=0)
    baseline_ideal_nodes = baseline_res["routes"][0]["route"]
    
    # ---------------------------------------------------------
    # System B: Dynamic Fleet Manager
    # ---------------------------------------------------------
    print("[Step 3] Booting Active Simulation Matrix & Injecting massive Roadblock...")
    fleet_manager = DynamicFleetManager(base_matrix, num_vehicles=1, depot=0)
    
    # Heavily block the most useful edge in their current path
    if len(baseline_ideal_nodes) > 2:
        break_edge = (baseline_ideal_nodes[1], baseline_ideal_nodes[2])
        fleet_manager.trigger_delay_event(break_edge[0], break_edge[1], delay_multiplier=15.0)

    # Capture what the baseline OR-tools would have suffered blindly pushing through:
    inflated_matrix = fleet_manager.sim_engine.get_travel_times()
    blind_cost = fleet_manager._calculate_route_cost(baseline_ideal_nodes, inflated_matrix)
    evaluations.append(evaluate_route_plan("Static OR-Tools (Blind)", blind_cost, 0))

    # Calculate the dynamically adapted detour cost
    reroute_res = fleet_manager.evaluate_and_reroute(threshold_degradation=1.1)
    dynamic_dist = fleet_manager.active_routes[0]["distance"] if reroute_res["recomputed"] else blind_cost
    delays_fixed = 1 if reroute_res["recomputed"] else 0
    evaluations.append(evaluate_route_plan("Dynamic Router", dynamic_dist, delays_fixed))
    
    # ---------------------------------------------------------
    # System C: PPO Reinforcement Learning
    # ---------------------------------------------------------
    print("[Step 4] Training Reinforcement Array (Fast convergence)...")
    # Quick low-epoch train to demonstrate execution on the baseline map
    rl_model, _ = train_routing_agent(base_matrix, total_timesteps=8000)
    rl_res = evaluate_routing_agent(rl_model, base_matrix)
    evaluations.append(evaluate_route_plan("RL Policy (Baseline Map)", rl_res["total_distance"], 0))

    # Final Output
    print_comparison_report(evaluations)

if __name__ == "__main__":
    main()
