# src/web_ui/app.py

import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import json
import sys
import os
import random
from datetime import datetime

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

from src.orbit_engine import OrbitEngine
from src.radio_core import RadioCore
from src.decoder import TelemetryDecoder
from src.data_manager import DataManager
from src.pass_predictor import PassPredictor

# --- PAGE CONFIG (Layout) ---
st.set_page_config(
    page_title="NGSC Mission Control", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER: CSS LOADER ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# --- HELPER: RADAR DRAWER ---
def create_radar_fig(azimuth, elevation, is_active=False):
    """Generates the Plotly Figure for the Radar"""
    plot_el = max(0, elevation) # Clamp negative values to 0 for display
    
    if is_active:
        marker_color = '#00FF00' # Neon Green
        symbol = 'cross'
        opacity = 1.0
    else:
        marker_color = '#444444' # Dim Grey
        symbol = 'circle'
        opacity = 0.5

    fig = go.Figure()
    
    # The Satellite Dot
    fig.add_trace(go.Scatterpolar(
        r=[90 - plot_el], 
        theta=[azimuth],
        mode='markers',
        marker=dict(size=20, color=marker_color, symbol=symbol, line=dict(width=2, color='white'), opacity=opacity),
        name='Satellite'
    ))
    
    # The Cyberpunk Grid Layout
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        polar=dict(
            bgcolor='rgba(20, 20, 30, 0.4)',
            radialaxis=dict(visible=True, range=[0, 90], showline=False, tickfont=dict(color='#888'), gridcolor='#333'),
            angularaxis=dict(direction="clockwise", rotation=90, color='#00FFFF', gridcolor='#444')
        ),
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(color="white")
    )
    return fig

# --- INITIALIZATION ---
@st.cache_resource
def get_system():
    try:
        with open(os.path.join(project_root, 'config/satellites.json'), 'r') as f:
            sat_data = json.load(f)
            sat_map = {s['name']: s for s in sat_data['satellites']}
    except:
        st.error("Config Error: satellites.json missing.")
        st.stop()
        
    orbit = OrbitEngine()
    radio = RadioCore(mock_mode=True)
    decoder = TelemetryDecoder()
    predictor = PassPredictor(orbit.station)
    return sat_map, orbit, radio, decoder, predictor

# Load System & Styles
sat_map, orbit_engine, radio_core, decoder, predictor = get_system()
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    load_css(css_path)

# --- SIDEBAR ---
st.sidebar.title("🚀 NGSC V3.0")
app_mode = st.sidebar.radio("Select Module", ["Mission Control", "Pass Predictor", "Data Vault"])
st.sidebar.divider()

st.sidebar.header("Target Config")
selected_sat_name = st.sidebar.selectbox("Active Satellite", list(sat_map.keys()))
current_sat_info = sat_map[selected_sat_name]

# Load Satellite Logic
custom_tle = current_sat_info.get('custom_tle', None)
sat_obj = orbit_engine.get_satellite_by_name(selected_sat_name, custom_tle_lines=custom_tle)

if sat_obj:
    source = "Custom" if custom_tle else "CelesTrak"
    st.sidebar.success(f"Locked: {selected_sat_name}")
    st.sidebar.caption(f"Source: {source}")
else:
    st.sidebar.error("TLE Missing")

