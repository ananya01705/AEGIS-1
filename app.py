""""
==================================================================================
 AEGIS-1 :: AUTONOMOUS SPACE DEBRIS INTERCEPTOR
 Code + AI Hybrid Architecture — Google AI Hackathon Prototype
==================================================================================
"""

import os
import time
import math
import random
from dataclasses import dataclass, field
from typing import List, Optional

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ----------------------------------------------------------------------------------
# Modern google-genai SDK 
# ----------------------------------------------------------------------------------
try:
    from google import genai
    from google.genai import types as genai_types
    GENAI_SDK_AVAILABLE = True
except ImportError:
    GENAI_SDK_AVAILABLE = False

# ==================================================================================
# PAGE CONFIG + THEME INITIALIZATION
# ==================================================================================
st.set_page_config(
    page_title="AEGIS-1 | Autonomous Space Debris Interceptor",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- THEME CONTROLLER PROFILE SELECTOR (Cleaned down to exactly 3 distinct options) ---
st.sidebar.markdown("### 🎛️ HUD DISPLAY PROFILE")
display_profile = st.sidebar.selectbox(
    "Ambient Environment Tuning",
    options=[
        "Cinematic Dark (Dim Room)", 
        "Matrix Cyberpunk",
        "Full Bright Display"
    ],
    index=0
)

# Define color schemes with eye-friendly container adaptations
if display_profile == "Full Bright Display":
    THEME = {
        "panel_bg": "#E2E8F0",      
        "plot_bg": "#F8FAFC",       # Warm/soft off-white container background instead of pure white flare
        "text_color": "#0F172A",    
        "grid_color": "#CBD5E1",    
        "threat_color": "#DC2626",  
        "secure_color": "#16A34A",  
        "banner_border": "#94A3B8"  
    }
elif display_profile == "Matrix Cyberpunk":
    THEME = {
        "panel_bg": "#0B0F19",      
        "plot_bg": "#0B1528",       # Softer translucent dark container layer to blend better with background
        "text_color": "#10B981",    
        "grid_color": "#064E3B",    
        "threat_color": "#F43F5E",  
        "secure_color": "#10B981",  
        "banner_border": "#059669"
    }
else:  # Default: Cinematic Dark (Dim Room)
    THEME = {
        "panel_bg": "#1E1B4B",      
        "plot_bg": "#13113C",       # Softened background container to match the dark canvas tone smoothly
        "text_color": "#E2E8F0",    
        "grid_color": "#334155",    
        "threat_color": "#FB7185",  
        "secure_color": "#34D399",  
        "banner_border": "#475569"
    }

# --- PRE-CALCULATE BACKGROUND STYLE BASED ON PROFILE ---
if display_profile == "Full Bright Display":
    app_background_style = THEME['panel_bg']
    sidebar_background_style = THEME['panel_bg']
else:
    app_background_style = "radial-gradient(ellipse at top left, #0a0e1a 0%, #05070d 55%, #000000 100%)"
    sidebar_background_style = "linear-gradient(180deg, #060a14 0%, #02040a 100%)"

CUSTOM_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Share+Tech+Mono&display=swap');

/* Global resets */
html, body, [class*="css"], .stMarkdown div p {{
    font-family: 'Share Tech Mono', monospace;
    color: {THEME['text_color']} !important;
}}

/* Entire Main Application Canvas */
.stApp, [data-testid="stAppViewContainer"] {{
    background: {app_background_style} !important;
    color: {THEME['text_color']} !important;
    transition: background 0.3s ease, color 0.3s ease;
}}

/* Sidebar Background */
section[data-testid="stSidebar"] {{
    background: {sidebar_background_style} !important;
    border-right: 1px solid {THEME['banner_border']}40 !important;
}}

/* Sidebar specific controls text */
section[data-testid="stSidebar"] h1, 
section[data-testid="stSidebar"] h2, 
section[data-testid="stSidebar"] h3, 
section[data-testid="stSidebar"] label {{
    color: {THEME['text_color']} !important;
}}

/* Title Headers */
h1, h2, h3 {{
    font-family: 'Orbitron', sans-serif !important;
    letter-spacing: 1px;
    color: {THEME['text_color']} !important;
}}

/* Adaptive App Header Title */
.aegis-title {{
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    font-size: 2.6rem;
    background: linear-gradient(90deg, {THEME['text_color']}, {THEME['secure_color']}, {THEME['text_color']});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}}

.aegis-subtitle {{
    color: {THEME['text_color']}AA;
    font-family: 'Share Tech Mono', monospace;
    letter-spacing: 3px;
    font-size: 0.95rem;
    margin-top: -8px;
}}

/* Adaptive Metrics Cards & Panels - Tuned down harsh contrast levels for the eyes */
.status-card, .mission-panel {{
    background-color: {THEME['plot_bg']} !important; 
    border: 1px solid {THEME['banner_border']}80 !important;
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 12px;
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.15) !important;
}}

.status-label {{
    font-size: 0.72rem;
    color: {THEME['text_color']}88;
    letter-spacing: 2px;
    text-transform: uppercase;
}}

.status-value {{
    font-family: 'Orbitron', sans-serif;
    font-size: 1.15rem;
    font-weight: 700;
    color: {THEME['text_color']} !important;
}}

/* Status Alerts mapped to exact theme colors */
.status-green {{ color: {THEME['secure_color']} !important; }}
.status-cyan  {{ color: {THEME['text_color']} !important; }}
.status-amber {{ color: {THEME['threat_color']}B3 !important; }}
.status-red   {{ color: {THEME['threat_color']} !important; }}

.threat-badge {{
    display: inline-block;
    font-family: 'Orbitron', sans-serif;
    font-weight: 900;
    padding: 6px 18px;
    border-radius: 6px;
    letter-spacing: 2px;
    font-size: 0.95rem;
    background: {THEME['threat_color']}20;
    color: {THEME['threat_color']} !important;
    border: 1px solid {THEME['threat_color']};
}}

.divider-glow {{
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, {THEME['banner_border']}80, transparent);
    margin: 18px 0;
}}

/* System Log Monitor box */
.mono-log {{
    font-family: 'Share Tech Mono', monospace;
    background: {THEME['panel_bg']};
    border: 1px solid {THEME['banner_border']}40;
    border-radius: 8px;
    padding: 16px;
    color: {THEME['secure_color']};
    white-space: pre-wrap;
    font-size: 0.88rem;
    line-height: 1.55;
}}

/* Progress bars map to structural statuses */
.timeline-fail {{
    background: {THEME['threat_color']};
    height: 26px;
    border-radius: 4px;
}}
.timeline-success {{
    background: {THEME['secure_color']};
    height: 26px;
    border-radius: 4px;
}}

/* Unified Call to Action Button */
.stButton>button {{
    font-family: 'Orbitron', sans-serif;
    font-weight: 700;
    letter-spacing: 1.5px;
    background: {THEME['secure_color']} !important;
    color: {THEME['panel_bg']} !important;
    border: none;
    border-radius: 8px;
    padding: 14px 10px;
    transition: all 0.2s ease-in-out;
}}
.stButton>button:hover {{
    opacity: 0.9;
    transform: translateY(-1px);
}}

/* Styled Animation Pulse Components */
.pulse-loader-text {{
    color: {THEME['secure_color']};
    font-weight: bold;
    animation: blinker 1.5s linear infinite;
}}
@keyframes blinker {{
    50% {{ opacity: 0.3; }}
}}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==============================================================================
# 🛰️ AEGIS-1 MISSION CONTROL INITIALIZATION & SECURITY CORE
# ==============================================================================
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets.get("GEMINI_API_KEY")
    except Exception:
        api_key = None

if "api_key" not in st.session_state and api_key:
    st.session_state["api_key"] = api_key

if "api_key" not in st.session_state:
    st.sidebar.markdown("### 🛰️ SYSTEM INITIALIZATION")
    st.sidebar.error("⚠️ CRITICAL: SYSTEM DEACTIVATED")
    st.sidebar.info(
        "**AI AUTHORIZATION REQUIRED**\n\n"
        "Please provide a Gemini Master Access Key to initialize the autonomous mission core."
    )
    
    user_key = st.sidebar.text_input("ENTER MASTER API KEY:", type="password")
    
    if st.sidebar.button("🤖 ACTIVATE ONBOARD CORE"):
        if user_key:
            st.session_state["api_key"] = user_key
            st.rerun()
        else:
            st.sidebar.warning("Authorization key cannot be empty.")
    if st.sidebar.button("🔄 RESET MASTER KEY"):
        st.session_state.clear()
        st.rerun()       
    st.title("AEGIS-1")
    st.subheader("Autonomous Space Mission Preservation & Threat Management System")
    st.warning("🔒 Onboard systems are currently locked. Please authenticate using the initialization terminal in the sidebar.")
    st.stop()
    

st.sidebar.markdown("### 🛰️ SYSTEM INITIALIZATION")
st.sidebar.success("🟢 GEMINI MASTER AGENT: ONLINE")
st.sidebar.markdown("""
**MISSION AI:** ACTIVE  
**ROUTING:** DETERMINISTIC PIPELINES  
**SECURITY STATUS:** ENCRYPTED
""")

FINAL_API_KEY = st.session_state["api_key"]

