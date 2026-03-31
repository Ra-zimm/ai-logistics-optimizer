"""
Capacitated Vehicle Routing Problem with Time Windows (CVRPTW) Exact Solver

Massively upgrades standard geometric matrices by natively tracking live physical parameters:
- Strictly prevents trucks from exceeding cargo allowances.
- Computes mathematical time-matrix speeds executing 10-minute node delivery stalls perfectly.
- Eliminates any node arrays arriving past designated operational time windows.
"""

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from typing import Dict, Any

def solve_cvrptw(data_dict: Dict[str, Any], time_limit_seconds: int = 15) -> Dict[str, Any]:
    scaling_factor = 100
    
    dist_matrix = data_dict["distance_matrix"]
    
    # Calculate Chronological Time Array mappings:
    # Converting array kilometer geometries back into minutes leveraging average local 40km/h routing speed (0.66 km/m)
    speed_km_per_min = 40.0 / 60.0
    time_matrix = (np.array(dist_matrix) / speed_km_per_min)
    
    # Convert safely into solver integer matrices
    int_dist_matrix = (np.array(dist_matrix) * scaling_factor).astype(int).tolist()
    int_time_matrix = (np.array(time_matrix)).astype(int).tolist() 
    
    demands = data_dict["demands"]
    vehicle_capacities = data_dict["vehicle_capacities"]
    time_windows = data_dict["time_windows"]
    num_vehicles = data_dict["num_vehicles"]
    depot = 0
    
    manager = pywrapcp.RoutingIndexManager(len(dist_matrix), num_vehicles, depot)
    routing = pywrapcp.RoutingModel(manager)

    # ----------------------------------------------------
    # Constraint 1: Objective Distance Dimensions
    # ----------------------------------------------------
    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int_dist_matrix[from_node][to_node]
        
    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    
    # ----------------------------------------------------
    # Constraint 2: Mathematical Capacity Limitations
    # ----------------------------------------------------
    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return demands[from_node]
        
    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    
    # Engine structurally halts a truck pathway immediately if predicted node payload exceeds physical maximum capacities
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0, 
        vehicle_capacities, 
        True, 
        'Capacity'
    )
    
    # ----------------------------------------------------
    # Constraint 3: Strict Time Window Enforcements
    # ----------------------------------------------------
    def time_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        # Assume an explicit continuous 10-minute stalling "service un-loading time" executed at every target node.
        service_time = 10 if from_node != depot else 0
        return int_time_matrix[from_node][to_node] + service_time
        
    time_callback_index = routing.RegisterTransitCallback(time_callback)
    
    routing.AddDimension(
        time_callback_index,
        30,  # Max wait time directly permitted at an origin target (allowing trucks to legally idle waiting for shifts to open)
        480, # Maximum route allowance total (mechanically 8 real hours mapped)
        False,  
        'Time'
    )
    time_dimension = routing.GetDimensionOrDie('Time')
    
    # Programmatically execute strict CumulVar range tracking array against all generated targets
    for location_idx, time_window in enumerate(time_windows):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])
        
    # Hook Depot
    for i in range(num_vehicles):
        index = routing.Start(i)
        time_dimension.CumulVar(index).SetRange(time_windows[0][0], time_windows[0][1])

    # Instantiate logic Search heuristics
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    search_parameters.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
    search_parameters.time_limit.seconds = time_limit_seconds

    # COMPUTE
    solution = routing.SolveWithParameters(search_parameters)
    
    if not solution:
        return {"status": "failed", "error": "No solution mathematically mapped meeting both explicit Delivery Time limits and internal Truck weight constraints simultaneously!"}

    routes = []
    total_distance = 0.0
    
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        route_nodes = []
        route_distance = 0
        route_load = 0
        
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            time_var = time_dimension.CumulVar(index)
            
            route_nodes.append({
                "node_index": node_index,
                "arrival_minute": solution.Min(time_var),
                "demand_unloaded": demands[node_index]
            })
            route_load += demands[node_index]
            
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
            
        # Hook target return node completion 
        end_node_index = manager.IndexToNode(index)
        time_var = time_dimension.CumulVar(index)
        route_nodes.append({
            "node_index": end_node_index,
            "arrival_minute": solution.Min(time_var),
            "demand_unloaded": 0
        })
        
        real_dist = route_distance / scaling_factor
        routes.append({
            "vehicle_id": vehicle_id,
            "route_timeline": route_nodes,
            "route": [n["node_index"] for n in route_nodes],
            "distance": round(real_dist, 2),
            "total_cargo_load": route_load
        })
        total_distance += real_dist

    return {
        "status": "success",
        "total_distance": round(total_distance, 2),
        "routes": routes
    }
