"""
Vehicle Routing Problem (VRP) Solver using Google OR-Tools.

Provides a robust, exact solver baseline for optimizing vehicle routes
where the primary objective is minimizing total fleet distance.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from typing import Dict, Any, List, Union

def solve_vrp(
    distance_matrix: Union[List[List[float]], np.ndarray], 
    num_vehicles: int, 
    depot: int = 0,
    time_limit_seconds: int = 5
) -> Dict[str, Any]:
    """
    Solves the Vehicle Routing Problem (VRP) to minimize total distance across all vehicles.
    
    Args:
        distance_matrix: 2D array indicating travel costs (distances) between nodes.
        num_vehicles: Number of vehicles available for the routes.
        depot: The starting and ending node index for all vehicles (usually 0).
        time_limit_seconds: Maximum computation time allowed for heuristic search.
        
    Returns:
        A dictionary containing the total optimized distance and a breakdown of 
        the exact nodes visited by each vehicle.
    """
    
    # OR-Tools routing module requires integer values for constraints.
    # We defensively scale up floating point kilometer calculations (like Haversine coords)
    # to preserve decimal level precision before running the integer solver.
    scaling_factor = 100
    
    # Generate scaled integer distance matrix
    int_matrix = np.array(distance_matrix) * scaling_factor
    int_matrix = int_matrix.astype(int).tolist()
    
    data = {
        'distance_matrix': int_matrix,
        'num_vehicles': num_vehicles,
        'depot': depot
    }

    # 1. Initialize the Routing Index Manager and Model
    manager = pywrapcp.RoutingIndexManager(
        len(data['distance_matrix']),
        data['num_vehicles'], 
        data['depot']
    )
    
    routing = pywrapcp.RoutingModel(manager)

    # 2. Define the Distance Callback
    def distance_callback(from_index, to_index):
        """Returns the scaled distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    # Register the callback with the routing engine
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)

    # 3. Define the Cost Objective Function
    # We want to minimize the total travel costs evaluated using the distance callback
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)


    # 4. Search parameters Configuration
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )
    # Using Guided Local Search as the metaheuristic for a robust baseline globally
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    )
    search_parameters.time_limit.seconds = time_limit_seconds

    # 5. Solve the Model
    solution = routing.SolveWithParameters(search_parameters)

    # 6. Extract solutions to structured Python Dictionary
    if not solution:
        return {"status": "failed", "error": "No solution found by OR-Tools."}

    routes = []
    total_distance = 0.0

    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route_nodes = []
        route_distance = 0
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_nodes.append(node_index)
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            # Keep sum
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        # Append target depot node to complete the loop
        route_nodes.append(manager.IndexToNode(index))
        # Descend scale factor back to real floating point kms
        real_route_dist = route_distance / scaling_factor
        
        routes.append({
            "vehicle_id": vehicle_id,
            "route": route_nodes,
            "distance": real_route_dist
        })
        
        total_distance += real_route_dist

    return {
        "status": "success",
        "total_distance": round(total_distance, 2),
        "routes": routes
    }