# ==================================================================================
# SCENARIO DEFINITIONS
# ==================================================================================
SCENARIOS = {
    "Low Risk Path": {
        "description": "A tracked debris fragment passes at a wide safety margin. Routine monitoring posture.",
        "debris_count": 1,
        "closing_velocity_kms": 1.9,
        "base_probability": 0.015,
        "time_to_impact_s": 42.0,
        "miss_distance_km": 4.8,
        "severity": 1,
    },
    "High Risk Conjunction": {
        "description": "A conjunction event with elevated collision probability. Debris trajectory intersects the station's orbital corridor.",
        "debris_count": 1,
        "closing_velocity_kms": 6.1,
        "base_probability": 0.18,
        "time_to_impact_s": 22.0,
        "miss_distance_km": 0.9,
        "severity": 2,
    },
    "Emergency Collision": {
        "description": "Imminent high-velocity impact trajectory. Single fragment on direct intercept course with the platform.",
        "debris_count": 1,
        "closing_velocity_kms": 11.3,
        "base_probability": 0.61,
        "time_to_impact_s": 11.0,
        "miss_distance_km": 0.12,
        "severity": 3,
    },
    "Kessler Syndrome Cascade (Multiple Debris)": {
        "description": "Cascading fragmentation event. Multiple hostile debris vectors converging simultaneously — worst-case scenario.",
        "debris_count": 7,
        "closing_velocity_kms": 9.7,
        "base_probability": 0.83,
        "time_to_impact_s": 8.5,
        "miss_distance_km": 0.05,
        "severity": 4,
    },
}

SEVERITY_LABELS = {
    1: ("NOMINAL", "status-green"),
    2: ("ELEVATED", "status-amber"),
    3: ("CRITICAL", "status-red"),
    4: ("SEVERE — CASCADE", "status-red"),
}


# ==================================================================================
# DETERMINISTIC PHYSICS ENGINE — 25 TRAJECTORY PLANNER
# ==================================================================================
@dataclass
class Trajectory:
    id: int
    burn_angle_deg: float
    altitude_delta_km: float
    plane_shift_deg: float
    fuel_cost_kg: float
    safety_margin_km: float
    delta_v_ms: float
    time_to_execute_s: float
    score: float = 0.0

@dataclass
class FutureThreatAnalysis:
    secondary_conjunctions: int
    orbital_stability_status: str  
    future_collision_prob: float
    mission_survivability_pct: float
    recommendation: str


def _seeded_rng(scenario_name: str):
    seed = abs(hash(scenario_name)) % (2**32 - 1)
    return np.random.default_rng(seed + int(time.time() * 1000) % 997)


def generate_25_trajectories(scenario_name: str) -> List[Trajectory]:
    scenario = SCENARIOS[scenario_name]
    rng = _seeded_rng(scenario_name)

    severity = scenario["severity"]
    trajectories: List[Trajectory] = []

    angles = np.linspace(-180, 180, 25) + rng.normal(0, 4, 25)
    for i in range(25):
        burn_angle = float(((angles[i] + 180) % 360) - 180)

        altitude_delta = float(rng.uniform(0.5, 12.0) * (1 + severity * 0.15))
        plane_shift = float(rng.uniform(-3.5, 3.5))

        delta_v = float(
            abs(burn_angle) * 0.014
            + altitude_delta * 0.22
            + abs(plane_shift) * 0.35
            + rng.uniform(0.05, 0.4)
        )

        isp_effective = 310.0
        g0 = 9.81
        dry_mass_kg = 420.0
        fuel_cost = float(dry_mass_kg * (1 - math.exp(-delta_v / (isp_effective * g0 / 1000))) )
        fuel_cost = max(0.05, fuel_cost)

        safety_margin = float(
            max(0.05, (altitude_delta * 0.35 + abs(burn_angle) * 0.01)
                * (1.0 + rng.uniform(-0.1, 0.25)))
        )

        exec_time = float(0.3 + delta_v * 0.05 + rng.uniform(0, 0.15))

        traj = Trajectory(
            id=i + 1,
            burn_angle_deg=round(burn_angle, 2),
            altitude_delta_km=round(altitude_delta, 3),
            plane_shift_deg=round(plane_shift, 3),
            fuel_cost_kg=round(fuel_cost, 3),
            safety_margin_km=round(safety_margin, 3),
            delta_v_ms=round(delta_v * 1000, 1),
            time_to_execute_s=round(exec_time, 2),
        )
        trajectories.append(traj)

    margins = np.array([t.safety_margin_km for t in trajectories])
    fuels = np.array([t.fuel_cost_kg for t in trajectories])
    times = np.array([t.time_to_execute_s for t in trajectories])

    def normalize(arr):
        rng_span = arr.max() - arr.min()
        return (arr - arr.min()) / rng_span if rng_span > 1e-9 else np.zeros_like(arr)

    norm_margin = normalize(margins)
    norm_fuel = 1 - normalize(fuels)
    norm_time = 1 - normalize(times)

    weights = (0.55, 0.30, 0.15)
    scores = weights[0] * norm_margin + weights[1] * norm_fuel + weights[2] * norm_time

    for t, s in zip(trajectories, scores):
        t.score = round(float(s) * 100, 2)

    trajectories.sort(key=lambda t: t.score, reverse=True)
    return trajectories

def compute_future_threat_matrix(scenario_name: str, chosen_traj: Optional[Trajectory], total_debris: int) -> FutureThreatAnalysis:
    if not chosen_traj:
        return FutureThreatAnalysis(0, "NOMINAL", 0.0, 100.0, "System standing by.")
        
    hazard_factor = (total_debris * 0.02) + (abs(chosen_traj.plane_shift_deg) * 0.05)
    
    if total_debris > 15:
        secondary_events = random.choice([1, 2, 3])
        stability = "LOW"
        future_prob = round(min(45.0, hazard_factor * 100), 1)
        survivability = round(100.0 - future_prob - (chosen_traj.fuel_cost_kg * 0.5), 1)
        rec = "Execute secondary phase tracking. Prepare alternative delta-v burn arrays for next orbital pass."
    elif total_debris > 5:
        secondary_events = random.choice([0, 1])
        stability = "MODERATE"
        future_prob = round(min(15.0, hazard_factor * 50), 1)
        survivability = round(100.0 - future_prob, 1)
        rec = "Maintain elevated telemetry awareness. Re-scan corridor at T+180 seconds."
    else:
        secondary_events = 0
        stability = "HIGH"
        future_prob = round(max(0.5, hazard_factor * 10), 1)
        survivability = round(100.0 - future_prob, 1)
        rec = "Maintain autonomous monitoring protocols for the next orbital cycle."

    return FutureThreatAnalysis(
        secondary_conjunctions=secondary_events,
        orbital_stability_status=stability,
        future_collision_prob=future_prob,
        mission_survivability_pct=survivability,
        recommendation=rec
    )


def get_top_3(trajectories: List[Trajectory]) -> List[Trajectory]:
    return trajectories[:3]

def evaluate_emergency_protocol(scenario_name: str, scenario: dict, debris_count: int) -> dict:
    time_to_impact = scenario.get("time_to_impact_s", 30.0)
    prob = scenario.get("base_probability", 0.0)
    miss_dist = scenario.get("miss_distance_km", 5.0)
    
    if scenario.get("severity") == 4 or time_to_impact <= 10.0 or debris_count >= 25:
        level = "AUTONOMOUS LOCKDOWN"
        css_class = "status-red"
        desc = "CRITICAL ALERT: Communication latency exceeds intercept window. Human confirmation disabled."
        auth = "FULL ENCRYPTED AUTONOMOUS MANEUVER CAPABILITY ENGAGED"
    elif time_to_impact <= 15.0 or prob > 0.5:
        level = "CRITICAL THREAT"
        css_class = "status-red"
        desc = "IMMINENT CONJUNCTION: Time vector requires automatic reaction grid configurations."
        auth = "AUTONOMOUS ENGINE ALLOCATION GRANTED"
    elif miss_dist < 1.5 or prob > 0.15:
        level = "HIGH RISK"
        css_class = "status-amber"
        desc = "ELEVATED CLOSE-APPROACH: Pre-calculating safety windows."
        auth = "AUTOMATED INTRUSION POSTURE STAGED"
    elif miss_dist <= 4.0:
        level = "CAUTION MONITORING"
        css_class = "status-cyan"
        desc = "ROUTINE INTERSECTION: Object path within wide buffer radar rings."
        auth = "MANUAL OVERRIDE AVAILABLE"
    else:
        level = "NOMINAL OPERATIONAL PROFILE"
        css_class = "status-green"
        desc = "CLEAR CORRIDOR: System maintaining monitoring cycle."
        auth = "STABLE BEACON ACTIVE"
        
    return {
        "level": level,
        "class": css_class,
        "description": desc,
        "authorization": auth
    }

def compute_subsystem_resource_grid(scenario_name: str, chosen_traj: Optional[Trajectory]) -> dict:
    base_power = 94.2
    base_thrust = 12.0
    
    if not chosen_traj:
        return {"power": base_power, "thrust": 0.0, "comms": "STABLE", "status": "NOMINAL"}
        
    power_drain = (chosen_traj.delta_v_ms * 0.015) + (chosen_traj.fuel_cost_kg * 0.4)
    thrust_load = (chosen_traj.delta_v_ms / chosen_traj.time_to_execute_s) * 0.08
    
    final_power = round(max(45.0, base_power - power_drain), 1)
    final_thrust = round(min(100.0, base_thrust + thrust_load), 1)
    
    comms_status = "DEGRADED (HIGH VIBRATION)" if final_thrust > 65.0 else "STABLE LINK"
    grid_status = "CRITICAL LOAD" if final_power < 60.0 else "NOMINAL OPERATIONAL PROFILE"
    
    return {
        "power": final_power,
        "thrust": final_thrust,
        "comms": comms_status,
        "status": grid_status
    }

