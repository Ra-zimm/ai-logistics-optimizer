"""
Advanced Environment Simulation Matrix Overlays

Generates chronologically mapped and environmentally adjusted
physics mechanics directly to logistics networks. Completely decoupled 
from standard constraints targeting strictly external weather properties
and temporal Peak time traffic congestion sine-waves.
"""
import numpy as np

class AdvancedSimulationEngine:
    """
    Stateful discrete-event engine extending basic metrics into
    chronological Traffic Time-of-Day penalties and global Weather modifiers.
    """
    def __init__(self, base_distance_matrix: np.ndarray, weather_condition: str = "clear"):
        self.base_distance_matrix = base_distance_matrix.copy()
        
        # Valid physical states: 'clear', 'rain', 'snow', 'storm'
        self.weather_condition = weather_condition.lower()
        
        # Map physics universally 
        self.current_distance_matrix = self._apply_initial_weather(self.base_distance_matrix)
        
    def _apply_initial_weather(self, matrix: np.ndarray) -> np.ndarray:
        """
        Scales traversal boundaries natively adjusting map speed calculations globally.
        """
        weather_multipliers = {
            "clear": 1.0,
            "rain": 1.25, # 25% slower speeds
            "snow": 1.60, # 60% slower due to hazardous driving
            "storm": 2.20 # Severe hurricane-level delays
        }
        mult = weather_multipliers.get(self.weather_condition, 1.0)
        new_mat = matrix * mult
        return new_mat
        
    def apply_time_of_day_traffic(self, current_minute_of_day: int) -> np.ndarray:
        """
        Dynamically calculates edge penalties evaluating a standard 8-hour shift.
        Peak rush hours typically mathematically array out around 12:00PM (240 min) and 4:00PM (480 min).
        """
        import math
        
        # We will bound it mathematically tracking a sine wave logic.
        # x-axis normalized across pi space creating chronological rolling ripples mimicking actual city grids.
        normalized_time = (current_minute_of_day / 480.0) * math.pi * 2.5
        
        # Generate continuous harmonic wave delays over the hour
        traffic_wave = abs(math.sin(normalized_time)) 
        
        # Surge peaks represent a +50% delay factor during absolute rush hours
        surge_multiplier = 1.0 + (traffic_wave * 0.50)
        
        # Overwrite exactly onto active weather geometries
        surge_matrix = self.current_distance_matrix * surge_multiplier
        np.fill_diagonal(surge_matrix, 0.0)
        
        return surge_matrix
