
from pathlib import Path
from datetime import datetime
import random

import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# CONFIGURATION
# =========================================================
st.set_page_config(
    page_title="AirMind AI | Smart Comfort Intelligence",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "models" / "airmind_model.joblib"

# =========================================================
# THEME
# =========================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}
.stApp {
    background: #0b1020;
    color: #edf2ff;
}
[data-testid="stSidebar"] {
    background: #11182b;
    border-right: 1px solid #27314a;
}
[data-testid="stMetric"] {
    background: linear-gradient(145deg,#151f35,#10182a);
    border: 1px solid #283650;
    padding: 18px;
    border-radius: 15px;
}
[data-testid="stMetricLabel"] {
    color: #9baac6;
}
[data-testid="stMetricValue"] {
    color: #f3f6ff;
}
h1, h2, h3 {
    color: #f4f7ff !important;
}
p, label {
    color: #b9c5db;
}
.hero {
    padding: 26px 28px;
    border: 1px solid #34415c;
    border-radius: 20px;
    background: linear-gradient(120deg,#172641,#11182a 70%);
    margin-bottom: 22px;
}
.eyebrow {
    color: #f2c76b;
    text-transform: uppercase;
    letter-spacing: 2px;
    font-size: 11px;
    font-weight: 800;
}
.hero-title {
    font-size: 34px;
    font-weight: 800;
    letter-spacing: -1px;
    color: #ffffff;
    margin: 6px 0;
}
.hero-sub {
    font-size: 14px;
    color: #b8c6dd;
}
.panel {
    padding: 20px;
    background: #111a2d;
    border: 1px solid #283650;
    border-radius: 16px;
    margin-bottom: 12px;
}
.speed {
    font-size: 34px;
    font-weight: 800;
    color: #f2c76b;
    margin: 4px 0;
}
.small {
    font-size: 12px;
    color: #91a1bf;
}
.status {
    display: inline-block;
    background: #24344b;
    color: #c6d7ef;
    padding: 5px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
}
div.stButton > button {
    background: #e9bd5a;
    color: #10182a;
    border: none;
    border-radius: 10px;
    font-weight: 800;
    min-height: 42px;
}
div.stButton > button:hover {
    background: #ffd77e;
    color: #10182a;
    border: none;
}
hr {
    border-color: #283650;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD MODEL
# =========================================================
@st.cache_resource
def load_saved_model():
    saved = joblib.load(MODEL_PATH)
    return saved["model"], saved["features"]

if not MODEL_PATH.exists():
    st.error("Trained model not found. Run `python train_model.py` first.")
    st.stop()

model, features = load_saved_model()

# =========================================================
# SESSION STATE
# =========================================================
if "history" not in st.session_state:
    st.session_state.history = []

if "temperature" not in st.session_state:
    st.session_state.temperature = 30.0

if "humidity" not in st.session_state:
    st.session_state.humidity = 65

if "occupied" not in st.session_state:
    st.session_state.occupied = True

if "preference" not in st.session_state:
    st.session_state.preference = "Balanced"

if "manual_mode" not in st.session_state:
    st.session_state.manual_mode = False

if "manual_speed" not in st.session_state:
    st.session_state.manual_speed = "Medium"

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("## 🌬️ AirMind AI")
    st.caption("SMART COMFORT INTELLIGENCE")
    st.divider()

    st.markdown("### Environmental inputs")

    st.slider(
        "Temperature (°C)", 18.0, 40.0, 30.0, 0.5,
        key="temperature"
    )
    st.slider(
        "Relative humidity (%)", 20, 95, 65,
        key="humidity"
    )

    st.toggle("Room occupancy detected", key="occupied")

    st.selectbox(
        "Comfort preference",
        ["Energy-conscious", "Balanced", "More airflow"],
        key="preference",
    )

    st.divider()
    st.markdown("### Control settings")

    st.toggle("Enable manual override", key="manual_mode")

    if st.session_state.manual_mode:
        st.selectbox(
            "Requested speed",
            ["Off", "Low", "Medium", "High"],
            key="manual_speed",
        )

    st.caption(
        "Demo mode: inputs are simulated manually. "
        "No physical fan is connected."
    )

    if st.button("🎲 Simulate new room conditions", use_container_width=True):
        st.session_state.temperature = round(random.uniform(22, 38), 1)
        st.session_state.humidity = random.randint(35, 85)
        st.session_state.occupied = random.choice([True, True, False])
        st.rerun()

# =========================================================
# MODEL INPUT AND PREDICTION
# =========================================================
preference_map = {
    "Energy-conscious": 0,
    "Balanced": 1,
    "More airflow": 2,
}

input_df = pd.DataFrame([{
    "temperature": st.session_state.temperature,
    "humidity": st.session_state.humidity,
    "occupied": int(st.session_state.occupied),
    "comfort_preference": preference_map[st.session_state.preference],
}])[features]

# The trained model predicts the speed category.
ml_prediction = str(model.predict(input_df)[0])
probabilities = model.predict_proba(input_df)[0]

# Apply a separate safety policy to the final recommendation.
# Vacancy shutoff is a software policy, not a hardware safety guarantee.
if not st.session_state.occupied:
    recommended_speed = "Off"
    decision_reason = "Room marked vacant: the software policy recommends Off."
elif st.session_state.manual_mode:
    recommended_speed = st.session_state.manual_speed
    decision_reason = "Manual override is active. The user-selected speed takes priority."
else:
    recommended_speed = ml_prediction
    decision_reason = (
        f"The model recommends {ml_prediction} based on the current "
        "environmental inputs and selected preference."
    )

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <div class="eyebrow">ATOMQUEST 2026 · TRACK 1</div>
    <div class="hero-title">AirMind AI</div>
    <div class="hero-sub">
        Context-aware fan intelligence · Environmental monitoring ·
        Explainable machine learning
    </div>
</div>
""", unsafe_allow_html=True)

left, right = st.columns([3, 1])
with left:
    st.markdown("### System overview")
    st.caption("Current scenario · Values are simulated, not live sensor readings")
with right:
    st.markdown(
        '<div style="text-align:right"><span class="status">'
        '● SOFTWARE DEMO</span></div>',
        unsafe_allow_html=True,
    )

# =========================================================
# KPI CARDS
# =========================================================
k1, k2, k3, k4 = st.columns(4)

k1.metric("Temperature", f"{st.session_state.temperature:.1f} °C")
k2.metric("Humidity", f"{st.session_state.humidity}%")
k3.metric(
    "Occupancy",
    "Occupied" if st.session_state.occupied else "Vacant",
)
k4.metric("ML prediction", ml_prediction)

st.markdown("")

# =========================================================
# MAIN CONTENT
# =========================================================
left_col, right_col = st.columns([1.15, 1])

with left_col:
    st.markdown("### Fan intelligence")

    st.markdown(
        f"""
        <div class="panel">
            <div class="eyebrow">FINAL SPEED RECOMMENDATION</div>
            <div class="speed">◉ {recommended_speed}</div>
            <div class="small">{decision_reason}</div>
            <hr>
            <div class="small">
                ML output: <b>{ml_prediction}</b><br>
                Control policy: <b>{
                    "Manual override" if st.session_state.manual_mode
                    else "Vacancy policy" if not st.session_state.occupied
                    else "Model recommendation"
                }</b>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("#### Why this decision?")

    reasons = []

    if not st.session_state.occupied:
        reasons.append("• Occupancy is marked vacant.")
    else:
        reasons.append("• The room is marked occupied.")

    if st.session_state.temperature >= 30:
        reasons.append("• Temperature is relatively high in the selected scenario.")
    elif st.session_state.temperature <= 23:
        reasons.append("• Temperature is relatively low in the selected scenario.")
    else:
        reasons.append("• Temperature is within the middle of the available input range.")

    if st.session_state.humidity >= 70:
        reasons.append("• Humidity is high in the selected scenario.")

    if st.session_state.manual_mode:
        reasons.append("• Manual override replaces the model recommendation.")

    for reason in reasons:
        st.markdown(reason)

    st.caption(
        "These are input-based explanations, not causal explanations "
        "of the Random Forest prediction."
    )

with right_col:
    st.markdown("### Environmental snapshot")

    gauge1, gauge2 = st.columns(2)

    with gauge1:
        fig_t = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.temperature,
            number={"suffix": " °C", "font": {"color": "#f4f7ff"}},
            title={"text": "Temperature", "font": {"color": "#b9c5db"}},
            gauge={
                "axis": {"range": [18, 40], "tickcolor": "#9baac6"},
                "bar": {"color": "#e9bd5a"},
                "bgcolor": "#111a2d",
                "bordercolor": "#283650",
                "steps": [
                    {"range": [18, 24], "color": "#24344b"},
                    {"range": [24, 32], "color": "#33405a"},
                    {"range": [32, 40], "color": "#4a3541"},
                ],
            },
        ))
        fig_t.update_layout(
            height=220, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#f4f7ff",
        )
        st.plotly_chart(fig_t, use_container_width=True)

    with gauge2:
        fig_h = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.humidity,
            number={"suffix": "%", "font": {"color": "#f4f7ff"}},
            title={"text": "Humidity", "font": {"color": "#b9c5db"}},
            gauge={
                "axis": {"range": [20, 95], "tickcolor": "#9baac6"},
                "bar": {"color": "#73b7ee"},
                "bgcolor": "#111a2d",
                "bordercolor": "#283650",
                "steps": [
                    {"range": [20, 45], "color": "#24344b"},
                    {"range": [45, 70], "color": "#33405a"},
                    {"range": [70, 95], "color": "#4a3541"},
                ],
            },
        ))
        fig_h.update_layout(
            height=220, margin=dict(l=10, r=10, t=40, b=10),
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#f4f7ff",
        )
        st.plotly_chart(fig_h, use_container_width=True)