# ==========================================
# PAGE 1: MISSION CONTROL
# ==========================================
if app_mode == "Mission Control":
    # Custom Header (Replaces the standard title)
    st.markdown(f"""
    <h1 style='text-align: left; margin-top: -50px;'>🛰️ MISSION CONTROL</h1>
    <p style='color: #00FFFF;'>STATUS: ONLINE | STATION: AHMEDABAD | TRACKING: {selected_sat_name}</p>
    <hr style='border-color: #00FFFF; margin-top: -10px;'>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Polar Radar")
        
        # 1. SETUP UI CONTAINERS
        c1, c2, c3 = st.columns(3)
        m_az = c1.metric("Azimuth", "0.0°")
        m_el = c2.metric("Elevation", "0.0°")
        m_dist = c3.metric("Range", "0 km")
        
        radar_chart = st.empty()
        
        # 2. RENDER INITIAL STATIC RADAR (So it's not empty!)
        if sat_obj:
            initial_pos = orbit_engine.get_position(sat_obj)
            initial_fig = create_radar_fig(initial_pos['azimuth'], initial_pos['elevation'], is_active=False)
            radar_chart.plotly_chart(initial_fig, use_container_width=True)

    with col2:
        st.subheader("Telemetry Link")
        m_freq = st.metric("Frequency", f"{current_sat_info['frequency']/1e6} MHz")
        m_dop = st.metric("Doppler", "0 Hz")
        
        st.divider()
        m_volt = st.metric("Battery", "No Signal")
        m_temp = st.metric("Temp", "No Signal")
        
        # Tracking Switch
        tracking_active = st.toggle("ACTIVATE TRACKING", value=False)

    # 3. THE LIVE LOOP
    if tracking_active and sat_obj:
        logger = DataManager(selected_sat_name)
        base_freq = current_sat_info['frequency']
        
        while True:
            # Physics
            pos = orbit_engine.get_position(sat_obj)
            is_visible = pos['elevation'] > 0
            
            # Radio/Data (Mock)
            mock_doppler = random.randint(-2000, 2000) 
            radio_core.set_doppler_freq(base_freq, mock_doppler)
            
            packet = decoder.get_mock_packet()
            telem = decoder.parse_frame(packet)
            
            if telem:
                logger.log_packet(telem, pos, mock_doppler)

            # UI Updates
            m_az.metric("Azimuth", f"{pos['azimuth']:.2f}°")
            m_dist.metric("Range", f"{pos['distance_km']:.0f} km")
            m_freq.metric("Frequency", f"{(base_freq+mock_doppler)/1e6:.6f} MHz")
            m_dop.metric("Doppler", f"{mock_doppler} Hz")

            if is_visible:
                m_el.metric("Elevation", f"{pos['elevation']:.2f}°", "LOCKED")
                m_volt.metric("Battery", f"{telem['voltage']:.2f} V")
                m_temp.metric("Temp", f"{telem['temp']} °C")
                active_state = True
            else:
                m_el.metric("Elevation", f"{pos['elevation']:.2f}°", "LOS", delta_color="inverse")
                m_volt.metric("Battery", "No Signal")
                m_temp.metric("Temp", "No Signal")
                active_state = False

            # Update Radar using helper function
            fig = create_radar_fig(pos['azimuth'], pos['elevation'], is_active=active_state)
            radar_chart.plotly_chart(fig, use_container_width=True)
            
            time.sleep(0.5)

# ==========================================
# PAGE 2: PASS PREDICTOR
# ==========================================
elif app_mode == "Pass Predictor":
    st.header(f"📅 Schedule: {selected_sat_name}")
    
    if st.button("Calculate Next 24h"):
        with st.spinner("Calculating..."):
            passes = predictor.get_next_passes(sat_obj)
        if passes:
            st.success(f"Next AOS: {passes[0]['aos'].utc_datetime().strftime('%H:%M:%S UTC')}")
            
            # Create Table Data
            data_rows = [[p['aos'].utc_datetime().strftime("%H:%M:%S"), f"{p['max_el']:.1f}°", p['duration_str']] for p in passes]
            df = pd.DataFrame(data_rows, columns=["Start Time (UTC)", "Max Elevation", "Duration"])
            
            # Display Table (CSS will now make this bright!)
            st.table(df)
        else:
            st.warning("No visible passes found.")

# ==========================================
# PAGE 3: DATA VAULT
# ==========================================
elif app_mode == "Data Vault":
    st.header("💾 Data Vault")
    log_dir = os.path.join(project_root, 'data/telemetry')
    if os.path.exists(log_dir):
        files = sorted(os.listdir(log_dir), reverse=True)
        selected_file = st.selectbox("Select Log", files)
        if selected_file:
            df_log = pd.read_csv(os.path.join(log_dir, selected_file))
            st.dataframe(df_log, use_container_width=True)
            if not df_log.empty and 'battery_voltage' in df_log.columns:
                st.line_chart(df_log, x='timestamp', y='battery_voltage')