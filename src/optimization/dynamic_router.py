"""
Dynamic Routing Manager

Handles the orchestration of the OR-Tools baseline solver alongside the 
discrete-event simulation engine. 

Facilitates 'minimal recomputation' by strictly recalculating routes *only* 
when simulated delay thresholds are breached, comparing the old configurations 
against newly optimized routes.
"""

from typing import Dict, Any, List
from .or_tools_solver import solve_vrp
import sys
import os

# Adjust pathing so relative internal imports hook correctly
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from simulation.engine import LogisticsSimulationEngine


class DynamicFleetManager:
    def __init__(self, initial_distance_matrix: list, num_vehicles: int, depot: int = 0):
        self.num_vehicles = num_vehicles
        self.depot = depot
        self.sim_engine = LogisticsSimulationEngine(initial_distance_matrix)
        
        # 1. Determine the initial global baseline routes before any dynamic events
        resolution = solve_vrp(initial_distance_matrix, num_vehicles, depot)
        self.active_routes = resolution.get("routes", [])
        
    def trigger_delay_event(self, node_a: int, node_b: int, delay_multiplier: float):
        """Injects a dynamic roadblock into the environment engine."""
        self.sim_engine.inject_road_block(node_a, node_b, delay_multiplier)
        
    def evaluate_and_reroute(self, threshold_degradation: float = 1.2) -> Dict[str, Any]:
        """
        Evaluate if current active routes have significantly degraded due to events.
        If they have, perform a 'minimal recomputation' by strictly calling the OR-Tools 
        solver *only* when the threshold is breached.
        """
        current_matrix = self.sim_engine.get_travel_times()
        results = {"recomputed": False, "reports": []}
        
        needs_reroute = False
        
        # --- LOGIC: Minimal Recomputation --- 
        # Instead of constantly running heavy ML or exact OR-Tools solvers universally on a loop, 
        # we passively evaluate standard linear array traversals over the baseline node plan. 
        # We only pay the expensive computational cost to mathematically re-solve the network
        # if the lightweight `check_reroute_needed` function flags a severe penalty.
        for route_info in self.active_routes:
            if self.sim_engine.check_reroute_needed(route_info["route"], threshold_degradation):
                needs_reroute = True
                break
                
        if needs_reroute:
            results["recomputed"] = True
            
            # Re-solve the VRP utilizing the inflated traffic distance matrix
            new_resolution = solve_vrp(current_matrix, self.num_vehicles, self.depot)
            new_routes = new_resolution.get("routes", [])
            
            # --- LOGIC: Compare Old vs New ---
            # Evaluate how the old node arrangements would have fared under the new
            # traffic constraints compared to the newly structured routes.
            for old_r, new_r in zip(self.active_routes, new_routes):
                traffic_cost_old_path = self._calculate_route_cost(old_r["route"], current_matrix)
                
                report = {
                    "vehicle_id": old_r["vehicle_id"],
                    "old_route": old_r["route"],
                    "new_route": new_r["route"],
                    "changed": old_r["route"] != new_r["route"],
                    "old_cost_under_traffic": traffic_cost_old_path,
                    "new_optimized_cost": new_r["distance"]
                }
                results["reports"].append(report)
            
            # Update the fleet's active paths to the recovered paths
            self.active_routes = new_routes
            
        return results

    def _calculate_route_cost(self, route: List[int], matrix) -> float:
        """Helper to compute exact cost of an array of nodes over a traffic matrix."""
        cost = 0.0
        for i in range(len(route) - 1):
            cost += matrix[route[i]][route[i+1]]
        return round(cost, 2)
