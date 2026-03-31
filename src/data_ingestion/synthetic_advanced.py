"""
Advanced Synthetic Data Generator (CVRPTW)

Generates physical restrictions required for deeper operational thesis studies:
- Node Demand (package weights)
- Maximum Vehicle Capacity
- Rigid Delivery Time Windows (Opening / Closing boundaries)
"""
import numpy as np
from typing import Dict, Any

def haversine_vectorized(latA, lonA, latB, lonB):
    R = 6371.0 # km
    latA, lonA = np.radians(latA), np.radians(lonA)
    latB, lonB = np.radians(latB), np.radians(lonB)
    dlat = latB - latA
    dlon = lonB - lonA
    a = np.sin(dlat / 2)**2 + np.cos(latA) * np.cos(latB) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c

def generate_cvrptw_data(
    num_locations: int = 15,
    num_vehicles: int = 4,
    vehicle_capacity: int = 40,
    bounding_box: tuple = (40.70, -74.05, 40.85, -73.90),
    random_seed: int = 42
) -> Dict[str, Any]:
    
    np.random.seed(random_seed)
    
    min_lat, min_lon, max_lat, max_lon = bounding_box
    total_nodes = num_locations + 1
    
    lats = np.random.uniform(min_lat, max_lat, total_nodes)
    lons = np.random.uniform(min_lon, max_lon, total_nodes)
    nodes = np.column_stack((lats, lons))
    
    # Distance Computations
    lats_row = lats[:, np.newaxis]
    lons_row = lons[:, np.newaxis]
    lats_col = lats[np.newaxis, :]
    lons_col = lons[np.newaxis, :]
    
    distance_matrix = haversine_vectorized(lats_row, lons_row, lats_col, lons_col)
    distance_matrix = np.round(distance_matrix, 2)
    np.fill_diagonal(distance_matrix, 0.0)
    
    # ----------------------------------------------------
    # Constraint 1: Payload Demands
    # ----------------------------------------------------
    # Generating between 3 and 15 cargo packages per destination
    demands = np.random.randint(3, 15, size=total_nodes).tolist()
    demands[0] = 0 # Depot mechanically demands absolutely 0 cargo
    
    vehicle_capacities = [vehicle_capacity] * num_vehicles
    
    # ----------------------------------------------------
    # Constraint 2: Operating Time Windows
    # ----------------------------------------------------
    # Assuming standard daily execution shift of exactly 8 hours total duration (480 computational minutes).
    # The depot remains entirely accessible consistently the full duration.
    time_windows = [(0, 480)]
    
    for _ in range(num_locations):
        # Delivery sites mandate strict arrival brackets randomly throughout the day (guaranteeing 2-3 hour open slots)
        start_min = np.random.randint(0, 300) 
        end_min = start_min + np.random.randint(120, 180)
        # Cap securely to daily limit of 480 explicitly
        end_min = min(end_min, 480)
        time_windows.append((int(start_min), int(end_min)))
        
    return {
        "depot": nodes[0],
        "locations": nodes[1:],
        "all_nodes": nodes,
        "distance_matrix": distance_matrix,
        "num_vehicles": num_vehicles,
        "demands": demands,
        "vehicle_capacities": vehicle_capacities,
        "time_windows": time_windows
    }
