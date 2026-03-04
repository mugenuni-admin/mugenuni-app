import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ==========================================
# PAGE CONFIGURATION & HEADER
# ==========================================
st.set_page_config(page_title="Financial Engine", layout="wide")

st.title("💰 Financial Engine & ROI Calculator")
st.markdown("""
This module translates the biological outputs of the *Tripneustes gratilla* grow-out and enhancement models 
into commercial unit economics. It visualizes the Capital Expenditure (CAPEX), Operational Expenditure (OPEX), 
and the 5-year cumulative cash flow to determine the exact break-even horizon.
""")
st.divider()

# ==========================================
# SIDEBAR PARAMETERS
# ==========================================
st.sidebar.header("Capital Expenditure (CAPEX)")
facility_capex = st.sidebar.number_input("Facility Build & Equipment ($)", min_value=1000000, value=4400000, step=100000)

st.sidebar.header("Revenue Assumptions")
monthly_harvest_kg = st.sidebar.number_input("Target Premium Uni (kg/month)", min_value=100, value=1500, step=100)
price_per_kg = st.sidebar.number_input("Wholesale Price per kg ($ AUD)", min_value=50, value=200, step=10)

st.sidebar.header("Monthly OPEX Assumptions")
feed_cost = st.sidebar.number_input("Ulva Feed Cost ($/month)", value=35000, step=1000)
labor_cost = st.sidebar.number_input("Labor & Management ($/month)", value=65000, step=1000)
energy_cost = st.sidebar.number_input("Energy & Pumping ($/month)", value=40000, step=1000)
logistics_cost = st.sidebar.number_input("Packaging & Freight ($/month)", value=26800, step=1000)

# ==========================================
# FINANCIAL CALCULATIONS
# ==========================================
# Top Line
monthly_revenue = monthly_harvest_kg * price_per_kg
annual_revenue = monthly_revenue * 12

# Expenses
total_monthly_opex = feed_cost + labor_cost + energy_cost + logistics_cost
annual_opex = total_monthly_opex * 12

# Margins
monthly_ebitda = monthly_revenue - total_monthly_opex
gross_margin_pct = (monthly_ebitda / monthly_revenue) * 100 if monthly_revenue > 0 else 0

# Unit Economics
total_urchins_harvested = 50000  # Based on master app summary
cost_per_urchin = total_monthly_opex / total_urchins_harvested

# ==========================================
# 5-YEAR CASH FLOW SIMULATION
# ==========================================
months = np.arange(0, 61)
cash_flow = np.zeros(61)

# Assume Months 1-12 are construction and biological ramp-up (Burning OPEX, No Revenue)
# Month 13 onwards is steady-state harvest
for m in months:
    if m == 0:
        cash_flow[m] = -facility_capex
    elif m <= 12:
        # Burning 70% of OPEX during ramp-up, zero revenue
        cash_flow[m] = cash_flow[m-1] - (total_monthly_opex * 0.7)
    else:
        # Steady state operations
        cash_flow[m] = cash_flow[m-1] + monthly_ebitda

df_cashflow = pd.DataFrame({
    "Month": months,
    "Cumulative Cash Flow ($)": cash_flow
})

# Find Break-Even Month
break_even_month = df_cashflow[df_cashflow["Cumulative Cash Flow ($)"] >= 0]["Month"].min()
if pd.isna(break_even_month):
    break_even_text = "> 60 Months"
else:
    break_even_text = f"Month {int(break_even_month)}"

# Calculate maximum capital required (Valley of Death)
max_drawdown = df_cashflow["Cumulative Cash Flow ($)"].min()
working_capital_needed = abs(max_drawdown) - facility_capex

# ==========================================
# DASHBOARD METRICS
# ==========================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Capital Required (CAPEX + Working)", value=f"${abs(max_drawdown):,.0f}")
with col2:
    st.metric(label="Unit Cost per Urchin", value=f"${cost_per_urchin:.2f}")
with col3:
    st.metric(label="Steady-State Gross Margin", value=f"{gross_margin_pct:.1f}%")
with col4:
    st.metric(label="Capital Break-Even", value=break_even_text)

st.divider()

# ==========================================
# VISUALIZATIONS
# ==========================================
row1_col1, row1_col2 = st.columns([2, 1])

with row1_col1:
    # 1. Cumulative Cash Flow Chart (The Valley of Death)
    fig_cf = px.area(df_cashflow, x="Month", y="Cumulative Cash Flow ($)", 
                     title="5-Year Cumulative Cash Flow & Break-Even Analysis",
                     color_discrete_sequence=['#2E7D32'])
    
    # Add a horizontal line at $0 to show break-even
    fig_cf.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-Even $0")
    
    # Shade the "Valley of Death" below zero red, and above zero green
    fig_cf.update_traces(fill='tozeroy')
    fig_cf.update_layout(hovermode="x unified", yaxis_title="Cumulative Cash Flow (AUD)")
    st.plotly_chart(fig_cf, use_container_width=True)

with row1_col2:
    # 2. OPEX Breakdown Donut Chart
    opex_data = pd.DataFrame({
        "Category": ["Feed (Ulva)", "Labor & Mgmt", "Energy/Pumps", "Logistics/Packaging"],
        "Cost": [feed_cost, labor_cost, energy_cost, logistics_cost]
    })
    
    fig_opex = px.pie(opex_data, values="Cost", names="Category", hole=0.5,
                      title="Monthly OPEX Distribution",
                      color_discrete_sequence=px.colors.sequential.Teal)
    
    fig_opex.update_traces(textposition='inside', textinfo='percent+label')
    fig_opex.update_layout(showlegend=False)
    st.plotly_chart(fig_opex, use_container_width=True)

# ==========================================
# FINANCIAL SUMMARY EXPANDER & EXPORT
# ==========================================
with st.expander("View Detailed Financial Summary"):
    st.markdown(f"""
    ### 📊 Pro Forma Steady-State Snapshot (Annualized)
    * **Annual Revenue:** ${annual_revenue:,.2f}
    * **Annual Operating Expenses:** ${annual_opex:,.2f}
    * **Annual EBITDA:** ${(annual_revenue - annual_opex):,.2f}
    
    *Note: Simulation assumes a 12-month construction and biological ramp-up phase where OPEX is drawn down without corresponding harvest revenues.*
    """)

st.divider()
st.subheader("📥 Export Data")
st.markdown("Download the 60-month cash flow simulation to Microsoft Excel (CSV format).")

# Convert dataframe to CSV
csv_data = df_cashflow.to_csv(index=False).encode('utf-8')

# Create the download button
st.download_button(
    label="Download 5-Year Cash Flow Data (CSV)",
    data=csv_data,
    file_name="mugenuni_5_year_cashflow.csv",
    mime="text/csv",
)