# =========================================================
# MODEL SCORES
# =========================================================
st.divider()
st.markdown("### Model prediction scores")
st.caption(
    "Scores are model outputs for the synthetic training task. "
    "They are not probabilities of human comfort."
)

prob_df = pd.DataFrame({
    "Fan speed": model.classes_,
    "Score (%)": probabilities * 100,
}).sort_values("Score (%)", ascending=True)

fig_p = go.Figure(go.Bar(
    x=prob_df["Score (%)"],
    y=prob_df["Fan speed"],
    orientation="h",
    marker_color=[
        "#e9bd5a" if name == ml_prediction else "#40516f"
        for name in prob_df["Fan speed"]
    ],
    text=[f"{v:.1f}%" for v in prob_df["Score (%)"]],
    textposition="outside",
))
fig_p.update_layout(
    height=280,
    xaxis=dict(range=[0, 115], title="Model score (%)"),
    yaxis_title="",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font_color="#dce5f5",
    margin=dict(l=20, r=30, t=10, b=30),
)
st.plotly_chart(fig_p, use_container_width=True)

# =========================================================
# FEATURE IMPORTANCE
# =========================================================
st.markdown("### What influences the model?")

if hasattr(model, "feature_importances_"):
    importance_df = pd.DataFrame({
        "Input feature": features,
        "Importance": model.feature_importances_,
    }).sort_values("Importance", ascending=True)

    fig_i = go.Figure(go.Bar(
        x=importance_df["Importance"],
        y=importance_df["Input feature"],
        orientation="h",
        marker_color="#73b7ee",
        text=[f"{v:.3f}" for v in importance_df["Importance"]],
        textposition="outside",
    ))
    fig_i.update_layout(
        height=280,
        xaxis_title="Relative feature importance",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dce5f5",
        margin=dict(l=20, r=40, t=10, b=30),
    )
    st.plotly_chart(fig_i, use_container_width=True)

    st.caption(
        "Feature importance measures how the fitted model uses each input. "
        "It does not prove that changing that input causes a particular outcome."
    )

