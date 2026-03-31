"""
Reinforcement Learning Environment for Vehicle Route Optimization.

Implements a standard Gymnasium interface allowing Stable-Baselines3 agents 
to interact with the routing problem. 
State: Dictionary of Current Node and Visited location mask.
Action: Discrete choice of the next location.
Reward: Negative Distance per step (minimization objective).
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np

class RouteOptimizationEnv(gym.Env):
    metadata = {'render.modes': ['console']}

    def __init__(self, distance_matrix: np.ndarray, depot: int = 0):
        super(RouteOptimizationEnv, self).__init__()
        
        self.distance_matrix = np.array(distance_matrix, dtype=float)
        self.num_nodes = self.distance_matrix.shape[0]
        self.depot = depot
        
        # Action space: choice of next node to travel to
        self.action_space = spaces.Discrete(self.num_nodes)
        
        # Observation space: 
        # - current_node: Discrete scalar indicating where the truck is
        # - visited: Binary array indicating which locations are fully served
        self.observation_space = spaces.Dict({
            "current_node": spaces.Discrete(self.num_nodes),
            "visited": spaces.MultiBinary(self.num_nodes)
        })
        
        # Internal state
        self.current_node = self.depot
        self.visited = np.zeros(self.num_nodes, dtype=int)
        self.visited[self.depot] = 1
        self.route = [self.depot]
        self.total_distance = 0.0

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_node = self.depot
        self.visited = np.zeros(self.num_nodes, dtype=int)
        self.visited[self.depot] = 1
        self.route = [self.depot]
        self.total_distance = 0.0
        
        return self._get_obs(), self._get_info()

    def _get_obs(self):
        return {
            # Must cast scalar strictly to type required by gymnasium
            "current_node": int(self.current_node), 
            "visited": self.visited.copy().astype(np.int8) # MultiBinary typically requires int8 arrays
        }
        
    def _get_info(self):
        return {"route": self.route, "total_distance": self.total_distance}

    def step(self, action):
        action = int(action)
        reward = 0.0
        terminated = False
        truncated = False
        
        # 1. Check for Invalid Actions (already visited node)
        if self.visited[action] == 1:
            # Check edge case: The only valid "re-visit" is going back to the depot at the very end
            if action == self.depot and np.sum(self.visited) == self.num_nodes:
                dist = self.distance_matrix[self.current_node, action]
                self.total_distance += dist
                self.route.append(action)
                self.current_node = action
                # Excellent reward behavior: finalize cleanly with negative distance
                reward = -dist
                terminated = True
            else:
                # Invalid move: Massive penalty to discourage visiting same nodes, ends episode to prevent loops
                reward = -1000.0  
                terminated = True
        else:
            # 2. Valid Actions (Visiting a new active node)
            dist = self.distance_matrix[self.current_node, action]
            self.total_distance += dist
            self.route.append(action)
            self.visited[action] = 1
            self.current_node = action
            
            # Formulate core RL objective: Minimize geographic distance
            reward = -dist
            
        info = self._get_info()
        return self._get_obs(), reward, terminated, truncated, info
