import streamlit as st
import pandas as pd

st.set_page_config(page_title="Mugenuni Environmental Engine", layout="wide")

# High-Contrast Styling
st.markdown("""
    <style>
    html, body, [class*="ViewContainer"] { font-size: 20px !important; }
    h1 { font-size: 44px !important; color: #000000 !important; border-bottom: 3px solid #000; }
    .stMetric { background-color: #ffffff; padding: 25px; border: 4px solid #000000; border-radius: 15px; }
    .warning-box { background-color: #ffe6e6; padding: 20px; border-left: 6px solid #cc0000; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: SYSTEM PARAMETERS ---
st.sidebar.header("🌊 WATER DYNAMICS")
flow_rate = st.sidebar.slider("Exchanges per Hour", 0.3, 3.0, 1.0, step=0.1)
temp = st.sidebar.slider("Water Temp (°C)", 24.0, 30.0, 27.0, step=0.5)

st.sidebar.divider()
st.sidebar.header("⚖️ BIOMASS LOAD")
urchin_weight = st.sidebar.number_input("Average Urchin Weight (g)", value=200, step=10)
urchins_per_raceway = st.sidebar.number_input("Urchins per Raceway", value=1270, step=10)

# --- THE MATH ---
total_biomass_kg = (urchin_weight * urchins_per_raceway) / 1000
raceway_vol_L = 2640
water_flow_Lph = raceway_vol_L * flow_rate

# Oxygen Calculation
# Assuming ~6.7 mg/L DO saturation at 27C and 35ppt
do_saturation = 6.7 
o2_influx_gph = (water_flow_Lph * do_saturation) / 1000
o2_consumption_rate = 15 # Conservative estimate: mg/kg/hr
o2_demand_gph = (total_biomass_kg * o2_consumption_rate) / 1000
o2_buffer = o2_influx_gph - o2_demand_gph

# Feed & IMTA Ulva loop calculation
daily_feed_rate = 0.05
daily_ulva_kg = total_biomass_kg * daily_feed_rate
weekly_ulva_kg = daily_ulva_kg * 7

# --- MAIN INTERFACE ---
st.title("♻️ MUGENUNI: ENVIRONMENTAL & IMTA ENGINE")
st.write(f"### Simulating an 11m Raceway ({raceway_vol_L} L) with {total_biomass_kg:.1f} kg of Standing Biomass")

col1, col2, col3 = st.columns(3)
col1.metric("FLOW RATE (L/hr)", f"{water_flow_Lph:,.0f}")
col2.metric("O2 INFLUX (g/hr)", f"{o2_influx_gph:.1f}")
col3.metric("O2 DEMAND (g/hr)", f"{o2_demand_gph:.1f}")

st.divider()

tab1, tab2, tab3 = st.tabs(["🫧 OXYGEN DYNAMICS", "🌿 IMTA ULVA LOOP", "⚠️ CHEMISTRY & RISK"])

with tab1:
    st.write("### Dissolved Oxygen (DO) Buffer")
    demand_pct = (o2_demand_gph / o2_influx_gph) * 100 if o2_influx_gph > 0 else 100
    st.write(f"At {temp}°C, the biological oxygen demand of the urchins accounts for only **{demand_pct:.1f}%** of the dissolved oxygen provided strictly by the main water exchange.")
    
    if o2_buffer > 0:
        st.success(f"**Safe Margin:** The system maintains a surplus of **{o2_buffer:.1f} grams/hour** of oxygen, creating a massive safety buffer before accounting for supplementary tray aeration or influent spouts.")
    else:
        st.error("**CRITICAL:** Biological oxygen demand exceeds primary influx. High mortality risk.")

with tab2:
    st.write("### The Circular Nutrient Loop")
    st.write("Total Ammonia Nitrogen (TAN) excretion for *T. gratilla* is exceptionally low, flushing effortlessly at 1.0 exchange/hour. The primary bio-remediation strategy utilizes *Ulva* raceways to strip dissolved nitrogenous waste and upcycle it into high-protein feed.")
    
    
    
    st.info(f"**Feed Production Target:** To maintain this {total_biomass_kg:.0f}kg standing crop at a 5% daily consumption rate, the IMTA biofilter must continuously produce **{weekly_ulva_kg:.1f} kg of 34% protein Ulva per week**.")

with tab3:
    st.write("### Biogenic Acidification Risk Management")
    st.markdown("""
    <div class='warning-box'>
        <h4>PRIMARY LIMITING FACTOR: pH REDUCTION</h4>
        The intensive uptake of bicarbonates for test calcification and the continuous release of respiratory CO2 by <i>T. gratilla</i> rapidly alters the carbonate chemistry of the water. <br><br><b>If pH drops below 7.8, test growth effectively stalls.</b>
    </div>
    """, unsafe_allow_html=True)
    
    st.write(" ")
    st.write("### Standard Operating Procedure (SOP): Alkalinity Dosing")
    st.write("* Nitrification in the MBBR biofilter inherently consumes alkalinity.")
    st.write("* **Mitigation:** An automated Sodium Bicarbonate dosing pump must be integrated into the primary sump.")
    st.write("* **Trigger:** pH probes continuously monitor the effluent, triggering the dosing pump to strictly maintain pH at **8.1**.")