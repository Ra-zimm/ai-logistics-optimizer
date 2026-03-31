"""
Analytics Visualization Suite

Reads the aggregated benchmark datasets from CSV and generates 
advanced statistical comparisons plotting natively via seaborn/matplotlib.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def main():
    # Enforce clean visual styling globally
    sns.set_theme(style="whitegrid", palette="muted")
    
    # Safely locate the project mapping explicitly
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    csv_path = os.path.join(base_dir, 'data', 'processed', 'benchmark_results.csv')
    output_dir = os.path.join(base_dir, 'data', 'processed', 'plots')
    os.makedirs(output_dir, exist_ok=True)
    
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found. Please wait for batch_benchmark.py to finish.")
        return
        
    df = pd.read_csv(csv_path)
    print("✅ Successfully ingested Benchmark Data Frame.")
    
    # ----------------------------------------------------
    # 1. Bar Chart: Average Total Distance
    # ----------------------------------------------------
    print("Generating Chart 1: Total Distance Layout...")
    plt.figure(figsize=(10, 6))
    
    # Using 'method' capitalization matching exactly what the CSV wrote
    # Depending on CSV, it might be 'Static Baseline', 'Dynamic Router', 'RL Policy (PPO)'
    sns.barplot(data=df, x="method", y="total_distance_km", errorbar="sd", palette="viridis")
    plt.title("Average Traversed Cost Distance by Routing Model\n(Lower is Optimal)", fontsize=15, fontweight='bold')
    plt.ylabel("Distance (km)", fontsize=12)
    plt.xlabel("Algorithm Methodology", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '1_avg_total_distance.png'), dpi=300)
    plt.close()
    
    # ----------------------------------------------------
    # 2. Line Chart: Delivery Time Across Unique Simulation Runs
    # ----------------------------------------------------
    print("Generating Chart 2: Time Series Runs...")
    plt.figure(figsize=(13, 6))
    sns.lineplot(data=df, x="Run_ID", y="delivery_time_hours", hue="method", marker='o', linewidth=2.5)
    plt.title("Expected Delivery Time Over 20 Independent Geographic Renderings", fontsize=15, fontweight='bold')
    plt.ylabel("Delivery Time (Hours)", fontsize=12)
    plt.xlabel("Unique Geographic Map Scenario (Run ID)", fontsize=12)
    plt.xticks(df['Run_ID'].unique())
    plt.legend(title="Algorithm Profile", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, '2_delivery_time_variance.png'), dpi=300)
    plt.close()
    
    # ----------------------------------------------------
    # 3. Percentage Improvement Chart (Compared to Baseline)
    # ----------------------------------------------------
    print("Generating Chart 3: Efficiency Deltas...")
    pivot_df = df.pivot(index='Run_ID', columns='method', values='total_distance_km')
    
    # Ensure columns exist dynamically
    static_col = "Static Baseline"
    dynamic_col = "Dynamic Router"
    rl_col = "RL Policy (PPO)"
    
    if static_col in pivot_df.columns:
        # Distance Efficiency = (Base - Adapted) / Base
        if dynamic_col in pivot_df.columns:
            pivot_df['Dynamic OR-Tools Engine (%)'] = ((pivot_df[static_col] - pivot_df[dynamic_col]) / pivot_df[static_col]) * 100
        if rl_col in pivot_df.columns:
            pivot_df['PyTorch PPO Network (%)'] = ((pivot_df[static_col] - pivot_df[rl_col]) / pivot_df[static_col]) * 100
            
        plot_cols = [c for c in ['Dynamic OR-Tools Engine (%)', 'PyTorch PPO Network (%)'] if c in pivot_df.columns]
        
        if len(plot_cols) > 0:
            improv_df = pivot_df[plot_cols].melt(var_name='Method', value_name='Improvement (%)')
            
            plt.figure(figsize=(10, 6))
            sns.barplot(data=improv_df, x="Method", y="Improvement (%)", errorbar="sd", palette="mako")
            plt.title("% Cost Reduction Vs Static Baseline Engine (Blind to Traffic)", fontsize=15, fontweight='bold')
            plt.ylabel("Improvement (%) - Higher is Better", fontsize=12)
            plt.xlabel("Adaptive Method", fontsize=12)
            plt.axhline(0, color='black', linestyle='--', linewidth=1.5)
            plt.tight_layout()
            plt.savefig(os.path.join(output_dir, '3_percentage_improvement.png'), dpi=300)
            plt.close()
        
    print(f"\n✅ Graphic Pipeline Finished! 3 High-Res PNG analytical plots saved to:")
    print(f" -> {output_dir}")

if __name__ == "__main__":
    main()
