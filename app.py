import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Z1- IPR", layout="wide", page_icon="🛢️")
st.markdown("""
<style>
.main-header {font-size:2.5rem; color:#1f77b4; font-weight:bold;}
.sub-header {font-size:1.2rem; color:#666;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🛢️ Z1</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Well Performance & IPR Analysis Dashboard</p>', unsafe_allow_html=True)
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
    # شلنا Q اليدوي

if Pwf > Pr: 
    st.error("Error: Pwf cannot be greater than Pr")
    st.stop()

# ====== CALCULATIONS - معادلة Darcy المصححة ======
denom = 141.2 * Bo * mu * (np.log(re/rw) - 0.75 + S)
PI = kh / denom  # Productivity Index
AOF = PI * Pr    # AOF = PI * Pr للـ Darcy Flow

# نحسب Q تلقائي من Pwf
Q_calculated = PI * (Pr - Pwf)  
Q_calculated = max(0, Q_calculated) # عشان ما يطلع سالب

efficiency = (Q_calculated / AOF) * 100 if AOF > 0 else 0
drawdown = Pr - Pwf

# ====== IPR CURVE ======
P_vals = np.linspace(0, Pr, 100)
Q_vals = PI * (Pr - P_vals)  # معادلة Darcy الخطية

tab_dash, tab_curve, tab_diag, tab_report = st.tabs(["📊 Dashboard", "📈 IPR Curve", "🔍 Diagnostics", "📄 Report"])

with tab_dash:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AOF", f"{AOF:,.1f} STB/day")
    col2.metric("Calculated Q", f"{Q_calculated:,.0f} STB/day") # غيرنا الاسم
    col3.metric("Efficiency", f"{efficiency:.2f}%")
    col4.metric("PI", f"{PI:.4f} STB/d/psi")
    
    if Pwf > Pb:
        st.success(f"Flow Regime: Darcy Single Phase - Pwf > Pb")
    else:
        st.warning(f"Flow Regime: Below Pb. Use Arzaq Nodal for accuracy")

with tab_curve:
    fig, ax = plt.subplots(figsize=(10,6))
    ax.plot(Q_vals, P_vals, 'b-', linewidth=2.5, label="IPR Curve - Darcy")
    ax.plot(Q_calculated, Pwf, 'ro', markersize=12, label=f'Operating Point: Q={Q_calculated:,.0f}, Pwf={Pwf:.0f}') # استخدمنا المحسوب
    ax.axhline(y=Pb, color='g', linestyle='--', label=f'Bubble Point Pb={Pb} psi')
    ax.set_xlabel("Flow Rate Q (STB/day)", fontsize=12)
    ax.set_ylabel("Pressure (psi)", fontsize=12)
    ax.set_title("Inflow Performance Relationship - IPR", fontsize=14, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    ax.invert_yaxis()
    st.pyplot(fig)

with tab_diag:
    st.subheader("Well Diagnostics")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Drawdown", f"{drawdown:.0f} psi")
        st.metric("AOF", f"{AOF:,.1f} STB/day")
    with col2:
        st.metric("Calculated Q", f"{Q_calculated:,.0f} STB/day") # استخدمنا المحسوب
        st.metric("Efficiency", f"{efficiency:.2f}%")
    
    if efficiency < 50:
        st.warning("Low Efficiency: Well may need stimulation")
    elif efficiency < 80:
        st.info("Medium Efficiency")
    else:
        st.success("High Efficiency")

with tab_report:
    st.subheader("Generate PDF Report")
    if st.button("📄 Generate Full Report"):
        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        y = 800
        
        # Header
        c.setFont("Helvetica-Bold", 18)
        c.drawString(50, y, "Z1- Well Performance Report")
        y -= 25
        c.setFont("Helvetica", 10)
        c.drawString(50, y, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        y -= 35
        
        # Inputs
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "1. Input Parameters")
        y -= 20
        c.setFont("Helvetica", 10)
        inputs = [
            f"Reservoir Pressure Pr: {Pr:.0f} psi",
            f"Bubble Point Pb: {Pb:.0f} psi", 
            f"Bottom Hole Pressure Pwf: {Pwf:.0f} psi",
            f"Calculated Flow Rate Q: {Q_calculated:,.0f} STB/day", # عدلناه
            f"Permeability-Thickness kh: {kh:,.0f} mD.ft",
            f"Viscosity mu: {mu:.2f} cp",
            f"Formation Volume Factor Bo: {Bo:.2f} RB/STB",
            f"Skin Factor S: {S:.1f}",
            f"Drainage Radius re: {re:.0f} ft",
            f"Wellbore Radius rw: {rw:.2f} ft"
        ]
        for inp in inputs:
            c.drawString(70, y, f"• {inp}"); y -= 15
        
        y -= 15
        # Results
        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y, "2. Results")
        y -= 20
        c.setFont("Helvetica", 10)
        c.drawString(70, y, f"• Productivity Index PI: {PI:.4f} STB/day/psi"); y -= 15
        c.drawString(70, y, f"• Absolute Open Flow AOF: {AOF:,.2f} STB/day"); y -= 15
        c.drawString(70, y, f"• Well Efficiency: {efficiency:.2f} %"); y -= 15
        c.drawString(70, y, f"• Drawdown: {drawdown:.0f} psi"); y -= 15
        c.drawString(70, y, f"• Flow Regime: Darcy Single Phase")
        
        c.save()
        buffer.seek(0)
        st.download_button("⬇️ Download PDF Report", buffer, "Z1_Report.pdf", "application/pdf")
