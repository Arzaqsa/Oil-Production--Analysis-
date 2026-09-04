import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4

st.set_page_config(page_title="Arzaq Pro - IPR", layout="wide", page_icon="🛢️")

# CSS احترافي
st.markdown("""
<style>
    .main-header {font-size:2.5rem; color:#0D47A1; font-weight:700}
    .sub-header {font-size:1.1rem; color:#555}
    div[data-testid="metric-container"] {background-color: #E3F2FD; padding: 10px; border-radius: 10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">🛢️ Arzaq Pro</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Well Performance & IPR Analysis Dashboard</p>', unsafe_allow_html=True)
st.divider()

# ===================== SIDEBAR =====================
with st.sidebar:
    st.header("⚙️ Control Panel")
    tab1, tab2, tab3 = st.tabs(["📊 Inputs", "⚡ Presets", "ℹ️ About"])
    
    with tab1:
        with st.expander("▼ Reservoir Properties", expanded=True):
            Pr = st.number_input("Reservoir Pressure Pr (psi)", 1000.0, 15000.0, 5000.0, 100.0)
            Pb = st.number_input("Bubble Point Pb (psi)", 500.0, 10000.0, 3000.0, 100.0)
            re = st.number_input("Drainage Radius re (ft)", 100.0, 5000.0, 1000.0, 50.0)
        with st.expander("▼ Well Geometry"):
            rw = st.number_input("Wellbore Radius rw (ft)", 0.1, 1.0, 0.3, 0.05)
            S = st.number_input("Skin Factor S", -5.0, 50.0, 0.0, 0.5)
        with st.expander("▼ Fluid Properties"):
            kh = st.number_input("Permeability-Thickness kh (mD.ft)", 1000.0, 100000.0, 10000.0, 500.0)
            mu = st.number_input("Viscosity mu (cp)", 0.1, 10.0, 1.0, 0.1)
            Bo = st.number_input("Formation Volume Factor Bo (RB/STB)", 1.0, 3.0, 1.2, 0.05)
        
        st.subheader("Operating Conditions")
        Pwf = st.slider("Bottom Hole Pressure Pwf (psi)", 0.0, Pr, 800.0, 50.0)
        Q = st.number_input("Current Flow Rate Q (STB/day)", 0.0, 200000.0, 36065.0, 500.0)
    
    with tab2:
        if st.button("🟢 Light Oil Well"): 
            st.session_state.update({'Pr':5000,'Pb':3000,'kh':15000,'mu':0.8,'Bo':1.25})
            st.rerun()
        if st.button("🟠 Heavy Oil Well"):
            st.session_state.update({'Pr':4000,'Pb':2000,'kh':5000,'mu':5.0,'Bo':1.1})
            st.rerun()

# ===================== VALIDATION & CALC =====================
if Pwf > Pr: 
    st.error("❌ Error: Pwf cannot be greater than Pr")
    st.stop()

pi = np.pi
denom = 141.2 * Bo * mu * (np.log(re/rw) - 0.75 + S)

# نحسب AOF كامل بدون قسمة 1000
AOF_full = (kh * (Pr**2 - Pb**2)) / denom if Pb < Pr else (kh * Pr) / (141.2 * Bo * mu * (np.log(re/rw) + S))
AOF = AOF_full / 1000  # للعرض فقط بالالف

efficiency = (Q / AOF_full) * 100 if AOF_full > 0 else 0  # <-- هنا التعديل

# IPR Curve
P_vals = np.linspace(0, Pr, 100)
Q_vals = []
for P in P_vals:
    if P >= Pb: 
        Qp = (kh * (Pr - P)) / (141.2 * Bo * mu * (np.log(re/rw) + S))
    else: 
        Qb = (kh * (Pr - Pb)) / (141.2 * Bo * mu * (np.log(re/rw) + S))
        Qp = Qb + (AOF_full - Qb) * (1 - 0.2*(P/Pb) - 0.8*(P/Pb)**2)  # <-- استخدمنا AOF_full
    Q_vals.append(max(0, Qp))

# ===================== PDF FUNCTION =====================
def create_pdf():
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    c.setFont("Helvetica-Bold", 18); c.drawString(50, 800, "Arzaq Pro - IPR Report")
    c.setFont("Helvetica", 10); c.drawString(50, 780, f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    c.line(50, 770, 550, 770)
    y = 740
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Input Parameters:"); y -= 20
    c.setFont("Helvetica", 10)
    inputs = [f"Pr = {Pr} psi", f"Pb = {Pb} psi", f"Pwf = {Pwf} psi", f"Q = {Q} STB/day", f"AOF = {AOF:.1f} STB/day", f"Efficiency = {efficiency:.1f}%"]
    for i in inputs: c.drawString(70, y, i); y -= 15
    y -= 20
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Diagnosis:")
    flow = "VOGEL - Two Phase Flow" if Pwf < Pb else "DARCY - Single Phase Flow"
    c.setFont("Helvetica", 10); c.drawString(70, y-15, flow)
    y -= 30
    c.setFont("Helvetica-Bold", 12); c.drawString(50, y, "Recommendation:")
    if efficiency > 80: rec = "Well is operating efficiently >80%."
    elif efficiency > 50: rec = "Well performance is good. Monitor closely."
    else: rec = "Consider well stimulation to improve productivity."
    c.setFont("Helvetica", 10); c.drawString(70, y-15, rec)
    c.save()
    buffer.seek(0)
    return buffer

# ===================== MAIN TABS =====================
tab_dash, tab_curve, tab_diag, tab_report = st.tabs(["📊 Dashboard", "📈 IPR Curve", "🔍 Diagnostics", "📄 Report"])

with tab_dash:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("AOF", f"{AOF:.1f} STB/day")
    col2.metric("Current Q", f"{Q:.0f} STB/day")
    col3.metric("Efficiency", f"{efficiency:.1f}%")
    col4.metric("Flow Type", "Vogel" if Pwf < Pb else "Darcy")

with tab_curve:
    fig, ax = plt.subplots(figsize=(10,6))
    max_x = max(max(Q_vals), Q) * 1.1  
    color = 'orange' if Pwf < Pb else 'blue'
    ax.plot(Q_vals, P_vals, color=color, linewidth=2.5, label='IPR Curve')
    ax.scatter(Q, Pwf, color='red', s=120, zorder=5, label='Operating Point')
    ax.set_xlim(0, max_x)
    ax.set_xlabel("Flow Rate (STB/day)"); ax.set_ylabel("Pressure (psi)")
    ax.legend(); ax.grid(True, alpha=0.3); ax.invert_yaxis()
    st.pyplot(fig)

with tab_diag:
    if Pwf >= Pb: st.success(f"✅ DARCY FLOW: Single Phase Above Pb")
    else: st.warning(f"⚠️ VOGEL FLOW: Two Phase Below Pb")
    st.progress(min(efficiency/100, 1.0))

with tab_report:
    st.subheader("📄 Generate Professional Report")
    st.write("Click the button below to download a professional PDF report with all inputs, results, and recommendations.")
    pdf_file = create_pdf()
    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_file,
        file_name=f"Arzaq_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        mime="application/pdf"
    )

st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
