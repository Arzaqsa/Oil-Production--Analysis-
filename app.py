import streamlit as st
import math

st.set_page_config(page_title="Well Production Calculator", layout="centered")
st.title("Well Production Calculator")

st.subheader("Input Parameters")

col1, col2 = st.columns(2)
with col1:
    Pr = st.number_input("Reservoir Pressure Pr (psi)", value=3000.0)
    Pwf = st.number_input("Bottomhole Flowing Pressure Pwf (psi)", value=1500.0)
    kh = st.number_input("Permeability-Thickness kh (mD-ft)", value=10000.0)
    mu = st.number_input("Viscosity mu (cP)", value=0.5)

with col2:
    Bo = st.number_input("Oil Formation Volume Factor Bo (RB/STB)", value=1.2)
    re = st.number_input("Drainage Radius re (ft)", value=1000.0)
    rw = st.number_input("Wellbore Radius rw (ft)", value=0.3)
    S = st.number_input("Skin Factor S", value=0.0)

if st.button("Calculate Q (STB/day)", type="primary"):
    errors = []
    if Pr <= Pwf: errors.append("Pr must be greater than Pwf")
    if kh <= 0: errors.append("kh must be positive")
    if mu <= 0: errors.append("mu must be positive")
    if Bo <= 0: errors.append("Bo must be positive")
    if re <= rw: errors.append("re must be greater than rw")
    
    if errors:
        for e in errors: st.error(e)
    else:
        numerator = 0.00708 * kh * (Pr - Pwf)
        denominator = mu * Bo * (math.log(re/rw) - 0.75 + S)
        Q = numerator / denominator
        st.success(f"Calculated Flow Rate: {Q:.2f} STB/day")
        st.latex(r"Q = \frac{0.00708 \cdot k h \cdot (P_r - P_{wf})}{\mu \cdot B_o \cdot (\ln(\frac{r_e}{r_w}) - 0.75 + S)}")

st.caption("Based on Darcy Radial Flow Equation")
