import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Arzaq Pro - IPR", layout="wide", page_icon="🛢️")
st.session_state.clear()

st.markdown('<p class="main-header">🛢️ Arzaq Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Well Performance & IPR Analysis Dashboard</p>', unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("⚙️ Control Panel")
    Pr = st.number_input("Reservoir Pressure Pr (psi)", 1000.0, 15000.0, 5000.0, 100.0)
    Pb = st.number_input("Bubble Point Pb (psi)", 500.0, 10000.0, 3000.0, 100.0) # خليه 3000
    re = st.number_input("Drainage Radius re (ft)", 100.0, 5000.0, 1000.0, 50.0)
    rw = st.number_input("Wellbore Radius rw (ft)", 0.1, 1.0, 0.3, 0.05)
    S = st.number_input("Skin Factor S", -5.0, 50.0, 0.0, 0.5) # خليه 0
    kh = st.number_input("Permeability-Thickness kh (mD.ft)", 1000.0, 100000.0, 10000.0, 500.0)
    mu = st.number_input("Viscosity mu (cp)", 0.1, 10.0, 1.0, 0.1)
    Bo = st.number_input("Formation Volume Factor Bo (RB/STB)", 1.0, 3.0, 1.2, 0.05)
    Pwf = st.slider("Bottom Hole Pressure Pwf (psi)", 0.0, Pr, 3300.0, 50.0)
    Q = st.number_input("Current Flow Rate Q (STB/day)", 0.0, 200000.0, 36065.0, 500.0)

if Pwf > Pr: 
    st.error("Error: Pwf cannot be greater than Pr")
    st.stop()

denom = 141.2 * Bo * mu * (np.log(re/rw) - 0.75 + S)

if Pb < Pr:
    AOF = (kh * (Pr**2 - Pb**2)) / denom
else:
    AOF = (kh * Pr) / (141.2 * Bo * mu * (np.log(re/rw) + S))

efficiency = (Q / AOF) * 100 if AOF > 0 else 0

# للتشخيص
st.sidebar.write(f"Debug: AOF={AOF:.1f}, Denom={denom:.2f}")

P_vals = np.linspace(0, Pr, 100)
Q_vals = []
for P in P_vals:
    if P >= Pb: 
        Qp = (kh * (Pr - P)) / (141.2 * Bo * mu * (np.log(re/rw) + S))
    else: 
        Qb = (kh * (Pr - Pb)) / (141.2 * Bo * mu * (np.log(re/rw) + S))
        Qp = Qb + (AOF - Qb) * (1 - 0.2*(P/Pb) - 0.8*(P/Pb)**2)
    Q_vals.append(max(0, Qp))

tab_dash, tab_curve, tab_diag, tab_report = st.tabs(["📊 Dashboard", "📈 IPR Curve", "🔍 Diagnostics", "📄 Report"])

with tab_dash:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AOF", f"{AOF:.1f} STB/day")
    col2.metric("Current Q", f"{Q:.0f} STB/day")
    col3.metric("Efficiency", f"{efficiency:.2f}%") # خليتها 2 خانات
    col4.metric("Flow Type", "Vogel" if Pwf < Pb else "Darcy")
