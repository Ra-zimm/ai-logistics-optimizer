# AI Logistics System 🚛

An Academic MSc-level Reinforcement Learning and Logistics Optimization engine. This repository actively develops and evaluates baseline static routing (VRP), dynamically self-adapting systems tracking real-time traffic bottlenecks, advanced Capacitated logic with Time Windows (CVRPTW), and standard Reinforcement Learning (RL) natively integrating execution arrays.

## 📁 Repository Structure

```text
ai_logistics_system/
│
├── app/                      
│   └── main.py                 # Interactive Streamlit UI Dashboard
│
├── data/
│   └── processed/              # Formatted CSV evaluation datasets and PNG metrics charts
│
├── scripts/                    # Core Execution Pipelines
│   ├── run_simulation.py       # Basic traffic threshold routing demonstrations
│   ├── train_rl.py             # Gymnasium/PPO agent training natively
│   ├── batch_benchmark.py      # Produces multi-run analytical datasets tracking to CSV 
│   ├── visualize_results.py    # Plots Seaborn visual Analytics on generated datasets
│   ├── test_advanced.py        # Proves full vehicle payload capacity & strict delivery Time-Window limits 
│   └── ab_test.py              # A/B Paired T-Test statistical confidence evaluation
│
├── src/
│   ├── data_ingestion/         # Geometric array configurations & mathematical package scaling
│   ├── evaluation/             # Standard analytic trackers (Fuel estimates, Routing Delays, Expected Distances)
│   ├── optimization/           # OR-Tools exact constraints, Reinforcement agents, Dynamic logic evaluators
│   └── simulation/             # Discrete Traffic Sine-Wave structures and Global Weather multipliers
│
└── requirements.txt            # System dependency structure
```

## 🚀 Installation & Setup

Ensure you have a standard Python implementation installed and explicitly initialize the environment:

```bash
cd D:\Project_Advait\ai_logistics_system
pip install -r requirements.txt
```

*(Note: Depending on your exact system bounds, libraries like `pydeck`, `seaborn`, `scipy`, and `stable-baselines3` will install sequentially to fully enable the backend.)*

---

## 🛠️ Execution & Testing Guide

You can modularly test every single architectural tier of the thesis pipeline using the dedicated pipeline endpoints constructed below:

### 1. Interactive Visual Dashboard (Streamlit)
Boot up the interactive 3D map plotting live generated geography locations natively tracking node coordinate geometry. This dashboard allows you to inject severe dynamic traffic roadblocks structurally via sliders and graphically proves how the Dynamic Engine reacts and saves Operational Expected Fleet Hours.
```bash
streamlit run app/main.py
```

### 2. A/B Statistical Confidence Evaluation
Rigorously establish your thesis mathematical metrics. Evaluates 40 randomized geometric simulations exploring both Static execution arrays and Dynamic Engine Reroutes. Applies Scipy `ttest_rel` Paired Tests statistically evaluating explicit geographic advantages formally proving superiority exactly bounded at standard `95% Statistical Confidence Levels`.
```bash
python scripts/ab_test.py
```

### 3. Generate Analytical Thesis Charts
If you need high-resolution graphics embedding exactly into standard academic documents:
1. Run the strict 20-batch multi-simulation loop. This iterates explicit scenarios generating raw `pandas.DataFrame` array exports cleanly to `data/processed/benchmark_results.csv`:
    ```bash
    python scripts/batch_benchmark.py
    ```
2. Spawn the distinct Seaborn internal rendering pipeline parsing the CSV generating `.png` bar/line charts directly into `data/processed/plots/`:
    ```bash
    python scripts/visualize_results.py
    ```

### 4. Advanced Realism Track (CVRPTW & Physics)
Explore the deeply advanced optimization loops completely mimicking live industry tracking execution. Runs rigorous code incorporating maximum vehicle kilograms payload restrictions, incredibly tight chronological arrival minutes, continuous sinusoidal harmonic rush-hour delays mapping absolute real-world peaks, and severe atmospheric modifiers (`storm`, `snow` matrices).
```bash
python scripts/test_advanced.py
```

### 5. Reinforcement Learning Logic (Neural Evaluation)
Instantiate a fully decoupled custom physics mapped `Gymnasium Environment`. Defines literal agent restrictions bounding severe explicit penalties (-1000 scoring arrays on illegal target visits) running purely executing standard Stable-Baselines3 Proximal Policy Optimization (PPO) mathematical arrays natively to learn graph geometries independently!
```bash
python scripts/train_rl.py
```
