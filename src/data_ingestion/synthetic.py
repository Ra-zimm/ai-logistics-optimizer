import numpy as np
from typing import Dict, Any

def haversine_vectorized(latA, lonA, latB, lonB):
    """
    Vectorized Haversine distance calculator for generating a distance matrix.
    Input shapes are broadcast against each other.
    Returns distance in kilometers.
    """
    R = 6371.0  # Earth radius in km
    
    # Convert degrees to radians
    latA, lonA = np.radians(latA), np.radians(lonA)
    latB, lonB = np.radians(latB), np.radians(lonB)
    
    dlat = latB - latA
    dlon = lonB - lonA
    
    a = np.sin(dlat / 2)**2 + np.cos(latA) * np.cos(latB) * np.sin(dlon / 2)**2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    
    return R * c

def generate_logistics_data(
    num_locations: int = 15,
    num_vehicles: int = 3,
    bounding_box: tuple = (40.70, -74.05, 40.85, -73.90), # e.g. NYC area bounds
    random_seed: int = 42
) -> Dict[str, Any]:
    """
    Generates synthetic logistics data including a depot, delivery locations, and a distance matrix.
    
    Args:
        num_locations: Number of delivery locations (excluding depot).
        num_vehicles: Number of available vehicles.
        bounding_box: Tuple of (min_lat, min_lon, max_lat, max_lon) for coordinate generation.
        random_seed: Random seed for reproducibility.
        
    Returns:
        A dictionary containing depot coordinates, locations, distance matrix, and vehicle count.
    """
    # Enforce reproducibility
    np.random.seed(random_seed)
    
    min_lat, min_lon, max_lat, max_lon = bounding_box
    total_nodes = num_locations + 1  # 1 Depot + delivery locations
    
    # Generate random Latitudes and Longitudes
    lats = np.random.uniform(min_lat, max_lat, total_nodes)
    lons = np.random.uniform(min_lon, max_lon, total_nodes)
    
    nodes = np.column_stack((lats, lons))
    
    # Compute Distance Matrix using broadcasting
    lats_row = lats[:, np.newaxis]
    lons_row = lons[:, np.newaxis]
    lats_col = lats[np.newaxis, :]
    lons_col = lons[np.newaxis, :]
    
    distance_matrix = haversine_vectorized(lats_row, lons_row, lats_col, lons_col)
    
    # Round distances to 2 decimal places for realism and zero-out the diagonal
    distance_matrix = np.round(distance_matrix, 2)
    np.fill_diagonal(distance_matrix, 0.0)
    
    return {
        "depot": nodes[0],
        "locations": nodes[1:],
        "all_nodes": nodes,
        "distance_matrix": distance_matrix,
        "num_vehicles": num_vehicles
    }
