import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(page_title="Valuation & Exit", layout="wide")

st.title("🤝 Valuation & Investor Exit Calculator")
st.markdown("""
This module models the equity split based on the Pre-Money Valuation of Mugenuni Research Pty Ltd's Intellectual Property 
and projects the potential Return on Investment (ROI) for incoming capital at a future liquidity event (e.g., Year 6 buyout).
""")
st.divider()

# ==========================================
# SIDEBAR PARAMETERS (The "Fiddle" Levers)
# ==========================================
st.sidebar.header("1. Company Valuation")
ip_value = st.sidebar.number_input("Mugenuni IP & Sweat Equity ($ Pre-Money)", min_value=0, value=2500000, step=100000)

st.sidebar.header("2. Capital Raise")
capital_raise = st.sidebar.number_input("Capital Required ($)", min_value=500000, value=4400000, step=100000)

st.sidebar.header("3. Year 6 Exit Assumptions")
# Defaulting to a conservative multiple of the steady-state EBITDA from the Financial Engine
projected_ebitda = st.sidebar.number_input("Projected Year 6 EBITDA ($)", value=3200000, step=100000)
exit_multiple = st.sidebar.slider("Industry Exit Multiple (x EBITDA)", min_value=2.0, max_value=15.0, value=6.0, step=0.5)

# ==========================================
# EQUITY CALCULATIONS
# ==========================================
post_money_valuation = ip_value + capital_raise

if post_money_valuation > 0:
    investor_equity_pct = capital_raise / post_money_valuation
    founder_equity_pct = ip_value / post_money_valuation
else:
    investor_equity_pct = 0
    founder_equity_pct = 0

# ==========================================
# EXIT PAYOUT CALCULATIONS (Year 6)
# ==========================================
total_exit_value = projected_ebitda * exit_multiple
investor_payout = total_exit_value * investor_equity_pct
founder_payout = total_exit_value * founder_equity_pct

# Investor ROI Metrics
if capital_raise > 0:
    investor_profit = investor_payout - capital_raise
    roi_percentage = (investor_profit / capital_raise) * 100
    moic = investor_payout / capital_raise  # Multiple on Invested Capital
else:
    roi_percentage = 0
    moic = 0

# ==========================================
# DASHBOARD DISPLAY
# ==========================================
st.markdown("### 🏛️ The Equity Split (Post-Money)")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Post-Money Valuation", f"${post_money_valuation:,.0f}")
with col2:
    st.metric("Investor Equity", f"{investor_equity_pct * 100:.1f}%")
with col3:
    st.metric("Mugenuni (Founders) Equity", f"{founder_equity_pct * 100:.1f}%")

st.divider()

st.markdown("### 🚀 Year 6 Liquidity Event (Buyout)")
col4, col5, col6, col7 = st.columns(4)

with col4:
    st.metric("Total Enterprise Exit Value", f"${total_exit_value:,.0f}")
with col5:
    st.metric("Investor Gross Payout", f"${investor_payout:,.0f}")
with col6:
    st.metric("Investor ROI", f"{roi_percentage:,.0f}%")
with col7:
    st.metric("Cash Multiple (MOIC)", f"{moic:.1f}x")

# ==========================================
# VISUALIZATION
# ==========================================
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    # Equity Split Donut Chart
    equity_data = pd.DataFrame({
        "Party": ["Mugenuni (IP & Sweat Equity)", "New Investors"],
        "Value": [ip_value, capital_raise]
    })
    
    fig_equity = px.pie(equity_data, values="Value", names="Party", hole=0.5,
                        title="Post-Money Equity Distribution",
                        color_discrete_sequence=['#1f77b4', '#2ca02c'])
    
    fig_equity.update_traces(textposition='inside', textinfo='percent+label')
    fig_equity.update_layout(showlegend=False)
    st.plotly_chart(fig_equity, use_container_width=True)

with row1_col2:
    # Exit Payout Bar Chart
    payout_data = pd.DataFrame({
        "Party": ["Mugenuni Founders", "New Investors"],
        "Payout ($)": [founder_payout, investor_payout]
    })
    
    fig_payout = px.bar(payout_data, x="Party", y="Payout ($)", 
                        title="Year 6 Exit Payout Distribution",
                        text_auto='.2s',
                        color="Party",
                        color_discrete_sequence=['#1f77b4', '#2ca02c'])
    
    fig_payout.update_layout(showlegend=False, yaxis_title="Payout Value (AUD)")
    st.plotly_chart(fig_payout, use_container_width=True)