def compute_component_health_lifecycle(scenario_name: str, total_debris: int) -> dict:
    structure_wear = min(35.0, (total_debris * 0.95))
    avionics_thermal = min(40.0, (total_debris * 1.2))
    
    structural_integrity = round(100.0 - structure_wear, 1)
    avionics_health = round(100.0 - avionics_thermal, 1)
    optics_health = round(max(50.0, 100.0 - (total_debris * 1.4)), 1)
    
    overall_health = round((structural_integrity * 0.4) + (avionics_health * 0.4) + (optics_health * 0.2), 1)
    
    return {
        "structure": structural_integrity,
        "avionics": avionics_health,
        "optics": optics_health,
        "overall": overall_health
    }

# ==================================================================================
# LATENCY COMPARISON ENGINE
# ==================================================================================
def compute_latency_story(scenario_name: str):
    scenario = SCENARIOS[scenario_name]
    input_window = scenario["time_to_impact_s"]

    ground_station_seconds = {
        "Signal Uplink Delay": 3.2,
        "Ground Crew Analysis": 6.5,
        "Command Authorization": 2.9,
        "Signal Downlink + Actuation": 1.8,
    }
    ground_total = round(sum(ground_station_seconds.values()), 1)

    aegis_seconds = {
        "Onboard Detection": 0.4,
        "25-Trajectory Physics Computation": 0.5,
        "Gemini Decision Layer": 0.5,
        "Thruster Actuation": 0.2,
    }
    aegis_total = round(sum(aegis_seconds.values()), 1)

    return {
        "impact_window": input_window,
        "ground_breakdown": ground_station_seconds,
        "ground_total": ground_total,
        "ground_outcome": "MISSION FAILURE" if ground_total > input_window else "MISSION SUCCESS",
        "aegis_breakdown": aegis_seconds,
        "aegis_total": aegis_total,
        "aegis_outcome": "MISSION SUCCESS" if aegis_total < input_window else "MISSION FAILURE",
    }


def render_latency_widget(latency: dict):
    st.markdown("### ⏱️ Decision Latency: Human-in-the-Loop vs. Aegis-1 Autonomy")
    st.caption(
        f"Impact window for this scenario: **{latency['impact_window']}s**. "
        "Every second of communication delay is a second closer to catastrophic failure."
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🛰️ ➜ 🌍 Ground Station Route (Human-in-the-Loop)**")
        for label, dur in latency["ground_breakdown"].items():
            pct = min(100, (dur / latency["ground_total"]) * 100)
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;font-size:0.82rem;color:#ff9a9a;'> "
                f"<span>{label}</span><span>{dur:.1f}s</span></div>"
                f"<div class='timeline-fail' style='width:{pct}%;margin-bottom:8px;'></div>",
                unsafe_allow_html=True,
            )
        outcome_color = "#ff5c5c" if latency["ground_outcome"] == "MISSION FAILURE" else "#4dffb0"
        st.markdown(
            f"<div class='status-card'>"
            f"<span class='status-label'>Total Response Time</span><br>"
            f"<span class='status-value' style='color:{outcome_color}'>{latency['ground_total']}s "
            f"— IMPACT AT {latency['impact_window']}s ➜ <b>{latency['ground_outcome']}</b></span></div>",
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown("**🤖 Aegis-1 Autonomous Route (Onboard AI)**")
        for label, dur in latency["aegis_breakdown"].items():
            pct = min(100, (dur / latency["aegis_total"]) * 100)
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;font-size:0.82rem;color:#9affc9;'> "
                f"<span>{label}</span><span>{dur:.1f}s</span></div>"
                f"<div class='timeline-success' style='width:{pct}%;margin-bottom:8px;'></div>",
                unsafe_allow_html=True,
            )
        outcome_color = "#4dffb0" if latency["aegis_outcome"] == "MISSION SUCCESS" else "#ff5c5c"
        st.markdown(
            f"<div class='status-card'>"
            f"<span class='status-label'>Total Response Time</span><br>"
            f"<span class='status-value' style='color:{outcome_color}'>{latency['aegis_total']}s "
            f"— IMPACT AT {latency['impact_window']}s ➜ <b>{latency['aegis_outcome']}</b></span></div>",
            unsafe_allow_html=True,
        )


# ==================================================================================
# 3D ORBITAL CANVAS (PLOTLY) — ADDED DETAILS & ATMOSPHERE EFFECTS
# ==================================================================================
EARTH_RADIUS_KM = 6371.0
ORBIT_ALTITUDE_KM = 550.0


def build_sphere(radius, resolution=40):
    u = np.linspace(0, 2 * np.pi, resolution)
    v = np.linspace(0, np.pi, resolution)
    x = radius * np.outer(np.cos(u), np.sin(v))
    y = radius * np.outer(np.sin(u), np.sin(v))
    z = radius * np.outer(np.ones(np.size(u)), np.cos(v))
    return x, y, z


def build_orbit_ring(radius, inclination_deg=45, n=200):
    theta = np.linspace(0, 2 * np.pi, n)
    x = radius * np.cos(theta)
    y = radius * np.sin(theta)
    z = np.zeros(n)
    incl = math.radians(inclination_deg)
    y_rot = y * math.cos(incl) - z * math.sin(incl)
    z_rot = y * math.sin(incl) + z * math.cos(incl)
    return x, y_rot, z_rot 


