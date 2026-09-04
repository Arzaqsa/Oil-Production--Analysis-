import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Arzaq Pro - IPR", layout="wide", page_icon="🛢️")
st.markdown("""
<style>
.main-header {font-size:2.5rem; color:#1f77b4; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🛢️ Arzaq Pro</p>', unsafe_allow_html=True)
st.markdown('<p>Well Performance & IPR Analysis Dashboard</p>', unsafe_allow_html=True)
st.divider()

with st.sidebar:
    st.header("⚙️ Control Panel")
    Pr = st.number_input("Reservoir Pressure Pr (psi)", 1000.0, 15000.0, 5000.0, 100.0)
    Pb = st.number_input("Bubble Point Pb (psi)", 500.0, 10000.0, 3000.0, 100.0)
    re = st.number_input("Drainage Radius re (ft)", 100.0, 5000.0, 1000.0, 50.0)
    rw = st.number_input("Wellbore Radius rw (ft)", 0.1, 1.0, 0.3, 0.05)
    S = st.number_input("Skin Factor S", -5.0, 50.0, 0.0, 0.5)
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
PI = Q/(Pr-Pwf) if Pr!=Pwf else 0

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
    col3.metric("Efficiency", f"{efficiency:.2f}%")
    col4.metric("Flow Type", "Vogel" if Pwf < Pb else "Darcy")

with tab_curve:
    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(Q_vals, P_vals, 'b-', linewidth=2, label="IPR Curve")
    ax.plot(Q, Pwf, 'ro', markersize=10, label=f'Operating Point')
    ax.set_xlabel("Flow Rate Q (STB/day)"); ax.set_ylabel("Pressure (psi)")
    ax.set_title("IPR Curve"); ax.legend(); ax.grid(True)
    st.pyplot(fig)

with tab_diag:
    st.subheader("Well Diagnostics")
    st.write(f"**Productivity Index PI**: {PI:.3f} STB/day/psi")
    st.write(f"**Drawdown**: {Pr-Pwf:.0f} psi")

with tab_report:
    st.subheader("Generate PDF Report")
    if st.button("📄 Generate Report"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        y = 800
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, f"Arzaq Pro - Well Performance Report")
        y -= 30
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= 40
        
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "1. Input Parameters:")
        y -= 20
        c.setFont("Helvetica", 10)
        inputs = [f"Pr: {Pr} psi", f"Pb: {Pb} psi", f"Pwf: {Pwf} psi", f"Q: {Q} STB/day",
                  f"kh: {kh} mD.ft", f"mu: {mu} cp", f"Bo: {Bo} RB/STB", f"S: {S}", f"re: {re} ft", f"rw: {rw} ft"]
        for inp in inputs:
            c.drawString(70, y, f"- {inp}"); y -= 15
        
        y -= 10
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "2. Results:")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(70, y, f"- AOF: {AOF:.2f} STB/day"); y -= 15
        c.drawString(70, y, f"- Efficiency: {efficiency:.2f} %"); y -= 15
        c.drawString(70, y, f"- PI: {PI:.4f} STB/day/psi"); y -= 15
        c.drawString(70, y, f"- Flow Type: {'Vogel' if Pwf < Pb else 'Darcy'}")
        
        c.save()
        buffer.seek(0)
        st.download_button("⬇️ Download PDF", buffer, "Arzaq_Report.pdf", "application/pdf")