# =========================================================
# HISTORY
# =========================================================
st.divider()
st.markdown("### Session history")

if st.button("＋ Record current scenario", use_container_width=False):
    st.session_state.history.append({
        "Time": datetime.now().strftime("%H:%M:%S"),
        "Temperature (°C)": st.session_state.temperature,
        "Humidity (%)": st.session_state.humidity,
        "Occupied": st.session_state.occupied,
        "ML prediction": ml_prediction,
        "Final recommendation": recommended_speed,
    })

if st.session_state.history:
    history_df = pd.DataFrame(st.session_state.history)

    chart = go.Figure()
    chart.add_trace(go.Scatter(
        x=list(range(1, len(history_df) + 1)),
        y=history_df["Temperature (°C)"],
        mode="lines+markers",
        name="Temperature (°C)",
        line=dict(color="#e9bd5a", width=3),
    ))
    chart.add_trace(go.Scatter(
        x=list(range(1, len(history_df) + 1)),
        y=history_df["Humidity (%)"],
        mode="lines+markers",
        name="Humidity (%)",
        line=dict(color="#73b7ee", width=3),
        yaxis="y2",
    ))
    chart.update_layout(
        height=340,
        xaxis_title="Recorded scenario",
        yaxis=dict(title="Temperature (°C)"),
        yaxis2=dict(title="Humidity (%)", overlaying="y", side="right"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="#dce5f5",
        legend=dict(orientation="h", y=1.12),
    )
    st.plotly_chart(chart, use_container_width=True)
    st.dataframe(history_df, use_container_width=True, hide_index=True)

    csv = history_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download session history (CSV)",
        data=csv,
        file_name="airmind_session_history.csv",
        mime="text/csv",
    )
else:
    st.info("No scenarios recorded yet. Click 'Record current scenario' to begin.")

# =========================================================
# FOOTER
# =========================================================
st.divider()
st.markdown("""
<div style="text-align:center; padding:12px">
    <div class="eyebrow">AIRMIND AI · ATOMQUEST 2026</div>
    <div class="small">
        Software prototype · Simulated inputs · No physical fan control enabled
    </div>
</div>
""", unsafe_allow_html=True)