def build_3d_orbital_canvas(scenario_name: str, chosen_traj: Optional[Trajectory], override_count: Optional[int] = None):
    scenario = SCENARIOS[scenario_name]
    orbit_radius = EARTH_RADIUS_KM + ORBIT_ALTITUDE_KM

    if override_count is None and "scan_results" in st.session_state and st.session_state.scan_results is not None:
        debris_count = st.session_state.scan_results.get("debris_display_count", scenario["debris_count"])
    else:
        debris_count = override_count if override_count is not None else scenario["debris_count"]

    fig = go.Figure()

    # Base Earth Map Layer
    ex, ey, ez = build_sphere(EARTH_RADIUS_KM, 45)
    fig.add_trace(go.Surface(
        x=ex, y=ey, z=ez,
        colorscale=[[0, "#031633"], [0.3, "#073366"], [0.7, "#0d55a1"], [1.0, "#1c82e6"]],
        showscale=False, opacity=0.95, name="Earth Core",
        lighting=dict(ambient=0.6, diffuse=0.55, specular=0.4, roughness=0.3),
        hoverinfo="skip",
    ))

    # Dynamic Atmospheric Visual Flare Layer
    ax, ay, az = build_sphere(EARTH_RADIUS_KM + 180.0, 30)
    fig.add_trace(go.Surface(
        x=ax, y=ay, z=az,
        colorscale=[[0, "#4fa8ff"], [1.0, "#00c8ff"]],
        showscale=False, opacity=0.12, name="Atmospheric Layer",
        lighting=dict(ambient=0.9, diffuse=0.1),
        hoverinfo="skip",
    ))

    ox, oy, oz = build_orbit_ring(orbit_radius, inclination_deg=45)
    fig.add_trace(go.Scatter3d(
        x=ox, y=oy, z=oz, mode="lines",
        line=dict(color="#3fd0ff", width=4),
        name="Baseline Orbit",
    ))

    sat_x, sat_y, sat_z = ox[0], oy[0], oz[0]
    fig.add_trace(go.Scatter3d(
        x=[sat_x], y=[sat_y], z=[sat_z], mode="markers",
        marker=dict(size=7, color="#00ffea", symbol="diamond", line=dict(color="#ffffff", width=1)),
        name="Aegis-1 Satellite",
    ))

    rng = _seeded_rng(scenario_name + "_debris")
    for d in range(debris_count):
        start_dist = orbit_radius * (1.6 + rng.uniform(0, 0.5))
        theta_off = rng.uniform(-0.6, 0.6)
        phi_off = rng.uniform(-0.4, 0.4)
        dx0 = start_dist * math.cos(theta_off)
        dy0 = start_dist * math.sin(theta_off)
        dz0 = start_dist * math.sin(phi_off) * 0.6

        steps = 40
        xs = np.linspace(dx0, sat_x, steps)
        ys = np.linspace(dy0, sat_y, steps)
        zs = np.linspace(dz0, sat_z, steps)

        fig.add_trace(go.Scatter3d(
            x=xs, y=ys, z=zs, mode="lines+markers",
            line=dict(color="#ff3b3b", width=4 if debris_count > 10 else 5, dash="dot"),
            marker=dict(size=1.5 if debris_count > 10 else 2, color="#ff3b3b"),
            name=f"Debris Vector {d+1}" if debris_count <= 4 else ("Debris Vector Cluster" if d == 0 else ""),
            showlegend=True if d == 0 or debris_count <= 4 else False
        ))
        fig.add_trace(go.Scatter3d(
            x=[dx0], y=[dy0], z=[dz0], mode="markers",
            marker=dict(size=4 if debris_count > 10 else 5, color="#ff8080", symbol="x"),
            showlegend=False,
        ))

    if chosen_traj is not None:
        new_radius = orbit_radius + chosen_traj.altitude_delta_km
        angle_rad = math.radians(chosen_traj.burn_angle_deg)

        bx, by, bz = build_orbit_ring(new_radius, inclination_deg=45 + chosen_traj.plane_shift_deg, n=200)

        maneuver_x = bx[:60] * math.cos(angle_rad * 0.05) 
        maneuver_y = by[:60]
        maneuver_z = bz[:60] + chosen_traj.altitude_delta_km * np.linspace(0, 1, 60) * 0.02

        fig.add_trace(go.Scatter3d(
            x=maneuver_x, y=maneuver_y, z=maneuver_z, mode="lines",
            line=dict(color="#39ff8f", width=6),
            name=f"Maneuver Path (Traj #{chosen_traj.id})",
        ))
        fig.add_trace(go.Scatter3d(
            x=[maneuver_x[-1]], y=[maneuver_y[-1]], z=[maneuver_z[-1]], mode="markers",
            marker=dict(size=7, color="#39ff8f", symbol="diamond", line=dict(color="#ffffff", width=1)),
            name="Post-Maneuver Position",
        ))


    # Calculate chosen ID string dynamically for the title text
    traj_id_str = f"#{chosen_traj.id}" if chosen_traj else "Pending"

    fig.update_layout(
        # Space Defense dark UI alignment
        paper_bgcolor='#0a0f1d',  
        plot_bgcolor='#0a0f1d',
        font=dict(family="Share Tech Mono, monospace", color="#ffffff"), # Matches your app fonts!
        
        title=dict(
            text=f"<b>Aegis-1: Orbital Debris Avoidance Maneuver</b><br><sup>Trajectory {traj_id_str} Successfully Evades Impending Vector Corridor</sup>",
            x=0.05,
            y=0.92,
            font=dict(size=18, color="#ffffff")
        ),
        
        # 3D Scene tuning with hidden tick clutter
        scene=dict(
            aspectmode="data", # Forces Earth to stay perfectly spherical
            xaxis=dict(
                showgrid=True,
                gridcolor="#1e293b",
                showticklabels=False, # Hides the messy overlapping numbers
                title=dict(text="X-Axis", font=dict(size=10, color="#64748b")),
                showbackground=False
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor="#1e293b",
                showticklabels=False,
                title=dict(text="Y-Axis", font=dict(size=10, color="#64748b")),
                showbackground=False
            ),
            zaxis=dict(
                showgrid=True,
                gridcolor="#1e293b",
                showticklabels=False,
                title=dict(text="Z-Axis", font=dict(size=10, color="#64748b")),
                showbackground=False
            ),
            camera=dict(
                eye=dict(x=1.6, y=1.6, z=0.9) # Slightly widened angle to fit the orbit perfectly
            )
        ),
        
        # Legend layout positioning safely out of the grid space
        legend=dict(
            orientation="h",       
            yanchor="top",
            y=-0.05, # Moves it safely below the 3D canvas box to prevent overlap
            xanchor="center",
            x=0.5,
            bgcolor="rgba(10, 15, 29, 0.85)", 
            bordercolor="#334155",
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(r=10, l=10, b=60, t=90) 
    )
    return fig


# ==================================================================================
# MOCK DISPLAY-ONLY SPACE WEATHER CORE Generator
# ==================================================================================
def get_space_weather_data(scenario_name: str):
    """Generates immersive space ambient parameters aligned with scenarios."""
    if "Kessler" in scenario_name or "Emergency" in scenario_name:
        return {
            "kp_index": "G3 [Strong Geomagnetic Storm]",
            "kp_color": "status-red",
            "solar_flare": "X1.4 Class (High Flux Flare)",
            "proton_flux": "1,420 pfu [Elevated Radiation Hazard]",
            "ionosphere": "Highly Unstable // Scintillation Risk High"
        }
    else:
        return {
            "kp_index": "G1 [Minor Ambient Activity]",
            "kp_color": "status-green",
            "solar_flare": "C2.1 Class (Background)",
            "proton_flux": "12.4 pfu [Nominal Solar Base]",
            "ionosphere": "Quiet // Operational Margin Nominal"
        }


# ==================================================================================
# GEMINI 3.5 FLASH MASTER AGENT LAYER
# ==================================================================================
def get_genai_client(api_key: str = None):
    if not GENAI_SDK_AVAILABLE:
        return None
        
    active_key = api_key or st.session_state.get("api_key")
    if not active_key:
        return None
        
    try:
        return genai.Client(api_key=active_key)
    except Exception:
        return None


def build_agent_prompt(scenario_name: str, scenario: dict, top3: List[Trajectory],
                       all_trajectories: List[Trajectory], latency: dict, future_analysis: FutureThreatAnalysis) -> str:
    top3_desc = "\n".join(
        f"  - Trajectory #{t.id}: burn_angle={t.burn_angle_deg}°, altitude_delta={t.altitude_delta_km}km, "
        f"plane_shift={t.plane_shift_deg}°, delta_v={t.delta_v_ms}m/s, fuel_cost={t.fuel_cost_kg}kg, "
        f"safety_margin={t.safety_margin_km}km, exec_time={t.time_to_execute_s}s, score={t.score}/100"
        for t in top3
    )

    prompt = f"""
You are AEGIS-1, the onboard autonomous Master Agent Layer for a spacecraft collision-avoidance system.
A deterministic Python physics engine has ALREADY computed 25 candidate avoidance trajectories and has
ALREADY ranked and filtered them down to the Top 3 candidates below. You are NOT computing orbital
mechanics yourself — you are performing autonomous reasoning, threat assessment, and final trajectory
selection justification, exactly as a military-grade mission computer would.

SCENARIO: {scenario_name}
SCENARIO BRIEFING: {scenario['description']}
DEBRIS COUNT (MODIFIED BY SIDEBAR SLIDER OVERRIDE): {scenario['debris_count']}
CLOSING VELOCITY: {scenario['closing_velocity_kms']} km/s
BASELINE COLLISION PROBABILITY (pre-maneuver): {scenario['base_probability'] * 100:.1f}%
TIME TO IMPACT: {scenario['time_to_impact_s']} seconds
PRE-MANEUVER MISS DISTANCE: {scenario['miss_distance_km']} km

DECISION LATENCY CONTEXT (already computed by the system):
  - Ground Station (human-in-the-loop) total response time: {latency['ground_total']}s -> {latency['ground_outcome']}
  - Aegis-1 Autonomous total response time: {latency['aegis_total']}s -> {latency['aegis_outcome']}
  - Impact window: {latency['impact_window']}s

TOTAL CANDIDATE TRAJECTORIES EVALUATED BY PHYSICS ENGINE: {len(all_trajectories)}
TOP 3 TRAJECTORIES SHORTLISTED BY THE PHYSICS ENGINE (highest-scoring, in order):
{top3_desc}
IMPACT WINDOW: {latency['impact_window']} seconds
    
    FUTURE ORBIT PROJECTION ANALYSIS (T+1 Orbital Cycle):
      - Secondary Conjunction Events Detected: {future_analysis.secondary_conjunctions}
      - Post-Burn Orbital Stability Status: {future_analysis.orbital_stability_status}
      - Projected Future Collision Probability: {future_analysis.future_collision_prob}%
      - Calculated Long-Term Mission Survivability Yield: {future_analysis.mission_survivability_pct}%
      - Core System Future Recommendation Directive: {future_analysis.recommendation}
TASK:
Produce a structured, military-grade MISSION REPORT. Output MUST use exactly this section structure,
with clear ALL-CAPS section headers, no markdown code fences, concise but authoritative language:

THREAT LEVEL: <one of NOMINAL / ELEVATED / CRITICAL / SEVERE, plus a one-line justification>

COLLISION PROBABILITY: <your assessed probability post-analysis, with brief rationale referencing the
scenario's baseline probability and debris kinematics>

CRITICAL REASONING: <explain, in 3-5 sentences, why autonomous onboard decision-making was required for
this scenario, explicitly referencing the {latency['ground_total']}s ground-station latency vs the
{latency['aegis_total']}s Aegis-1 latency against the {latency['impact_window']}s impact window>

FUEL OPTIMIZATION: <state which single trajectory ID (from the Top 3 above) you are selecting as FINAL,
and justify the choice by explicitly comparing its fuel cost, safety margin, and execution time against
the other two shortlisted trajectories>

FINAL DECISION: AUTONOMOUS MANEUVER AUTHORIZED — TRAJECTORY #<id> — <one-line execution summary>

Be precise, decisive, and avoid hedging language. This is a real-time autonomous safety system.
"""
    return prompt.strip()


def call_gemini_master_agent(api_key: str, prompt: str) -> Optional[str]:
    def generate_local_fallback_report():
        if "Kessler Syndrome" in prompt or "COUNT" in prompt:
            threat = "SEVERE — CASCADING FRAGMENTATION HAZARD"
            prob = "89.4%"
            reasoning = "Simultaneous converging multi-vector debris clusters detected via sidebar override scaling. Human-in-the-loop latency (14.4s) dramatically gridlocks the critical impact window, making immediate autonomous intervention mandatory."
        elif "Emergency Collision" in prompt:
            threat = "CRITICAL — DIRECT INTERCEPT COURSE"
            prob = "61.0%"
            reasoning = "High-velocity fragment tracking directly to platform core. Onboard Aegis-1 routing resolved threat in under 2 seconds, preempting the impact corridor before ground crew communication could initiate."
        else:
            threat = "ELEVATED"
            prob = "18.0%"
            reasoning = "Debris trajectory intersects station secondary buffer corridor. Autonomous management authorized to maximize safety threshold margins."

        return f"""### SYSTEM LOG: LOCAL EXPERT BACKUP ENGAGED

**THREAT LEVEL:** {threat}

**COLLISION PROBABILITY:** Assessed at extreme risk boundary ({prob}) due to active closing trajectory vectors.

**CRITICAL REASONING:** {reasoning}

**FUEL OPTIMIZATION:** Finalizing selection of Trajectory #1. Cross-comparison metrics reveal it holds the highest safety-margin distribution while safely remaining inside nominal fuel-burn allocations.

**FINAL DECISION:** AUTONOMOUS MANEUVER AUTHORIZED — TRAJECTORY #1 — Vector adjustment successfully initiated on local backup engine."""

    client = get_genai_client(api_key)
    if client is None:
        return generate_local_fallback_report()
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2000,
                system_instruction=(
                    "You are AEGIS-1, a military-grade autonomous spacecraft mission computer. "
                    "You write terse, authoritative, structured mission reports. You must finish "
                    "every sentence completely. Never leave a section uncompleted or cut off."
                ),
            ),
        )
        return response.text
    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            st.toast("⚠️ Gemini API experiencing high demand. Seamlessly routing to onboard fallback processor!", icon="🤖")
            return generate_local_fallback_report()
        return f"__ERROR__::{error_msg}"


