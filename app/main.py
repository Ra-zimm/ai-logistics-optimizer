import streamlit as st
import numpy as np
import pandas as pd
import pydeck as pdk
import sys
import os

# Properly hook up internal architecture paths
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_ingestion.synthetic import generate_logistics_data
from optimization.dynamic_router import DynamicFleetManager
from evaluation.metrics import calculate_delivery_time

st.set_page_config(page_title="AI Logistics System", layout="wide", initial_sidebar_state="expanded")

# --- UI HEADER ---
st.title("🏎️ AI Logistics System Dashboard")
st.markdown("Interactive evaluation of standard static routing vs Dynamic AI-driven path adaptation.")

# --- SIDEBAR SIMULATION CONTROLS ---
st.sidebar.header("🌐 Routing Network Scope")
num_nodes = st.sidebar.slider("Active Delivery Targets", min_value=3, max_value=20, value=7)
num_vehicles = st.sidebar.slider("Fleet Vehicles Available", min_value=1, max_value=5, value=1)

st.sidebar.header("🚦 Dynamic Traffic Events")
st.sidebar.markdown("Test the engine's dynamic re-computation threshold by placing heavy blockades over standard routes.")
inject_traffic = st.sidebar.checkbox("Simulate Severe Roadblock Event", value=False)
traffic_severity = st.sidebar.slider("Severity Multiplier (Delay)", min_value=1.5, max_value=10.0, value=5.0)

# --- BACKEND LINKING ---
@st.cache_data
def load_routing_data(nodes, vehicles):
    return generate_logistics_data(num_locations=nodes, num_vehicles=vehicles, random_seed=42)

data = load_routing_data(num_nodes, num_vehicles)
dist_matrix = data["distance_matrix"]
all_nodes = data["all_nodes"]  # Coordinates array [lat, lon]

fleet_manager = DynamicFleetManager(dist_matrix, num_vehicles, 0)
baseline_routes = fleet_manager.active_routes

# Inject dynamically targeted delays if requested by UI
is_rerouted = False
if inject_traffic:
    # Explicitly break the very first scheduled edge of vehicle 1
    active_path = baseline_routes[0]["route"]
    if len(active_path) > 2:
        fleet_manager.trigger_delay_event(active_path[1], active_path[2], traffic_severity)
        
    # Evaluate global network mathematical tolerance vs active degradation 
    reroute_res = fleet_manager.evaluate_and_reroute(threshold_degradation=1.1)
    is_rerouted = reroute_res.get("recomputed", False)

active_routes = fleet_manager.active_routes

# --- GEOGRAPHIC MAP VISUALIZATIONS ---
st.subheader("Live Satellite Node Routing")

def format_pydeck_routes(routes, r_color, g_color, b_color):
    """Converts OR-Tools logic into PyDeck Geographic PathLayers."""
    path_data = []
    for r in routes:
        path = []
        for index in r["route"]:
            # Pydeck expects explicit [longitude, latitude] arrays natively
            lat, lon = all_nodes[index]
            path.append([lon, lat])
        path_data.append({"path": path})
        
    return pdk.Layer(
        "PathLayer",
        path_data,
        get_color=[r_color, g_color, b_color],
        width_scale=20,
        width_min_pixels=4,
        get_path="path",
        get_width=5
    )


# 1. Base Layer: Original mapped expectation (Red layout)
layer_unoptimized = format_pydeck_routes(baseline_routes, 200, 50, 50)
layers_array = [layer_unoptimized]

# 2. Adaptation Layer: Will trace out detours if computation activated (Green layout)
if inject_traffic and is_rerouted:
    st.info("🟢 **Dynamic Logic Engaged:** A massive roadblock was identified on your standard red path. The Dynamic Engine mathematically rerouted all trucks onto the green optimal paths!")
    layer_adapted = format_pydeck_routes(active_routes, 0, 200, 80)
    layers_array.append(layer_adapted)
elif inject_traffic and not is_rerouted:
    st.warning("⚠️ **Alert Triggered:** The delay event wasn't computationally severe enough to warrant entirely recomputing global arrays!")
else:
    st.success("✅ **Network Operating Normally:** No physical delay events active.")

# 3. Coordinate Node Scatter mappings
node_scatter = pdk.Layer(
    "ScatterplotLayer",
    [{"lon": all_nodes[i][1], "lat": all_nodes[i][0], "type": "Depot (Origin)" if i == 0 else "Delivery Target"} for i in range(len(all_nodes))],
    get_position="[lon, lat]",
    get_fill_color="type == 'Depot (Origin)' ? [0, 0, 0, 255] : [255, 255, 255, 255]",
    get_line_color=[0, 0, 0],
    line_width_min_pixels=2,
    get_radius=200,
    pickable=True
)
layers_array.append(node_scatter)

view_state = pdk.ViewState(latitude=all_nodes[0][0], longitude=all_nodes[0][1], zoom=11)
st.pydeck_chart(pdk.Deck(layers=layers_array, initial_view_state=view_state, tooltip={"text": "{type}"}))


# --- BENCHMARKING & ANALYTICS ---
st.markdown("---")
st.subheader("Performance Evaluation Analytics")

# Calculate active penalty logic
traffic_matrix = fleet_manager.sim_engine.get_travel_times()
unadapted_cost = fleet_manager._calculate_route_cost(baseline_routes[0]["route"], traffic_matrix)
adapted_cost = active_routes[0]["distance"]

col1, col2, col3 = st.columns(3)
col1.metric("Blind Route Cost (Under Traffic)", f"{unadapted_cost:.2f} km")

delta_str = f"-{unadapted_cost - adapted_cost:.2f} km avoided!" if is_rerouted else "0 km (Optimal)"
col2.metric("Dynamic Algorithm Cost", f"{adapted_cost:.2f} km", delta=delta_str, delta_color="normal")

time_saved_hours = calculate_delivery_time(unadapted_cost) - calculate_delivery_time(adapted_cost)
col3.metric("Fleet Operational Time Saved", f"{abs(time_saved_hours):.2f} hours", delta="Recomputation Edge" if is_rerouted else None)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("#### Cost Comparison Visualization")

# Automated UI Bar Charting
df = pd.DataFrame([
    {"Routing Method": "Static OR-Tools Baseline", "Traversed Kilometers": unadapted_cost},
    {"Routing Method": "Dynamic Engine Reroute", "Traversed Kilometers": adapted_cost}
])
st.bar_chart(df.set_index("Routing Method"))
