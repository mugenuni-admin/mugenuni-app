import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION & HEADER
# ==========================================
st.set_page_config(page_title="T. gratilla Grow-Out Model", layout="wide")

st.title("🌱 T. gratilla Grow-Out & Flow Rate Model")
st.markdown("""
This module simulates the biological growth, *Ulva* feed demand, and optimized water exchange 
requirements for a single 11m raceway holding **Tripneustes gratilla**. 
It includes the staggered flow-rate logic (0.5 exchange for < 40mm, 1.0 exchange for > 40mm) 
to accurately model OPEX efficiencies.
""")
st.divider()

# ==========================================
# SIDEBAR PARAMETERS
# ==========================================
st.sidebar.header("Biological Parameters")
start_size = st.sidebar.number_input("Starting Size (mm)", min_value=5.0, value=15.0, step=1.0)
target_size = st.sidebar.number_input("Target Size (mm)", min_value=20.0, value=80.0, step=1.0)
growth_rate = st.sidebar.number_input("Growth Rate (mm/week)", min_value=0.5, value=2.65, step=0.1)
feed_rate = st.sidebar.number_input("Daily Feed Rate (% Body Wt)", min_value=1.0, value=5.0, step=0.5) / 100

st.sidebar.header("Raceway Parameters")
urchins_per_raceway = st.sidebar.number_input("Urchins per Raceway (40% Density)", value=1270, step=10)
base_raceway_vol = st.sidebar.number_input("Base Raceway Volume (L)", value=2640, step=100)
flow_switch_size = st.sidebar.number_input("Flow Increase Threshold (mm)", value=40.0, step=1.0)

# ==========================================
# SIMULATION ENGINE
# ==========================================
weeks = []
diameters = []
weights = []
daily_feeds = []
hourly_flows = []

current_size = start_size
week = 0

# Run the loop until the target size is reached
while current_size <= target_size:
    weeks.append(week)
    diameters.append(current_size)
    
    # Allometric Weight Calculation: Weight = 0.0004 * (Diameter^3)
    weight_g = 0.0004 * (current_size ** 3)
    weights.append(weight_g)
    
    # Biomass and Feed Calculation
    biomass_kg = (weight_g * urchins_per_raceway) / 1000
    daily_feed_kg = biomass_kg * feed_rate
    daily_feeds.append(daily_feed_kg)
    
    # Staggered Flow Rate Logic
    if current_size < flow_switch_size:
        flow_lph = base_raceway_vol * 0.5  # 0.5 exchange per hour
    else:
        flow_lph = base_raceway_vol * 1.0  # 1.0 exchange per hour
    hourly_flows.append(flow_lph)
    
    # Increment for next week
    current_size += growth_rate
    week += 1

# Compile into a DataFrame
df = pd.DataFrame({
    "Week": weeks,
    "Diameter (mm)": diameters,
    "Weight (g)": weights,
    "Daily Feed (kg)": daily_feeds,
    "Hourly Flow (L/hr)": hourly_flows
})

# Calculate Cumulative Totals
df["Cumulative Feed (kg)"] = df["Daily Feed (kg)"] * 7  # Convert daily to weekly
df["Cumulative Feed (kg)"] = df["Cumulative Feed (kg)"].cumsum()

# ==========================================
# DASHBOARD METRICS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Time to Target Size", value=f"{week - 1} Weeks")
with col2:
    final_weight = df["Weight (g)"].iloc[-1]
    st.metric(label="Final Target Weight", value=f"{final_weight:.1f} g")
with col3:
    total_feed = df["Cumulative Feed (kg)"].iloc[-1]
    st.metric(label="Total Ulva Required (Per Raceway)", value=f"{total_feed:.0f} kg")
with col4:
    # Calculate water saved by not running 1.0 exchange the whole time
    total_hours = (week - 1) * 7 * 24
    max_flow_possible = total_hours * base_raceway_vol
    actual_flow = (df["Hourly Flow (L/hr)"] * 7 * 24).sum()
    water_saved_ml = (max_flow_possible - actual_flow) / 1_000_000
    st.metric(label="Water Saved via Staggered Flow", value=f"{water_saved_ml:.2f} Megaliters")

st.divider()

# ==========================================
# VISUALIZATIONS
# ==========================================
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    # 1. Growth Curve (Diameter and Weight)
    fig_growth = go.Figure()
    fig_growth.add_trace(go.Scatter(x=df["Week"], y=df["Diameter (mm)"], mode='lines', name='Diameter (mm)', line=dict(color='#1E88E5', width=3)))
    fig_growth.add_trace(go.Scatter(x=df["Week"], y=df["Weight (g)"], mode='lines', name='Weight (g)', yaxis='y2', line=dict(color='#D32F2F', width=3)))
         
    fig_growth.update_layout(
        title="Biological Growth Trajectory (15mm to 80mm)",
        xaxis_title="Weeks in System",
        yaxis=dict(title=dict(text="Diameter (mm)", font=dict(color="#1E88E5")), tickfont=dict(color="#1E88E5")),
        yaxis2=dict(title=dict(text="Weight (g)", font=dict(color="#D32F2F")), tickfont=dict(color="#D32F2F"), overlaying='y', side='right'),
        hovermode="x unified"
    )
    st.plotly_chart(fig_growth, use_container_width=True)

with row1_col2:
    # 2. Water Flow Rate Shift
    fig_flow = px.area(df, x="Week", y="Hourly Flow (L/hr)", 
                       title="Raceway Water Exchange Rate Optimization",
                       color_discrete_sequence=['#00ACC1'])
    # Add a vertical line where the switch happens
    switch_week = df[df["Diameter (mm)"] >= flow_switch_size]["Week"].iloc[0]
    fig_flow.add_vline(x=switch_week, line_width=2, line_dash="dash", line_color="red", 
                       annotation_text=f" 40mm Reached (Flow Increased)", annotation_position="top left")
    
    fig_flow.update_layout(hovermode="x unified", yaxis_title="Pump Flow Rate (Liters/Hour)")
    st.plotly_chart(fig_flow, use_container_width=True)

# 3. Feed Demand Curve
fig_feed = px.bar(df, x="Week", y="Daily Feed (kg)", 
                  title="Daily Ulva Feed Demand Per Raceway (Scaling with Biomass)",
                  color_discrete_sequence=['#43A047'])
fig_feed.update_layout(hovermode="x unified", yaxis_title="Daily Ulva Required (kg)")
st.plotly_chart(fig_feed, use_container_width=True)

# ==========================================
# DATA EXPORT
# ==========================================
with st.expander("View Raw Simulation Data"):
    st.dataframe(df.style.format({
        "Diameter (mm)": "{:.1f}",
        "Weight (g)": "{:.1f}",
        "Daily Feed (kg)": "{:.2f}",
        "Hourly Flow (L/hr)": "{:.0f}",
        "Cumulative Feed (kg)": "{:.1f}"
    }))