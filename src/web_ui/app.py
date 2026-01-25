# src/web_ui/app.py

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import json
import sys
import os
import random

# --- 1. CRITICAL PATH SETUP (Must be before 'from src...') ---
# This tells Python: "Look for modules in the ngsc_project folder"
current_dir = os.path.dirname(os.path.abspath(__file__)) # .../src/web_ui
project_root = os.path.abspath(os.path.join(current_dir, "../..")) # .../ngsc_project
if project_root not in sys.path:
    sys.path.append(project_root)

# --- 2. NOW we can import our modules ---
from src.orbit_engine import OrbitEngine
from src.radio_core import RadioCore
from src.decoder import TelemetryDecoder
from src.data_manager import DataManager  # <--- Add this

# --- Page Config ---
st.set_page_config(
    page_title="NGSC Mission Control",
    page_icon="🛰️",
    layout="wide"
)

# --- Header ---
st.title("🛰️ Nanosat Ground Station Controller")
st.markdown("Status: **ONLINE** | Location: **Ahmedabad**")

# --- Sidebar: Mission Configuration ---
st.sidebar.header("Mission Config")

try:
    with open(os.path.join(project_root, 'config/satellites.json'), 'r') as f:
        sat_data = json.load(f)
        sat_list = {s['name']: s for s in sat_data['satellites']}
except FileNotFoundError:
    st.error("Config file not found! Check your config/satellites.json path.")
    st.stop()

selected_sat_name = st.sidebar.selectbox("Select Target", list(sat_list.keys()))
current_sat = sat_list[selected_sat_name]

# --- Initialize Engines ---
@st.cache_resource
def get_engines():
    orbit = OrbitEngine()           # Navigator
    radio = RadioCore(mock_mode=True) # Driver
    decoder = TelemetryDecoder()    # Translator
    return orbit, radio, decoder

orbit_engine, radio_core, decoder = get_engines()

# --- Main Dashboard Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(f"Tracking: {selected_sat_name}")
    az_metric = st.metric("Azimuth (Compass)", "0.0°")
    el_metric = st.metric("Elevation (Tilt)", "0.0°")
    dist_metric = st.metric("Range (Distance)", "0 km")
    radar_chart = st.empty()

with col2:
    st.subheader("Radio & Data")
    freq_metric = st.metric("Frequency", f"{current_sat['frequency']/1e6} MHz")
    doppler_metric = st.metric("Doppler Shift", "0 Hz")
    
    st.divider()
    
    st.subheader("Live Telemetry")
    volt_metric = st.metric("🔋 Battery", "Waiting...")
    temp_metric = st.metric("🌡️ Temp", "Waiting...")
    msg_metric = st.info("Status: Listening...")

    tracking_active = st.toggle("ACTIVATE TRACKING", value=False)

#src/web_ui/app.py

# ... (Previous code remains the same) ...

# --- The "Game Loop" ---
if tracking_active:
    
    # --- FIX START: Use Live TLEs instead of Hardcoded ones ---
    # We ask the engine: "Do you have this satellite in your downloaded file?"
    sat_obj = orbit_engine.get_satellite_by_name(selected_sat_name)
    
    if not sat_obj:
        # If the user selects "GTUSAT-1" (our fake one) or a missing sat
        st.error(f"⚠️ Could not find '{selected_sat_name}' in the live TLE file.")
        st.warning("Ensure the satellite name in satellites.json matches CelesTrak exactly.")
        st.stop()
    # --- FIX END ---
    
    base_freq = current_sat['frequency']
    
    # --- NEW: Start Recording ---
    logger = DataManager(selected_sat_name)
    
    while True:
        # 1. PHYSICS: Get Position
        pos = orbit_engine.get_position(sat_obj)
        
        # 2. RADIO: Mock Doppler
        mock_doppler = random.randint(-2000, 2000) 
        radio_core.set_doppler_freq(base_freq, mock_doppler)
        
        # 3. DATA: Mock Packet
        raw_packet = decoder.get_mock_packet()
        telemetry = decoder.parse_frame(raw_packet)
        
        # --- Save to Disk ---
        if telemetry:
            logger.log_packet(telemetry, pos, mock_doppler)
        
        # 4. UPDATE UI
        az_metric.metric("Azimuth", f"{pos['azimuth']:.2f}°")
        el_metric.metric("Elevation", f"{pos['elevation']:.2f}°")
        dist_metric.metric("Range", f"{pos['distance_km']:.0f} km")
        
        freq_metric.metric("Frequency", f"{(base_freq + mock_doppler)/1e6:.6f} MHz")
        doppler_metric.metric("Doppler Shift", f"{mock_doppler} Hz")
        
        if telemetry:
            volt_metric.metric("🔋 Battery", f"{telemetry['voltage']:.2f} V")
            temp_metric.metric("🌡️ Temp", f"{telemetry['temp']} °C")
            msg_metric.success(f"OBC Status: {telemetry['msg']}")
        
        # 5. PLOT: Polar Chart
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[90 - pos['elevation']], 
            theta=[pos['azimuth']],    
            mode='markers',
            marker=dict(size=15, color='red', symbol='cross'),
        ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 90]),
                angularaxis=dict(direction="clockwise", rotation=90)
            ),
            showlegend=False,
            height=400,
            margin=dict(l=20, r=20, t=20, b=20)
        )
        radar_chart.plotly_chart(fig)
        
        time.sleep(0.5)