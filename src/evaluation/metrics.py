"""
Evaluation Metrics for Route Optimization.

Provides standardized comparison metrics across all solver algorithms:
- Total Distance Traveled
- Delivery Time / Lateness 
- Fuel / Operational Cost Estimate
- Number of Dynamic Delays Handled
"""
from typing import Dict, Any, List

def calculate_delivery_time(distance_km: float, average_speed_kmh: float = 40.0) -> float:
    """Returns estimated continuous delivery traversal time in hours."""
    return distance_km / average_speed_kmh

def calculate_fuel_estimate(
    distance_km: float, 
    liters_per_100km: float = 12.0, 
    fuel_price_per_liter: float = 1.50
) -> Dict[str, float]:
    """Returns fuel consumed (L) and overall estimated cost ($) for a routing track."""
    fuel_used = (distance_km / 100.0) * liters_per_100km
    cost = fuel_used * fuel_price_per_liter
    return {"liters": round(fuel_used, 2), "cost_usd": round(cost, 2)}

def evaluate_route_plan(method_name: str, distance_km: float, num_delays_handled: int = 0) -> Dict[str, Any]:
    """
    Standardized evaluation dictionary generating all tracked metrics for comparing algorithms.
    """
    delivery_time = calculate_delivery_time(distance_km)
    fuel_stats = calculate_fuel_estimate(distance_km)
    
    return {
        "method": method_name,
        "total_distance_km": round(distance_km, 2),
        "delivery_time_hours": round(delivery_time, 2),
        "fuel_consumed_L": fuel_stats["liters"],
        "estimated_fuel_cost": fuel_stats["cost_usd"],
        "delays_handled": num_delays_handled
    }

def print_comparison_report(evaluations: List[Dict[str, Any]]):
    """Formats a structured master analytics report to standard terminal outputs."""
    print(f"\n{'='*75}")
    print(f"{'routing algorithm master comparison report'.upper():^75}")
    print(f"{'='*75}")
    print(f"{'Algorithm Method':<22} | {'Dist (km)':<10} | {'Time (h)':<9} | {'Fuel Cost':<10} | {'Delays':<6}")
    print(f"{'-'*75}")
    for eval in evaluations:
        print(f"{eval['method']:<22} | {eval['total_distance_km']:<10.2f} | {eval['delivery_time_hours']:<9.2f} | "
              f"${eval['estimated_fuel_cost']:<9.2f} | {eval['delays_handled']:<6}")
    print(f"{'='*75}\n")
