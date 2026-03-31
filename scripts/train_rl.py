"""
Script to orchestrate and train the Reinforcement Learning agent.
"""
import sys
import os
import numpy as np
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_ingestion.synthetic import generate_logistics_data
from optimization.rl_agent import train_routing_agent, evaluate_routing_agent

def main():
    print("--------------------------------------------------")
    print("1. Generating Scaled RL Training Environment...")
    print("--------------------------------------------------")
    # For a simple RL agent, an extremely large node pool requires exponentially heavier training.
    # Training a small 5-node city layout to demonstrate functionality natively here.
    data = generate_logistics_data(num_locations=4, num_vehicles=1, random_seed=42)
    dist_matrix = data["distance_matrix"]
    print(f"Loaded a 5x5 network distance configuration.")
    
    print("\n--------------------------------------------------")
    print("2. Firing up Stable-Baselines3 PPO Agent...")
    print("--------------------------------------------------")
    # PPO requires training epochs to mathematically converge its MLP policies.
    model, _ = train_routing_agent(dist_matrix, total_timesteps=20000)
    
    print("\n--------------------------------------------------")
    print("3. Deterministic Validation...")
    print("--------------------------------------------------")
    # Querying the model purely using trained inference rules without exploration randomness
    results = evaluate_routing_agent(model, dist_matrix)
    
    print("\n======= AGENT INFERENCE RESULTS =======")
    print(f"Learned Route Order : {results['route']}")
    print(f"Total Traversed Path: {results['total_distance']:.2f} km")
    
    if len(results['route']) < 6:
        print("\nNote: Standard RL failed to hit all targets perfectly without advanced Action Masking algorithms.")
        print("This represents standard PPO behaviors taking the shortest unvisited penalty route ending the loop.")
    else:
        print("\nSuccess! PPO properly connected all nodes iteratively!")

if __name__ == "__main__":
    main()