# ==================================================================================
# SIDEBAR — CONTROL PANEL
# ==================================================================================
with st.sidebar:
    st.markdown("<div class='aegis-title' style='font-size:1.6rem;'>🛰️ AEGIS-1</div>", unsafe_allow_html=True)
    st.markdown("<div class='aegis-subtitle'>MISSION CONTROL // ORBITAL DEFENSE</div>", unsafe_allow_html=True)
    st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)

    # Satellite Identity Integration
    st.markdown(
        f"<div class='status-card'><span class='status-label'>Designation</span><br>"
        f"<span class='status-value status-cyan'>AEG-7A</span></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='status-card'><span class='status-label'>Mission Class</span><br>"
        f"<span class='status-value status-cyan'>Orbital Defense System</span></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='status-card'><span class='status-label'>Time in Orbit</span><br>"
        f"<span class='status-value status-cyan'>487 Days</span></div>", unsafe_allow_html=True)
    
    st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)

    # Telemetry info continue 
    st.markdown(
        f"<div class='status-card'><span class='status-label'>Operational Status</span><br>"
        f"<span class='status-value status-green'>● ACTIVE</span></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='status-card'><span class='status-label'>Satellite Health</span><br>"
        f"<span class='status-value status-cyan'>NORMAL</span></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='status-card'><span class='status-label'>Fuel Remaining</span><br>"
        f"<span class='status-value status-green'>87%</span></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='status-card'><span class='status-label'>Velocity</span><br>"
        f"<span class='status-value status-cyan'>7.4 km/s</span></div>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='status-card'><span class='status-label'>AI Status</span><br>"
        f"<span class='status-value status-green'>● ONLINE (Gemini 3.5 Flash)</span></div>", unsafe_allow_html=True)

    st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
    st.markdown("**🎯 Scenario Selection**")
    scenario_choice = st.selectbox(
        "Scenario", list(SCENARIOS.keys()), label_visibility="collapsed",
    )
    st.caption(SCENARIOS[scenario_choice]["description"])

    st.markdown("<br>**💥 Kessler Debris Density Override**", unsafe_allow_html=True)
    base_count = SCENARIOS[scenario_choice]["debris_count"]
    debris_density_input = st.slider(
        "Debris Field Trackers",
        min_value=1,
        max_value=30,
        value=int(base_count),
        step=1,
        help="Simulates a runaway Kessler Syndrome chain reaction cascade by scaling vector intersections."
    )

    st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
    scan_clicked = st.button("🚀 [ INITIALIZE ORBITAL SCAN ]", use_container_width=True)

    st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
    st.caption("Aegis-1 Prototype · Code + AI Hybrid Architecture")
    st.caption("Physics Engine: Deterministic Python · Reasoning Layer: Gemini 3.5 Flash")
    st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
    st.markdown("**🖥️ INTERFACE VIEW MODE**")
    view_mode = st.radio(
        "View Mode Selection",
        ["🎥 Space Defense / Judges Mode", "🔬 Full Technical / Engineer Mode"],
        label_visibility="collapsed"
    )
# ==================================================================================
# MAIN HEADER
# ==================================================================================
st.markdown("<div class='aegis-title'>AEGIS-1 // AUTONOMOUS SPACE DEBRIS INTERCEPTOR</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='aegis-subtitle'>REAL-TIME ORBITAL COLLISION AVOIDANCE · CODE + AI HYBRID ARCHITECTURE</div>",
    unsafe_allow_html=True,
)
st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True) 
st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)

if "scan_results" not in st.session_state:
    st.session_state.scan_results = None

if not GENAI_SDK_AVAILABLE:
    st.warning(
        "⚠️ The `google-genai` package is not installed in this environment. "
        "Run `pip install google-genai` to enable the Gemini 3.5 Flash Master Agent Layer."
    )

# ==================================================================================
# 3. THE "DISPLAY-ONLY" SPACE WEATHER INTEGRATION (Immersive HUD Elements)
# ==================================================================================
weather = get_space_weather_data(scenario_choice)
weather_col1, weather_col2, weather_col3, weather_col4 = st.columns(4)

with weather_col1:
    st.markdown(f"<div class='status-card'><span class='status-label'>🌌 Geomagnetic Profile</span><br>"
                f"<span class='status-value {weather['kp_color']}'>{weather['kp_index']}</span></div>", unsafe_allow_html=True)
with weather_col2:
    st.markdown(f"<div class='status-card'><span class='status-label'>☀️ Solar Flare Yield</span><br>"
                f"<span class='status-value status-cyan'>{weather['solar_flare']}</span></div>", unsafe_allow_html=True)
with weather_col3:
    st.markdown(f"<div class='status-card'><span class='status-label'>⚛️ Proton Flux Density</span><br>"
                f"<span class='status-value status-cyan'>{weather['proton_flux']}</span></div>", unsafe_allow_html=True)
with weather_col4:
    st.markdown(f"<div class='status-card'><span class='status-label'>🛰️ Ionospheric Attenuation</span><br>"
                f"<span class='status-value status-green'>{weather['ionosphere']}</span></div>", unsafe_allow_html=True)

st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)


# ==================================================================================
# RUN SCAN PIPELINE (With High-Impact, Low-Effort Loading Animations)
# ==================================================================================
if scan_clicked:
    scenario = SCENARIOS[scenario_choice]

# -------------------------------------------------------------
# 🔥 ADVISOR PROPOSED FEATURE: 1-CLICK MISSION REPLAY MODE
# -------------------------------------------------------------
# st.sidebar.markdown("---")
#st.sidebar.markdown("### 🎬 DEMO MODE CONTROL")
#mission_replay = st.sidebar.button("🚀 LAUNCH MISSION REPLAY MODE", type="primary")

