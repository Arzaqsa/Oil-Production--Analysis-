import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Arzaq - IPR Calculator", layout="wide")
st.title("🛢️ Arzaq - IPR & Well Performance Calculator")
st.caption("Developed by Arzaq") 

st.sidebar.header("Input Parameters")

# --- INPUTS ---
Pr = st.sidebar.number_input("Reservoir Pressure Pr (psi)", 1000, 10000, 5000)
Pb = st.sidebar.number_input("Bubble Point Pressure Pb (psi)", 100, 10000, 3000)
Pwf = st.sidebar.number_input("Bottom Hole Pressure Pwf (psi)", 0, 10000, 1500)
kh = st.sidebar.number_input("Permeability-Thickness kh (mD.ft)", 100, 100000, 10000)
mu = st.sidebar.number_input("Viscosity mu (cp)", 0.1, 10.0, 1.0)
Bo = st.sidebar.number_input("Formation Volume Factor Bo (RB/STB)", 1.0, 2.0, 1.2)
re = st.sidebar.number_input("Drainage Radius re (ft)", 100, 5000, 1000)
rw = st.sidebar.number_input("Wellbore Radius rw (ft)", 0.1, 1.0, 0.3)
S = st.sidebar.number_input("Skin Factor S", -10.0, 50.0, 0.0)
Q = st.sidebar.number_input("Current Flow Rate Q (STB/day)", 0, 100000, 24043)

st.sidebar.markdown("---") 
st.sidebar.info("Built by Arzaq") # Removed heart

# --- CALCULATIONS ---
denom = mu * Bo * (np.log(re/rw) - 0.75 + S)
Q_calc = (0.00708 * kh * (Pr - Pwf)) / denom if denom > 0 else 0
AOF = (0.00708 * kh * Pr) / denom if denom > 0 else 0
PI = Q / (Pr - Pwf) if (Pr - Pwf) > 0 else 0

st.subheader("Results")
col1, col2, col3 = st.columns(3)
col1.metric("Calculated Q", f"{Q_calc:,.2f} STB/day")
col2.metric("AOF", f"{AOF:,.2f} STB/day")
col3.metric("Productivity Index PI", f"{PI:.3f} STB/day/psi")

# --- IPR CURVE: Auto Select Darcy or Vogel ---
st.subheader("IPR Curve")
pwf_plot = np.linspace(0, Pr, 100)

if Pwf >= Pb: # Single Phase - Use Darcy
    q_plot = (0.00708 * kh * (Pr - pwf_plot)) / denom
    curve_type = "Darcy - Single Phase"
    color = "blue"
else: # Two Phase - Use Vogel
    q_plot = AOF * (1 - 0.2 * (pwf_plot/Pr) - 0.8 * (pwf_plot/Pr)**2)
    curve_type = "Vogel - Two Phase"
    color = "orange"

fig, ax = plt.subplots()
ax.plot(q_plot, pwf_plot, label=f'{curve_type} IPR', color=color)
ax.scatter(Q, Pwf, color='red', s=100, zorder=5, label=f'Current: {Q:.0f} STB/day')
ax.set_xlabel('Flow Rate (STB/day)')
ax.set_ylabel('Bottomhole Pressure (psi)')
ax.set_title(f'Inflow Performance Relationship - {curve_type}')
ax.legend()
ax.grid(True)
ax.invert_yaxis()
st.pyplot(fig)

# --- PROFESSIONAL WARNING SYSTEM ---
st.subheader("Well Diagnostics")

# 1. Skin Factor Alert
if S > 20:
    st.error(f"⚠️ SEVERE FORMATION DAMAGE: Skin = {S:.1f}. Production loss >70%. Immediate stimulation required.")
elif S > 10:
    st.warning(f"⚠️ MODERATE DAMAGE: Skin = {S:.1f}. Consider Acidizing or Fracturing.")
elif S < 0:
    st.success(f"✅ STIMULATED WELL: Skin = {S:.1f}. Wellbore enhancement active.")

# 2. Drawdown Check
drawdown = Pr - Pwf
if drawdown > 0.5 * Pr:
    st.warning(f"⚠️ HIGH DRAWDOWN: {drawdown:.0f} psi. Risk of Water/Gas Coning.")
elif drawdown < 0.1 * Pr:
    st.info(f"ℹ️ LOW DRAWDOWN: {drawdown:.0f} psi. Sub-optimal production rate.")

# 3. Bubble Point Check
if Pwf < Pb:
    st.error(f"⚠️ BELOW BUBBLE POINT: Pwf={Pwf:.0f} psi < Pb={Pb:.0f} psi. Free gas present. Vogel IPR applied.")
else:
    st.success(f"✅ ABOVE BUBBLE POINT: Pwf={Pwf:.0f} psi > Pb={Pb:.0f} psi. Darcy IPR valid.")

# 4. Efficiency Check
efficiency = (Q / AOF) * 100 if AOF > 0 else 0
if efficiency < 20:
    st.warning(f"⚠️ LOW EFFICIENCY: Producing at {efficiency:.1f}% of AOF.")
else:
    st.info(f"ℹ️ WELL EFFICIENCY: {efficiency:.1f}% of AOF")

# 5. Productivity Index Check
if PI < 0.5:
    st.warning(f"⚠️ LOW PI: {PI:.3f} STB/day/psi. Poor well deliverability.")

# Footer
st.markdown("---")
st.markdown("<center>© 2026 Arzaq | Oil Well Analytics</center>", unsafe_allow_html=True)

