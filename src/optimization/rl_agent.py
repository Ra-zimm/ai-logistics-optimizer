"""
Reinforcement Learning Agent Handler using Stable-Baselines3.

Wraps the initial synthetic distance matrices and trains a standard 
Proximal Policy Optimization (PPO) model over the custom Route Optimization environment.
"""

import numpy as np
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from .rl_env import RouteOptimizationEnv

def train_routing_agent(distance_matrix: np.ndarray, total_timesteps: int = 50000):
    """
    Instantiates and trains a PPO algorithm natively supporting multi-input dict environments.
    """
    env = RouteOptimizationEnv(distance_matrix, depot=0)
    
    # Gym Environment Validation check structurally required by SB3
    check_env(env, warn=True)
    
    # We utilize MultiInputPolicy since the observation space is a Gymnasium Dict
    model = PPO("MultiInputPolicy", env, verbose=0, learning_rate=0.001)
    
    print(f"Beginning PPO Model Training for {total_timesteps} iterations...")
    model.learn(total_timesteps=total_timesteps)
    print("Training Completed.")
    
    return model, env

def evaluate_routing_agent(model, distance_matrix: np.ndarray):
    """
    Deterministically evaluates a trained routing model over its specific map.
    """
    env = RouteOptimizationEnv(distance_matrix, depot=0)
    obs, info = env.reset()
    terminated = False
    
    # Secure tracking to prevent infinite loops mechanically during deterministic inference
    max_steps = len(distance_matrix) + 2 
    step_count = 0
    
    while not terminated and step_count < max_steps:
        # Utilizing explicit deterministic behavior for actual inference mapping
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        step_count += 1
        
    return info