#if mission_replay:
 #   # 1. Dynamically discover a safe, real scenario key from your config to completely prevent KeyErrors
  #  safe_scenario_key = "Kessler: Syndrome Cascade (Worst Case)"
   # if 'SCENARIOS' in locals() and SCENARIOS:
    #    if safe_scenario_key not in SCENARIOS:
     #       safe_scenario_key = list(SCENARIOS.keys())[0]
            
    # 2. Extract a valid severity key from your existing configurations
   # fallback_severity = "CRITICAL" 
    #if 'SCENARIOS' in locals() and safe_scenario_key in SCENARIOS:
    #    fallback_severity = SCENARIOS[safe_scenario_key].get("severity", fallback_severity)
    #elif 'SEVERITY_LABELS' in locals() and SEVERITY_LABELS:
     #   fallback_severity = list(SEVERITY_LABELS.keys())[0]

    # Force states into session safely using the validated key
    #st.session_state.scenario_type = safe_scenario_key
    #st.session_state.debris_density = 7.0  

    # 3. Build the dramatic step-by-step presentation timeline
    #with st.status("📡 INITIALIZING ORBITAL RADAR CONSOLE...", expanded=True) as status:
     #   st.write("🔴 **T+0.0s:** SPACE DEBRIS DETECTED (7.0 km/s closing velocity)")
      #  time.sleep(1.2)
        
       # st.write("⚠️ **T+1.5s:** CRITICAL IMPACT WINDOW calculated: **8.5 Seconds**")
        #time.sleep(1.2)
        
        #st.write("❌ **T+3.0s:** GROUND CONTROL LATENCY verified: **14.4 Seconds**")
        #st.error("🚨 HUMAN INTERVENTION WINDOW EXCEEDED = CERTAIN MISSION FAILURE")
        #time.sleep(1.5)
        
      #  st.write("🛡️ **T+4.5s:** AEGIS-1 AUTONOMOUS LAYER ENGAGED")
       # time.sleep(1.0)
        
        #st.write("💻 **T+5.5s:** Deterministic Physics Engine running... **25 Trajectories Evaluated.**")
       # time.sleep(1.2)
        
        # Helper class supporting both object.attribute and dict["key"] lookups
        #class DotDict(dict):
         #   def __getattr__(self, key):
          #      if key not in self:
           #         return 0.0
      #          return self[key]
       #     __setattr__ = dict.__setitem__
        #    __delattr__ = dict.__delitem__

        # 4. Comprehensive Mock Dataset to satisfy ALL UI metric keys, canvas layers, and template tags
        #results = {
         #   "scenario_choice": safe_scenario_key, 
          #  "scenario": {
           #     "name": safe_scenario_key,
            #    "severity": fallback_severity,
             #   "base_probability": 0.99,
              #  "collision_probability": 0.99,
               # "time_to_impact": 8.5,
                #"time_to_impact_s": 8.5,
      #          "latency": 14.4,
       #         "latency_s": 14.4
    #        },
     #       "chosen_traj": DotDict({
      #          "id": "4B",
       #         "name": "Delta-V Vector Optim 4B",
        #        "burn_duration": "2.4s",
         #       "delta_v": "42.5 m/s",
         #       "clearance": "412m",
          #      "score": 0.982,
           #     "altitude_delta_km": 12.5       
       #     }),
        #    "trajectories": [], 
         #   "latency": {
          #      "aegis_total": 0.045,         
           #     "ground_control": 14.4,       
            #    "ground_total": 14.4,         
             #   "total": 14.445,
              #  "aegis_total_s": 0.045,
               # "aegis_breakdown": {
        #            "25-Trajectory Physics Computation": 0.035,
         #           "Threat Matrix Verification": 0.010
          #      }
           # },                  
            #"collision_prob": 0.99,           
           # "collision_probability": 0.99,           
        #    "time_to_impact": 8.5,            
         #   "time_to_impact_s": 8.5,            
          #  "future_risk_yield": 9.8,
           # "debris_display_count": 242,      
            #"active_threats": 25,             
           # "mitigation_status": "SUCCESS",
            
            # ✅ FIX: Added the missing ai_report block expected by line 1428 to clear the final layout hurdle
            #"ai_report": (
             #   "### 🛰️ AEGIS-1 AUTONOMOUS INTERCEPT REPORT\n\n"
              #  "**CRITICAL THREAT ANALYSIS:** A hypervelocity debris cluster was identified with an expected "
               # "impact window of **8.5s**. Traditional ground communication link round-trip time (**14.4s**) "
       #         "precluded human-in-the-loop remediation.\n\n"
        #        "**MITIGATION STRATEGY:** Automated execution of path vector **#4B** initiated at T+4.5 seconds. "
         #       "A 2.4-second continuous thruster firing successfully modified orbital eccentricity, yielding an "
          #      "effective safe clearance radius of **412 meters** from the core tracking cloud.\n\n"
           #     "**STATUS:** Target baseline restored. All primary telemetry metrics operational."
            #),
            
     #       "resource_grid": {"power": 45.0, "thrust": 100.0, "comms": "DEGRADED (HIGH VIBRATION)", "status": "CRITICAL LOAD"},
      #      "component_health": {"structure": 93.3, "avionics": 91.6, "optics": 98.2, "overall": 92.0}
       # }
        #st.session_state.scan_results = results
        
     #   status.update(label="✅ AEGIS-1 AUTONOMOUS MITIGATION COMPLETE - SATELLITE SECURED!", state="complete", expanded=False)
      #  st.rerun()  ###

    # Immersive Loading Experience container using dynamic placeholders
    progress_msg = st.empty()
    progress_bar = st.progress(0.0)
    
    with st.spinner("⚡ Connecting Telemetry Arrays..."):
        progress_msg.markdown("<span class='pulse-loader-text'>📡 PHASE 1: ACQUIRING DEBRIS CORRIDOR VECTOR MATRIX...</span>", unsafe_allow_html=True)
        time.sleep(0.4)
        progress_bar.progress(0.15)
        
        progress_msg.markdown("<span class='pulse-loader-text'>🧮 PHASE 2: INITIALIZING DETERMINISTIC PYTHON MECHANICAL SIMULATOR...</span>", unsafe_allow_html=True)
        all_trajectories = generate_25_trajectories(scenario_choice)
        time.sleep(0.4)
        progress_bar.progress(0.35)
        
        progress_msg.markdown("<span class='pulse-loader-text'>⚖️ PHASE 3: COMPILING PHYSICS RANKINGS & TIME-LATENCY DISTRIBUTIONS...</span>", unsafe_allow_html=True)
        top3 = get_top_3(all_trajectories)
        latency = compute_latency_story(scenario_choice)
        time.sleep(0.3)
        progress_bar.progress(0.55)
        
        progress_msg.markdown("<span class='pulse-loader-text'>🔮 PHASE 4: ENGAGING FUTURE PASS ORBITAL CONJUNCTION PREDICTOR ENGINE...</span>", unsafe_allow_html=True)
        future_analysis = compute_future_threat_matrix(scenario_choice, top3[0] if top3 else None, debris_density_input)
        emergency_state = evaluate_emergency_protocol(scenario_choice, scenario, debris_density_input)
        time.sleep(0.3)
        progress_bar.progress(0.70)
        
        progress_msg.markdown("<span class='pulse-loader-text'>🔋 PHASE 5: QUANTIFYING SUBSYSTEM TRANSIENTS & STRUCTURAL INTEGRITY LOSS...</span>", unsafe_allow_html=True)
        resource_grid = compute_subsystem_resource_grid(scenario_choice, top3[0] if top3 else None)
        component_health = compute_component_health_lifecycle(scenario_choice, debris_density_input)
        time.sleep(0.3)
        progress_bar.progress(0.85)

        ai_report = None
        if FINAL_API_KEY:
            progress_msg.markdown("<span class='pulse-loader-text'>🤖 PHASE 6: PIPING SOLUTIONS PACKET TO GEMINI 3.5 FLASH REASONING OVERLORD...</span>", unsafe_allow_html=True)
            scenario_adjusted = scenario.copy()
            scenario_adjusted["debris_count"] = debris_density_input
            
            prompt = build_agent_prompt(scenario_choice, scenario_adjusted, top3, all_trajectories, latency, future_analysis)
            ai_report = call_gemini_master_agent(FINAL_API_KEY, prompt)
            time.sleep(0.2)
        
        progress_bar.progress(1.0)
        progress_msg.empty()
        progress_bar.empty()
        st.toast("🟢 AEGIS-1 Mission Telemetry Synced Successfully!", icon="🛰️")

    st.session_state.scan_results = {
        "scenario_choice": scenario_choice,
        "scenario": scenario,
        "debris_display_count": debris_density_input, 
        "all_trajectories": all_trajectories,
        "top3": top3,
        "latency": latency,
        "future_analysis": future_analysis, 
        "emergency_state": emergency_state, 
        "resource_grid": resource_grid,       
        "component_health": component_health, 
        "ai_report": ai_report,
        "chosen_traj": top3[0] if top3 else None,
    }

# ==================================================================================
# RENDER RESULTS
# ==================================================================================
results = st.session_state.scan_results

if results is None:
    st.info(
        "👈 Select a scenario in the Mission Control sidebar and click "
        "**[ INITIALIZE ORBITAL SCAN ]** to run the Aegis-1 avoidance pipeline."
    )
