
import streamlit as st

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Mugenuni Master App",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# HEADER & HERO SECTION
# ==========================================
st.image("logo.jpg", width=250)
st.title("🌊 MUGENUNI RESEARCH PTY LTD")
st.subheader("Interactive Commercial Aquaculture Simulation Suite")
st.divider()

st.markdown("""
### Welcome to the Master App
This software suite is the digital twin of the proposed **5,400 sqm Glasshouse Facility in Northern N.S.W.** It mathematically models the biological growth, feed demands, operational physics, and financial returns 
for the commercial production of *Tripneustes gratilla*.

👈 **Please use the sidebar to navigate between the three core modules:**
""")

# ==========================================
# MODULE OVERVIEWS
# ==========================================
col1, col2, col3 = st.columns(3)

with col1:
    st.info("### 🌱 1. Grow-Out Model")
    st.markdown("""
    **The Biological Engine:**
    * Simulates the 17-week growth from 15mm to 60mm, and the bridge to the 80mm target.
    * Dynamically calculates daily *Ulva* feed demand.
    * Models the staggered water exchange strategy (0.5 to 1.0) and calculates Megaliters saved.
    """)

with col2:
    st.warning("### 🍣 2. Enhancement Model")
    st.markdown("""
    **The Finishing Sprint:**
    * Simulates the strict 8-week final grow-out phase (60mm to 80mm).
    * Tracks the Gonadosomatic Index (GSI) trajectory up to the 15% commercial target.
    * Calculates the precise premium roe yield per raceway using a 100% *Ulva* diet.
    """)

with col3:
    st.success("### 💰 3. Financial Engine")
    st.markdown("""
    **The ROI Calculator:**
    * Translates biological outputs into real-world unit economics ($3.67/unit cost).
    * Tracks the $4.4M CAPEX and the $1.1M Working Capital "Valley of Death".
    * Projects steady-state EBITDA and visualizes the exact month the facility breaks even.
    """)

st.divider()

# ==========================================
# PROJECT SUMMARY METRICS
# ==========================================
st.markdown("### 🏆 Northern N.S.W. Facility: Target Metrics")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    st.metric(label="Target Monthly Harvest", value="50,000 Units")
with metric_col2:
    st.metric(label="Premium Roe Yield (15% GSI)", value="1,500 kg / month")
with metric_col3:
    st.metric(label="Gross Operating Margin", value="44.4%")
with metric_col4:
    st.metric(label="Capital Break-Even", value="Month 44")

st.caption("© 2026 Mugenuni Research Pty Ltd. Confidential and Proprietary.")



