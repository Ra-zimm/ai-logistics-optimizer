# VIVA Presentation Script: AI Logistics Routing Engine

When you are presenting this to your professors or evaluators, you want to follow a **"Problem -> Solution -> Proof"** structure. This guide tells you exactly what to say and what scripts to run on your screen while you say it.

---

## Step 1: The Problem (Introduction)
**What to say:**
> *"Traditional logistics systems rely on 'Static Routing'. A dispatcher calculates the best route for a delivery truck at 6:00 AM, and the driver follows it all day. The problem is that the real world is volatile. If a massive traffic jam happens at 1:00 PM, a static route sends the truck straight into the jam, wasting fuel, missing delivery time windows, and costing the company money."*

## Step 2: The Solution (Your Architecture)
**What to say:**
> *"My project solves this by building a 'Hybrid AI Routing Optimzer'. It doesn't just calculate a route once; it continuously polls a real-world physics engine for traffic and weather constraints. If a route degrades by 20%, my **Dynamic Fleet Manager** mathematically interrupts the truck and forces it to take an optimal detour. I utilized Google's OR-Tools for exact mathematical solving, and built a custom Reinforcement Learning (RL) network using Proximal Policy Optimization to explore neural routing."*

---

## Step 3: The Live Demo (The "Wow" Factor)
*Before the presentation, have your terminal already running: `streamlit run app/main.py` and have the browser open to the Dashboard.*

**What to do on screen:**
1. Show them the map. Point out the black depot node and the white delivery targets. 
2. Point out the **Red Line** (This is the "Static" route the truck originally planned to take).
3. **Click the "Simulate Severe Roadblock" checkbox on the left sidebar.**

**What to say:**
> *"Let's look at it in action. Here is our delivery network. Suddenly, a severe accident occurs on the main highway. In a traditional system, the truck would be stuck. However, when I inject this traffic event into my system, notice what happens... The engine immediately recognizes the delay and dynamically reroutes the entire fleet onto the **Green Detour Path**! You can see in the metrics panel below that this AI decision literally saved us multiple Operational Fleet Hours and kilometers!"*

---

## Step 4: The MSc-Level Physics (The Math)
*Open your IDE and show them the `src/optimization/or_tools_cvrptw.py` file or run `python scripts/test_advanced.py` in a terminal.*

**What to say:**
> *"To ensure this was Master's level, I didn't just route dots on a map natively. I engineered it into a **Capacitated Vehicle Routing Problem with Time Windows (CVRPTW)**. 
> 1. **Payload Capacity:** The AI refuses to let a truck pick up more than 40kg of packages, forcing it to return to the depot mathematically.
> 2. **Time Windows:** The AI translates distances into chronological minutes, ensuring trucks only arrive at locations when their delivery shifts are actually open.
> 3. **Environmental Physics:** I built a continuous Harmonic Sine-Wave algorithm that artificially surges traffic speeds by 50% specifically around 12:00 PM and 4:00 PM to mimic live city 'Rush Hours', along with global Weather matrices slowing down speeds for 'Snow' or 'Storms'."*

---

## Step 5: The Statistical Proof (The Conclusion)
*Open up the three PNG charts inside your `data/processed/plots/` folder to show on the screen.*

**What to say:**
> *"Finally, I needed to academically prove that my Dynamic engine saves money. I wrote an automation array that ran 40 independent, randomized geographic city trials. 
> As you can see in these Seaborn visualization charts, the Dynamic Routing explicitly bypassed the Static Routing costs every time.
> I performed a **Scipy Paired T-Test** on the datasets. The resulting P-Value was incredibly low (`< 0.05`), allowing me to comfortably **Reject the Null Hypothesis** and statistically prove that this architecture yields a ~25% to 30% reduction in delivery times and fuel consumption!"*
