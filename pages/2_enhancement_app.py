import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION & HEADER
# ==========================================
st.set_page_config(page_title="T. gratilla Enhancement Model", layout="wide")

st.title("🍣 T. gratilla Gonad Enhancement Model (8-Week Sprint)")
st.markdown("""
This module models the final 8-week finishing phase. Juveniles enter at **60 mm**, 
are spaced to a 40% benthic density, and are fed a strict 100% diet of **34% protein *Ulva***. 
The goal is to bridge the final somatic growth gap to **80 mm (200g)** while driving the 
Gonadosomatic Index (GSI) to a premium **15%**.
""")
st.divider()

# ==========================================
# SIDEBAR PARAMETERS
# ==========================================
st.sidebar.header("Biological Parameters")
start_size = st.sidebar.number_input("Entry Size (mm)", min_value=40.0, value=60.0, step=1.0)
target_size = st.sidebar.number_input("Harvest Size (mm)", min_value=60.0, value=80.0, step=1.0)
enhancement_weeks = st.sidebar.number_input("Duration (Weeks)", min_value=4, value=8, step=1)
feed_rate = st.sidebar.number_input("Daily Feed Rate (% Body Wt)", min_value=1.0, value=5.0, step=0.5) / 100

st.sidebar.header("GSI & Yield Targets")
start_gsi = st.sidebar.number_input("Initial GSI (%)", min_value=1.0, value=5.0, step=0.5) / 100
target_gsi = st.sidebar.number_input("Target GSI (%)", min_value=10.0, value=15.0, step=0.5) / 100

st.sidebar.header("Raceway Capacity")
urchins_per_raceway = st.sidebar.number_input("Urchins per Raceway (40% Density)", value=1270, step=10)

# ==========================================
# SIMULATION ENGINE
# ==========================================
weeks = np.arange(0, enhancement_weeks + 1)
# Linear interpolation for growth and GSI during the 8-week phase
diameters = np.linspace(start_size, target_size, enhancement_weeks + 1)
gsis = np.linspace(start_gsi, target_gsi, enhancement_weeks + 1)

weights = []
roe_weights = []
daily_feeds = []

for i in range(len(weeks)):
    # Allometric Weight Calculation
    weight_g = 0.0004 * (diameters[i] ** 3)
    weights.append(weight_g)
    
    # Roe Yield Calculation
    roe_g = weight_g * gsis[i]
    roe_weights.append(roe_g)
    
    # Feed Calculation (per raceway)
    biomass_kg = (weight_g * urchins_per_raceway) / 1000
    daily_feed_kg = biomass_kg * feed_rate
    daily_feeds.append(daily_feed_kg)

# Compile into a DataFrame
df = pd.DataFrame({
    "Week": weeks,
    "Diameter (mm)": diameters,
    "Weight (g)": weights,
    "GSI (%)": gsis * 100,
    "Roe per Urchin (g)": roe_weights,
    "Daily Feed (kg)": daily_feeds
})

# Calculate Cumulative Feed
df["Cumulative Feed (kg)"] = df["Daily Feed (kg)"] * 7
df["Cumulative Feed (kg)"] = df["Cumulative Feed (kg)"].cumsum()

# ==========================================
# DASHBOARD METRICS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

final_weight = df["Weight (g)"].iloc[-1]
final_roe = df["Roe per Urchin (g)"].iloc[-1]
total_roe_raceway_kg = (final_roe * urchins_per_raceway) / 1000
total_feed = df["Cumulative Feed (kg)"].iloc[-1]

with col1:
    st.metric(label="Harvest Target Weight", value=f"{final_weight:.1f} g")
with col2:
    st.metric(label="Roe Yield per Urchin (15% GSI)", value=f"{final_roe:.1f} g")
with col3:
    st.metric(label="Total Premium Uni per Raceway", value=f"{total_roe_raceway_kg:.1f} kg")
with col4:
    st.metric(label="Total 34% Ulva Required per Raceway", value=f"{total_feed:.0f} kg")

st.divider()

# ==========================================
# VISUALIZATIONS
# ==========================================
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    # 1. GSI & Roe Weight Growth
    fig_gsi = go.Figure()
    fig_gsi.add_trace(go.Bar(x=df["Week"], y=df["Roe per Urchin (g)"], name='Roe Weight (g)', marker_color='#FFA726'))
    fig_gsi.add_trace(go.Scatter(x=df["Week"], y=df["GSI (%)"], mode='lines+markers', name='GSI (%)', yaxis='y2', line=dict(color='#E65100', width=3)))
    
    fig_gsi.update_layout(
        title="Gonad Bulking Trajectory (100% High-Protein Ulva)",
        xaxis_title="Enhancement Week",
        yaxis=dict(title=dict(text="Roe Weight (g)", font=dict(color="#FFA726")), tickfont=dict(color="#FFA726")),
        yaxis2=dict(title=dict(text="GSI (%)", font=dict(color="#E65100")), tickfont=dict(color="#E65100"), overlaying='y', side='right'),
        hovermode="x unified",
        legend=dict(x=0.01, y=0.99)
    )
    st.plotly_chart(fig_gsi, use_container_width=True)

with row1_col2:
    # 2. Daily Feed Demand
    fig_feed = px.area(df, x="Week", y="Daily Feed (kg)", 
                       title="Daily Feed Demand per Raceway (Scaling with Biomass)",
                       color_discrete_sequence=['#66BB6A'])
    fig_feed.update_layout(hovermode="x unified", yaxis_title="Daily 34% Ulva Required (kg)")
    st.plotly_chart(fig_feed, use_container_width=True)

# ==========================================
# DATA EXPORT
# ==========================================
with st.expander("View Raw Enhancement Data"):
    st.dataframe(df.style.format({
        "Diameter (mm)": "{:.1f}",
        "Weight (g)": "{:.1f}",
        "GSI (%)": "{:.1f}",
        "Roe per Urchin (g)": "{:.1f}",
        "Daily Feed (kg)": "{:.2f}",
        "Cumulative Feed (kg)": "{:.1f}"
    }))