else:
    scenario = results["scenario"]
    severity_label, severity_class = SEVERITY_LABELS[scenario["severity"]]
    top_traj = results["chosen_traj"]
    latency = results["latency"]
    f_data = results.get("future_analysis", None)
    
    e_state = results.get("emergency_state", {
        "level": "NOMINAL", 
        "class": "status-green", 
        "description": "Stable Protocol Monitoring", 
        "authorization": "STABLE ACTIVE"
    })

    # ==========================================
    # 🎥 VIEW 1: SPACE DEFENSE / JUDGES MODE 
    # ==========================================
    if "Judges Mode" in view_mode:
        st.markdown(
            f"""
            <div style="background-color:{THEME['panel_bg']}; padding:20px; border-radius:10px; border-left: 8px solid {THEME['banner_border']}; margin-bottom: 25px;">
                <h1 style="color:{THEME['threat_color']}; margin:0; font-size:28px; letter-spacing:1px;">⚠️ ORBITAL THREAT ISOLATION TERMINAL</h1>
                <p style="color:{THEME['text_color']}; margin:5px 0 0 0; font-size:14px; font-family:monospace;">
                    SYSTEM STATUS: SECURE REGION INDEX // PROFILE: {display_profile.upper()} ACTIVE
                </p>
            </div>
            """, 
            unsafe_allow_html=True
        )

        col_problem, col_resolution = st.columns(2)
        with col_problem:
            st.markdown("### 🔴 CRITICAL THREAT METRICS")
            st.metric(label="COLLISION PROBABILITY", value=f"{scenario['base_probability']*100:.1f} %")
            st.metric(label="HUMAN INTERVENTION WINDOW", value=f"{scenario['time_to_impact_s']} SECONDS")
            st.error("🚨 EMERGENCY TRIGGER: HUMAN OPERATOR RESPONSIVENESS FAILS INDICES")

        with col_resolution:
            st.markdown("### 🟢 AEGIS-1 AUTONOMOUS INTERVENE")
            st.metric(label="ONBOARD CORE RESPONSIVENESS", value=f"{latency['aegis_total']} SECONDS")
            st.metric(label="KINEMATIC TRAJECTORIES GENERATED", value="25 RUNS")
            st.success("🔒 SYSTEM AUTONOMOUS ACTION COMPLETE: SATELLITE SECURED")

        st.markdown("---")
        
        st.markdown(f"""
        <div class='mission-panel' style='border: 1px solid rgba(255, 92, 92, 0.4); padding: 20px; border-radius: 8px;'>
            <h4 style='color: #ff5c5c; margin-top: 0;'>⚠️ TRADITIONAL ROUTE: HUMAN-IN-THE-LOOP INTERVENTION</h4>
            <ul style='line-height: 1.8; font-size: 1.05rem; color: #ff5c5c; margin-bottom: 0;'>
                <li>📡 <b>SATELLITE OPERATIONAL</b> // Maintaining normal orbital lane profile.</li>
                <li>💥 <b>SUDDEN THREAT DETECTED</b> // <b>{results['debris_display_count']} incoming debris objects</b> tracked on direct intercept vectors.</li>
                <li>📈 <b>COLLISION PROBABILITY:</b> <span style='font-weight:bold; font-size:1.15rem; color:#ff5c5c;'>{scenario['base_probability']*100:.1f}%</span></li>
                <li>⏳ <b>CRITICAL INTERCEPT WINDOW:</b> Threat impact calculated in exactly <span style='font-weight:bold;'>{scenario['time_to_impact_s']} seconds</span>.</li>
                <li>🌍 <b>HUMAN LATENCY BOUNDARY:</b> Ground station routing & approval chain requires <span style='font-weight:bold;'>{latency['ground_total']} seconds</span>.</li>
                <li>❌ <b>RESULT: CATASTROPHIC IMPACT AT T+{scenario['time_to_impact_s']}s ➜ MISSION FAILURE</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='text-align: center; font-size: 1.8rem; font-weight: bold; margin: 25px 0; color: #00ffa2; letter-spacing: 1px;'>⚡ ORBITAL AUTONOMY TAKEOVER ENGAGED ⚡</div>", unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class='mission-panel' style='border: 1px solid rgba(0, 255, 162, 0.4); padding: 20px; border-radius: 8px;'>
            <h4 style='color: #00ffa2; margin-top: 0;'>🛰️ AEGIS-1 ROUTE: AUTONOMOUS MISSION PRESERVATION ENGINE</h4>
            <ul style='line-height: 1.8; font-size: 1.05rem; color: {THEME["text_color"]}; margin-bottom: 0;'>
                <li>🤖 <b>AEGIS-1 ONBOARD ENGINE ACTIVE</b> // Running edge computation arrays.</li>
                <li>🧮 <b>DETECTION & RESOLUTION:</b> 25 trajectory safety simulations generated in <b>{latency['aegis_breakdown']['25-Trajectory Physics Computation']}s</b>.</li>
                <li>🛡️ <b>EMERGENCY POSTURE UPDATED:</b> System escalated to <span class='{e_state['class']}' style='font-weight:bold;'>{e_state['level']}</span>.</li>
                <li>🔑 <b>AUTHORIZATION STATE:</b> <span style='font-weight:bold;'>{e_state['authorization']}</span></li>
                <li>🚀 <b>OPTIMAL SOLUTION EXECUTED:</b> Selected <b>Trajectory #{top_traj.id if top_traj else '24'}</b> for dynamic engine burn.</li>
                <li>⏱️ <b>AEGIS-1 RESPONSE LATENCY:</b> Total execution completed in just <span style='font-weight:bold;'>{latency['aegis_total']} seconds</span> (Well before the {scenario['time_to_impact_s']}s impact wall).</li>
                <li>🎯 <b>RESULT: COLLISION AVOIDED SUCCESSFULLY ➜  MISSION SECURE</b></li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
        j1, j2, j3 = st.columns(3)
        with j1:
            st.metric(label="🎯 SELECTED TRAJECTORY VECTOR", value=f"PATH #{top_traj.id if top_traj else '24'}")
        with j2:
            st.metric(label="🏆 COMPOUND MISSION CONFIDENCE", value=f"{top_traj.score if top_traj else 98.2:.1f} %")
        with j3:
             if f_data:
                 future_risk = f"{f_data.future_collision_prob:.1f} %"
             else:
                 future_risk = "0.0 %"
                 st.metric(label="🔮 FUTURE ORBITAL RISK CYCLE", value=future_risk)

        # =========================================================
        # NEW INTEGRATION: TECHNICAL SUB-SYSTEMS TELEMETRY FOR JUDGES
        # =========================================================
        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
        st.markdown("### 🔬 EVALUATOR TELEMETRY: ONBOARD RISK & COMPONENT LIFECYCLE")
        
        tech_col1, tech_col2 = st.columns(2)
        
        with tech_col1:
            st.markdown("#### 📡 Forward-Propagation Threat Matrix")
            # Try to fetch future threat data from results or session state
            active_f_data = results.get("f_data") or st.session_state.get("f_data")
            
            if active_f_data:
                # Convert the FutureThreatAnalysis dataclass fields into a clean UI table
                threat_df = pd.DataFrame([{
                    "Metrics": "Secondary Conjunctions", "Value": f"{active_f_data.secondary_conjunctions} Events"
                }, {
                    "Metrics": "Orbital Stability Status", "Value": str(active_f_data.orbital_stability_status)
                }, {
                    "Metrics": "Future Collision Probability", "Value": f"{active_f_data.future_collision_prob} %"
                }, {
                    "Metrics": "Mission Survivability Yield", "Value": f"{active_f_data.mission_survivability_pct} %"
                }])
                st.dataframe(threat_df, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Complete a simulation run to view the forward threat vector array.")
                
        with tech_col2:
            st.markdown("#### ⚡ Subsystem Resource Grid & Lifecycle Health")
            # Pull resource/health grids from results or fallback to session state
            r_grid = results.get("resource_grid") or st.session_state.get("resource_grid")
            c_health = results.get("component_health") or st.session_state.get("component_health")
            
            if r_grid and c_health:
                # Merge dictionary data into the beautifully structured grid table
                health_df = pd.DataFrame([
                    {"Subsystem Metric": "Core Power Reserve", "Status/Yield": f"{r_grid.get('power', 0)}%"},
                    {"Subsystem Metric": "Active Thruster Load", "Status/Yield": f"{r_grid.get('thrust', 0)}%"},
                    {"Subsystem Metric": "Structural Shielding Integrity", "Status/Yield": f"{c_health.get('structure', 0)}%"},
                    {"Subsystem Metric": "Flight Avionics Core Health", "Status/Yield": f"{c_health.get('avionics', 0)}%"},
                    {"Subsystem Metric": "Composite Health Yield", "Status/Yield": f"{c_health.get('overall', 0)}%"},
                ])
                st.dataframe(health_df, use_container_width=True, hide_index=True)
            else:
                st.info("ℹ️ Complete a simulation run to view hardware lifecycle metrics.")
        # =========================================================

        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
        st.markdown("### 🌍 Real-Time Orbital Intercept Canvas")
        fig3d = build_3d_orbital_canvas(
            scenario_name=results["scenario_choice"], 
            chosen_traj=results["chosen_traj"],
            override_count=results.get("debris_display_count", None)
        )
        st.plotly_chart(fig3d, use_container_width=True)

        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
        st.markdown("### 🤖 Onboard Master Agent — Gemini 3.5 Flash MISSION REPORT")
        ai_report = results["ai_report"]
        if isinstance(ai_report, str) and ai_report.startswith("__ERROR__::"):
            st.error(f"❌ Onboard Core Error: {ai_report.replace('__ERROR__::', '')}")
            if st.button("🔄 Clear Invalid Key & Try Again", type="primary"):
                st.session_state.clear()
                st.rerun()
        elif ai_report:
            with st.container(border=True):
                st.markdown(ai_report)
                
    # ==========================================
    # 🔬 VIEW 2: FULL TECHNICAL / ENGINEER MODE
    # ==========================================
    else:
        st.markdown("### 🛰️ Orbital Traffic Flow & Cascade Proximity Tracking Matrix")

        st.markdown("<div class='mission-panel'>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<span class='status-label'>Scenario</span><br><span class='status-value status-cyan'>{results['scenario_choice']}</span>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<span class='status-label'>Threat Severity</span><br><span class='threat-badge {severity_class}'>{severity_label}</span>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<span class='status-label'>Baseline Collision Probability</span><br><span class='status-value status-amber'>{scenario['base_probability']*100:.1f}%</span>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<span class='status-label'>Time to Impact</span><br><span class='status-value status-red'>{scenario['time_to_impact_s']}s</span>", unsafe_allow_html=True)
        
        st.markdown(f"""
            <div style='margin-top: 14px; border-top: 1px solid rgba(0, 240, 255, 0.1); padding-top: 10px; background: rgba(5, 42, 82, 0.3); padding: 12px; border-radius: 6px;'>
                <span class='status-label'>📋 System Directive:</span> <span style='font-size:0.9rem; color:#e0f7ff;'>{e_state['description']}</span><br>
                <span class='status-label'>🔑 Authorization State:</span> <span class='{e_state['class']}' style='font-size:0.9rem; font-weight:bold;'>{e_state['authorization']}</span>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        render_latency_widget(results["latency"])
        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)

        st.markdown("### 📊 SYSTEM CONFIDENCE & SECURITY MATRIX")
        m1, m2, m3, m4 = st.columns(4)
        
        fuel_efficiency = 100.0 - (top_traj.fuel_cost_kg / 5.0) if top_traj else 96.4
        fuel_efficiency = max(72.0, min(99.9, fuel_efficiency))
        
        safety_yield = 95.0 + (min(top_traj.safety_margin_km, 500.0) / 100.0) if top_traj else 99.1
        safety_yield = min(99.9, safety_yield)
        
        stability_factor = 97.0 - abs(top_traj.plane_shift_deg * 2.5) if top_traj else 95.8
        stability_factor = max(88.0, min(99.5, stability_factor))
        
        compound_score = top_traj.score if top_traj else 97.2

        with m1:
            st.metric(label="⛽ Fuel Optimization", value=f"{fuel_efficiency:.1f} %")
        with m2:
            st.metric(label="🛡️ Collision Avoidance", value=f"{safety_yield:.1f} %")
        with m3:
            st.metric(label="🛰️ Orbital Stability", value=f"{stability_factor:.1f} %")
        with m4:
            st.metric(label="🏆 COMPOUND CONFIDENCE", value=f"{compound_score:.1f} %")

        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)
        st.markdown("### 🔮 Forward-Propagation Matrix: Future Threat & Orbit Analysis")
        
        if f_data:
            fx1, fx2, fx3, fx4 = st.columns(4)
            with fx1:
                st.markdown(f"<div class='status-card'><span class='status-label'>Secondary Conjunctions</span><br><span class='status-value status-amber'>{f_data.secondary_conjunctions} Events</span></div>", unsafe_allow_html=True)
            with fx2:
                st.markdown(f"<div class='status-card'><span class='status-label'>Orbital Stability</span><br><span class='status-value status-cyan'>{f_data.orbital_stability_status}</span></div>", unsafe_allow_html=True)
            with fx3:
                st.markdown(f"<div class='status-card'><span class='status-label'>Future Collision Risk</span><br><span class='status-value status-red'>{f_data.future_collision_prob} %</span></div>", unsafe_allow_html=True)
            with fx4:
                st.markdown(f"<div class='status-card'><span class='status-label'>Mission Survivability</span><br><span class='status-value status-green'>{f_data.mission_survivability_pct} %</span></div>", unsafe_allow_html=True)
                
            st.info(f"📋 **System Onboard Future Recommendation Directive:** {f_data.recommendation}")
            
        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)     

        st.markdown("### 🧮 25-Trajectory Physics Planner & Filter Matrix")
        df = pd.DataFrame([t.__dict__ for t in results["all_trajectories"]])
        df = df.rename(columns={
            "id": "Traj #", "burn_angle_deg": "Burn Angle (°)", "altitude_delta_km": "Alt Δ (km)",
            "plane_shift_deg": "Plane Shift (°)", "fuel_cost_kg": "Fuel (kg)",
            "safety_margin_km": "Safety Margin (km)", "delta_v_ms": "Δv (m/s)",
            "time_to_execute_s": "Exec Time (s)", "score": "Score",
        })
        df_sorted = df.sort_values("Score", ascending=False)

        if top_traj is not None:
            st.markdown(f"""
                <div class='status-card' style='border: 2px solid #00ffa2; background: linear-gradient(135deg, #051a10cc, #060e1acc);'>
                    <span class='status-label' style='color:#00ffa2;'>🤖 PRIMARY COMPUTE CRITERIA PATH SELECTED</span><br>
                    <span class='status-value status-green'>TRAJECTORY #{top_traj.id} DETECTED AS OPTIMAL</span>
                    <p style='font-size:0.85rem; margin-top:6px; color:#a2ffd2;'>
                        Engine Metrics: Safety Margin of <b>{top_traj.safety_margin_km} km</b> achieved with an optimized fuel burn allocation of <b>{top_traj.fuel_cost_kg} kg</b>. 
                        Execution initialization window calculated at <b>{top_traj.time_to_execute_s}s</b>.
                    </p>
                </div>
            """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["🏆 Top 3 Shortlisted Candidates", "📊 Full 25-Trajectory Telemetry Matrix"])
        with tab1:
            st.dataframe(
                df_sorted.head(3).style.background_gradient(subset=["Score"], cmap="Greens")
                                       .background_gradient(subset=["Safety Margin (km)"], cmap="Blues")
                                       .background_gradient(subset=["Fuel (kg)"], cmap="Reds_r"),
                use_container_width=True, 
                hide_index=True,
            )
        with tab2:
            st.dataframe(df_sorted, use_container_width=True, hide_index=True, height=300)

        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)

        st.markdown("### 🌍 3D Orbital Space Domain Awareness — Real-Time Cluster Tracking")
        fig3d = build_3d_orbital_canvas(
            scenario_name=results["scenario_choice"], 
            chosen_traj=results["chosen_traj"],
            override_count=results.get("debris_display_count", None)
        ) 
        
        fig3d.update_layout(
            template="plotly_dark" if display_profile != "Full Bright Display" else "plotly_white",
            paper_bgcolor=THEME["panel_bg"],
            plot_bgcolor=THEME["plot_bg"],
            font=dict(family="monospace", size=12, color=THEME["text_color"]),
            margin=dict(l=0, r=0, b=0, t=30),
        )
        st.plotly_chart(fig3d, use_container_width=True)

        st.markdown("<hr class='divider-glow'/>", unsafe_allow_html=True)

        st.markdown("### 🔬 Real-Time Spacecraft Subsystem Grid & Component Health Matrix")
        r_grid = results.get("resource_grid", {"power": 94.2, "thrust": 0.0, "comms": "STABLE", "status": "NOMINAL"})
        c_health = results.get("component_health", {"structure": 100.0, "avionics": 100.0, "optics": 100.0, "overall": 100.0})
        
        # Pull text color dynamically based on theme selection
        # (If your theme dict uses a different key name like 'primary_text', update this key)
        txt_color = THEME.get('text_color', '#FFFFFF') 
        
        h_col1, h_col2 = st.columns(2)
        with h_col1:
            col1_html = f"""
            <div class='mission-panel' style='height: 250px; margin: 0; padding: 15px; color: {txt_color}; font-family: sans-serif;'>
                <h4 style='margin-top:0; color: {txt_color};'>🔋 Onboard Subsystem Resource Grid</h4>
                <p style='color: {txt_color};'><b>Grid Load Posture:</b> <code style='color: {THEME['secure_color']};'>{r_grid['status']}</code></p>
                
                <div style='margin-bottom: 12px; color: {txt_color};'>
                    <div style='display:flex; justify-content:space-between; font-size:0.85rem;'>
                        <span>⚡ Core Power Reserve</span><span>{r_grid['power']}%</span>
                    </div>
                    <div style='background: {THEME['grid_color']}40; width:100%; height:8px; border-radius:4px;'>
                        <div style='background: {THEME['secure_color']}; width:{r_grid['power']}%; height:100%; border-radius:4px;'></div>
                    </div>
                </div>

                <div style='margin-bottom: 12px; color: {txt_color};'>
                    <div style='display:flex; justify-content:space-between; font-size:0.85rem;'>
                        <span>🚀 Active Thruster Load</span><span>{r_grid['thrust']}%</span>
                    </div>
                    <div style='background: {THEME['grid_color']}40; width:100%; height:8px; border-radius:4px;'>
                        <div style='background: {THEME['threat_color']}; width:{r_grid['thrust']}%; height:100%; border-radius:4px;'></div>
                    </div>
                </div>
                
                <p style='margin-top:18px; color: {txt_color};'>📡 Communications Transceiver Array: <b>{r_grid['comms']}</b></p>
            </div>
            """
            st.components.v1.html(col1_html, height=260, scrolling=False)
            
        with h_col2:
            col2_html = f"""
            <div class='mission-panel' style='height: 250px; margin: 0; padding: 15px; color: {txt_color}; font-family: sans-serif;'>
                <h4 style='margin-top:0; color: {txt_color};'>🛠️ Automated Component Lifecycle Monitor</h4>
                <p style='color: {txt_color};'><b>Composite Platform Health Yield:</b> <code>{c_health['overall']}%</code></p>
                
                <div style='margin-bottom: 10px; color: {txt_color};'>
                    <div style='display:flex; justify-content:space-between; font-size:0.85rem;'>
                        <span>🛡️ Structural Shielding Integrity</span><span>{c_health['structure']}%</span>
                    </div>
                    <div style='background: {THEME['grid_color']}40; width:100%; height:6px; border-radius:4px;'>
                        <div style='background: {THEME['secure_color']}; width:{c_health['structure']}%; height:100%; border-radius:4px;'></div>
                    </div>
                </div>

                <div style='margin-bottom: 10px; color: {txt_color};'>
                    <div style='display:flex; justify-content:space-between; font-size:0.85rem;'>
                        <span>🖥️ Flight Avionics Core Temperature Threshold</span><span>{c_health['avionics']}%</span>
                    </div>
                    <div style='background: {THEME['grid_color']}40; width:100%; height:6px; border-radius:4px;'>
                        <div style='background: {THEME['secure_color']}; width:{c_health['avionics']}%; height:100%; border-radius:4px;'></div>
                    </div>
                </div>

                <div style='margin-bottom: 10px; color: {txt_color};'>
                    <div style='display:flex; justify-content:space-between; font-size:0.85rem;'>
                        <span>🔭 Star Tracker Optoelectronic Sensitivities</span><span>{c_health['optics']}%</span>
                    </div>
                    <div style='background: {THEME['grid_color']}40; width:100%; height:6px; border-radius:4px;'>
                        <div style='background: {THEME['secure_color']}; width:{c_health['optics']}%; height:100%; border-radius:4px;'></div>
                    </div>
                </div>
            </div>
            """
            st.components.v1.html(col2_html, height=260, scrolling=False)
        st.markdown("### 🤖 Onboard Master Agent — Gemini 3.5 Flash MISSION REPORT")
        ai_report = results["ai_report"]
        if not FINAL_API_KEY:
            st.warning("⚠️ **No Gemini API key detected.** Enter key in sidebar.")
        elif ai_report is None:
            st.warning("⚠️ `google-genai` SDK unavailable.")
        elif isinstance(ai_report, str) and ai_report.startswith("__ERROR__::"):
            st.error(f"❌ Gemini API call failed: {ai_report.replace('__ERROR__::', '')}")
            if st.button("🔄 Clear Invalid Key (Tech Mode)", type="primary", key="tech_reset_btn"):
                 st.session_state.clear()
                 st.rerun()
        else:
            with st.container(border=True):
                st.markdown(ai_report)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(
                label="💾 Export Signed Mission Telemetry Log (.TXT)",
                data=str(ai_report),
                file_name=f"AEGIS1_MISSION_{results['scenario_choice'].replace(' ', '_').upper()}_LOG.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.markdown("<br>", unsafe_allow_html=True)