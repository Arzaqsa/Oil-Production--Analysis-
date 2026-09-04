import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Arzaq Pro - IPR", layout="wide", page_icon="🛢️")

# CSS احترافي
st.markdown("""
<style>
    .main-header {font-size:2.5rem; color:#1f77b4; font-weight:700}
    .sub-header {font-size:1.2rem; color:#555}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🛢️ Arzaq Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Well Performance & IPR Analysis Dashboard</p>', unsafe_allow_html=True)
st.divider()

# ===================== SIDEBAR WITH TABS =====================
with st.sidebar:
    st.header("⚙️ Control Panel")
    
    tab1, tab2, tab3 = st.tabs(["📊 Inputs", "⚡ Presets", "ℹ️ About"])
    
    with tab1:
        st.subheader("Reservoir Data")
        with st.expander("▼ Reservoir Properties", expanded=True):
            Pr = st.number_input("Reservoir Pressure Pr (psi)", 1000.0, 15000.0, 5000.0, 100.0)
            Pb = st.number_input("Bubble Point Pb (psi)", 500.0, 10000.0, 3000.0, 100.0)
            re = st.number_input("Drainage Radius re (ft)", 100.0, 5000.0, 1000.0, 50.0)
        
        st.subheader("Well & Fluid Data")
        with st.expander("▼ Well Geometry", expanded=False):
            rw = st.number_input("Wellbore Radius rw (ft)", 0.1, 1.0, 0.3, 0.05)
            S = st.number_input("Skin Factor S", -5.0, 50.0, 0.0, 0.5)
        
        with st.expander("▼ Fluid Properties", expanded=False):
            kh = st.number_input("Permeability-Thickness kh (mD.ft)", 1000.0, 100000.0, 10000.0, 500.0)
            mu = st.number_input("Viscosity mu (cp)", 0.1, 10.0, 1.0, 0.1)
            Bo = st.number_input("Formation Volume Factor Bo (RB/STB)", 1.0, 3.0, 1.2, 0.05)
        
        st.subheader("Operating Conditions")
        Pwf = st.slider("Bottom Hole Pressure Pwf (psi)", 0.0, Pr, 800.0, 50.0)
        Q = st.number_input("Current Flow Rate Q (STB/day)", 0.0, 100000.0, 36065.0, 500.0)
    
    with tab2:
        st.subheader("Quick Load Presets")
        if st.button("🟢 Light Oil Well"):
            st.session_state.update({'Pr':5000,'Pb':3000,'kh':15000,'mu':0.8,'Bo':1.25})
            st.rerun()
        if st.button("🟠 Heavy Oil Well"):
            st.session_state.update({'Pr':4000,'Pb':2000,'kh':5000,'mu':5.0,'Bo':1.1})
            st.rerun()
        if st.button("🔵 Gas Well"):
            st.session_state.update({'Pr':6000,'Pb':6000,'kh':20000,'mu':0.02,'Bo':0.005})
            st.rerun()
    
    with tab3:
        st.info("Arzaq Pro v1.1\nDeveloped for IPR Analysis\nSupports Darcy & Vogel")

# ===================== VALIDATION =====================
if Pwf > Pr:
    st.error("❌ Error: Pwf cannot be greater than Pr")
    st.stop()

# ===================== CALCULATIONS =====================
pi = np.pi
AOF = (kh * (Pr**2 - Pb**2)) / (141.2 * Bo * mu * (np.log(re/rw) - 0.75 + S)) / 1000 if Pb < Pr else 0
efficiency = (Q / AOF * 1000) * 100 if AOF > 0 else 0

# IPR Curve
P_vals = np.linspace(0, Pr, 100)
Q_vals = []
for P in P_vals:
    if P >= Pb:
        Qp = (kh * (Pr - P)) / (141.2 * Bo * mu * (np.log(re/rw) + S))
    else:
        Qb = (kh * (Pr - Pb)) / (141.2 * Bo * mu * (np.log(re/rw) + S))
        Qp = Qb + (AOF*1000 - Qb) * (1 - 0.2*(P/Pb) - 0.8*(P/Pb)**2)
    Q_vals.append(max(0, Qp))

# ===================== MAIN TABS =====================
tab_dash, tab_curve, tab_diag = st.tabs(["📊 Dashboard", "📈 IPR Curve", "🔍 Diagnostics"])

with tab_dash:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AOF", f"{AOF:.1f} STB/day")
    col2.metric("Current Q", f"{Q:.0f} STB/day")
    col3.metric("Efficiency", f"{efficiency:.1f}%")
    col4.metric("Pwf/Pb Ratio", f"{Pwf/Pb:.2f}")

with tab_curve:
    fig, ax = plt.subplots(figsize=(10,6))
    color = 'blue' if Pwf >= Pb else 'orange'
    ax.plot(Q_vals, P_vals, color=color, linewidth=2.5, label='IPR Curve')
    ax.scatter(Q, Pwf, color='red', s=100, zorder=5, label='Operating Point')
    ax.set_xlabel("Flow Rate (STB/day)"); ax.set_ylabel("Pressure (psi)")
    ax.legend(); ax.grid(True, alpha=0.3); ax.invert_yaxis()
    st.pyplot(fig)

with tab_diag:
    if Pwf >= Pb:
        st.success(f"✅ DARCY FLOW: Pwf={Pwf:.0f} > Pb={Pb:.0f}. Single Phase")
    else:
        st.warning(f"⚠️ VOGEL FLOW: Pwf={Pwf:.0f} < Pb={Pb:.0f}. Free Gas Present")
    st.metric("Well Efficiency vs AOF", f"{efficiency:.1f}%")

st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
