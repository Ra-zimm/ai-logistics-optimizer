import numpy as np
from typing import Dict, List, Any, Tuple

class LogisticsSimulationEngine:
    """
    Simulation Engine for Logistics Routing Environments.
    
    Provides a stateful environment to simulate traffic delays, dynamic events 
    (like roadblocks), and compute the need for vehicle re-routing in real-time.
    """
    def __init__(self, base_distance_matrix: np.ndarray, random_seed: int = 42):
        """
        Initializes the simulation engine with a baseline distance matrix.
        """
        # Ensure deep copies to avoid modifying original ingested data
        self.base_distance_matrix = np.array(base_distance_matrix, dtype=float)
        self.current_distance_matrix = np.array(base_distance_matrix, dtype=float)
        
        self.simulated_time = 0.0
        self.random_state = np.random.RandomState(random_seed)
        self.active_events: List[Dict[str, Any]] = []
        
    def reset(self) -> np.ndarray:
        """Resets the simulation entirely to the baseline state."""
        self.current_distance_matrix = self.base_distance_matrix.copy()
        self.simulated_time = 0.0
        self.active_events.clear()
        return self.current_distance_matrix
        
    def advance_time(self, time_increment: float):
        """Advances the simulation clock (can be used to expire old road blocks later)."""
        self.simulated_time += time_increment
        
    def inject_traffic_delay(self, severity_max: float = 0.20) -> np.ndarray:
        """
        Simulates city-wide traffic by randomly increasing travel distances/times 
        across the board.
        
        Args:
            severity_max: The maximum percentage increase (e.g. 0.20 = up to 20% delay).
        Returns:
            The updated distance matrix.
        """
        shape = self.current_distance_matrix.shape
        
        # Generate random multiplicative noise matrix
        noise = self.random_state.uniform(1.0, 1.0 + severity_max, shape)
        
        # Ensure distance noise is symmetric (A to B is delayed same as B to A mostly)
        noise = (noise + noise.T) / 2.0
        np.fill_diagonal(noise, 1.0)
        
        self.current_distance_matrix *= noise
        
        self.active_events.append({
            "type": "GLOBAL_TRAFFIC",
            "severity_max": severity_max,
            "time": self.simulated_time
        })
        return self.current_distance_matrix
        
    def inject_road_block(self, node_a: int, node_b: int, delay_multiplier: float = 5.0) -> np.ndarray:
        """
        Simulates a specific dynamic event like a road block or accident 
        significantly impacting a specific routing edge.
        """
        original_dist = self.base_distance_matrix[node_a, node_b]
        new_dist = original_dist * delay_multiplier
        
        # Update both directions
        self.current_distance_matrix[node_a, node_b] = new_dist
        self.current_distance_matrix[node_b, node_a] = new_dist
        
        self.active_events.append({
            "type": "ROAD_BLOCK",
            "edge": (node_a, node_b),
            "original_cost": original_dist,
            "new_cost": new_dist,
            "time": self.simulated_time
        })
        
        return self.current_distance_matrix

    def get_travel_times(self) -> np.ndarray:
        """Retrieves the current dynamic state of the routing matrix."""
        return self.current_distance_matrix
        
    def check_reroute_needed(self, vehicle_route: List[int], threshold_degradation: float = 1.2) -> bool:
        """
        Checks if a specific vehicle's route has degraded significantly compared to the 
        baseline expectation, signaling that a re-solve by OR-Tools is required.
        
        Args:
            vehicle_route: Sequence of node indices representing the current route plan.
            threshold_degradation: 1.2 implies if the active route is 20% slower than 
                                    expected, return True.
        """
        baseline_cost = 0.0
        current_cost = 0.0
        
        # Evaluate cost traversing the planned edges
        for i in range(len(vehicle_route) - 1):
            u, v = vehicle_route[i], vehicle_route[i+1]
            baseline_cost += self.base_distance_matrix[u, v]
            current_cost += self.current_distance_matrix[u, v]
            
        if baseline_cost == 0:
            return False
            
        degradation = current_cost / baseline_cost
        return degradation > threshold_degradation
