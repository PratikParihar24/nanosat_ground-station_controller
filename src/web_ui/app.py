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

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NGSC Mission Control", 
    page_icon="🛰️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER FUNCTIONS ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

def create_radar_fig(azimuth, elevation, is_active=False):
    plot_el = max(0, elevation)
    marker_color = '#00FF00' if is_active else '#444444'
    symbol = 'cross' if is_active else 'circle'
    opacity = 1.0 if is_active else 0.5

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=[90 - plot_el], 
        theta=[azimuth],
        mode='markers',
        marker=dict(size=20, color=marker_color, symbol=symbol, line=dict(width=2, color='white'), opacity=opacity),
    ))
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
    )
    return fig

def create_map_fig(pos, ground_track, st_lat, st_lon):
    # Calculate current sat position (Lat/Lon) from the middle of the track (approx)
    # In a real system, we'd calculate this precisely, but for UI smoothnes...
    # We grab the last point in the 'past' list, which is 'now'.
    # Actually, let's just use the ground_track mid-point for safety.
    idx = len(ground_track['lat']) // 2
    sat_lat = ground_track['lat'][idx]
    sat_lon = ground_track['lon'][idx]

    fig = go.Figure()

    # 1. Orbit Path
    fig.add_trace(go.Scattergeo(
        lat=ground_track['lat'], lon=ground_track['lon'],
        mode='lines', line=dict(width=2, color='#00FFFF'),
        hoverinfo='none'
    ))

    # 2. Ground Station
    fig.add_trace(go.Scattergeo(
        lat=[st_lat], lon=[st_lon],
        mode='markers', marker=dict(size=10, color='#FF00FF', symbol='diamond'),
        hoverinfo='text', text=['Ahmedabad Station']
    ))

    # 3. Satellite
    fig.add_trace(go.Scattergeo(
        lat=[sat_lat], lon=[sat_lon],
        mode='markers', marker=dict(size=15, color='#00FF00', symbol='circle-open-dot', line=dict(width=3, color='white')),
        hoverinfo='text', text=['Satellite']
    ))

    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showland=True, landcolor="rgb(20, 20, 20)",
            showocean=True, oceancolor="rgb(10, 10, 15)",
            showcountries=True, countrycolor="rgb(50, 50, 50)",
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=400
    )
    return fig

# --- INIT ---
@st.cache_resource
def get_system():
    try:
        with open(os.path.join(project_root, 'config/satellites.json'), 'r') as f:
            sat_data = json.load(f)
            sat_map = {s['name']: s for s in sat_data['satellites']}
    except: st.stop()
    return sat_map, OrbitEngine(), RadioCore(mock_mode=True), TelemetryDecoder(), PassPredictor(OrbitEngine().station)

sat_map, orbit_engine, radio_core, decoder, predictor = get_system()
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path): load_css(css_path)

# --- SIDEBAR ---
st.sidebar.title("🚀 NGSC V3.0")
app_mode = st.sidebar.radio("Select Module", ["Mission Control", "Pass Predictor", "Data Vault"])
st.sidebar.divider()
selected_sat_name = st.sidebar.selectbox("Active Satellite", list(sat_map.keys()))
current_sat_info = sat_map[selected_sat_name]
custom_tle = current_sat_info.get('custom_tle', None)
sat_obj = orbit_engine.get_satellite_by_name(selected_sat_name, custom_tle_lines=custom_tle)
if sat_obj: st.sidebar.success(f"Locked: {selected_sat_name}")

# ==========================
# MISSION CONTROL
# ==========================
if app_mode == "Mission Control":
    st.markdown(f"""
    <h1 style='text-align: left; margin-top: -50px;'>🛰️ MISSION CONTROL</h1>
    <p style='color: #00FFFF;'>STATUS: ONLINE | STATION: AHMEDABAD | TRACKING: {selected_sat_name}</p>
    <hr style='border-color: #00FFFF; margin-top: -10px;'>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    # 1. SETUP UI CONTAINERS (STATIC)
    with col1:
        st.subheader("Polar Radar")
        c1, c2, c3 = st.columns(3)
        m_az = c1.metric("Azimuth", "0.0°")
        m_el = c2.metric("Elevation", "0.0°")
        m_dist = c3.metric("Range", "0 km")
        
        # KEY FIX: Define the empty container ONCE
        radar_placeholder = st.empty()

    with col2:
        st.subheader("Telemetry Link")
        m_freq = st.metric("Frequency", "--- MHz")
        m_dop = st.metric("Doppler", "--- Hz")
        st.divider()
        m_volt = st.metric("Battery", "---")
        m_temp = st.metric("Temp", "---")
        tracking_active = st.toggle("ACTIVATE TRACKING", value=False)
    
    st.subheader("🌍 Global Ground Track")
    # KEY FIX: Define the map container ONCE
    map_placeholder = st.empty()

    # 2. INITIAL STATIC RENDER (So it's not empty at start)
    if sat_obj:
        pos = orbit_engine.get_position(sat_obj)
        # Radar
        fig_radar = create_radar_fig(pos['azimuth'], pos['elevation'], is_active=False)
        radar_placeholder.plotly_chart(fig_radar, use_container_width=True, key="radar_static")
        
        # Map (Heavy calculation, do it once)
        st_lat = float(orbit_engine.config['GROUND_STATION']['latitude'])
        st_lon = float(orbit_engine.config['GROUND_STATION']['longitude'])
        track_data = orbit_engine.get_ground_track(sat_obj, duration_minutes=180)
        fig_map = create_map_fig(pos, track_data, st_lat, st_lon)
        map_placeholder.plotly_chart(fig_map, use_container_width=True, key="map_static")

    # 3. LIVE LOOP
    # 3. LIVE LOOP
    if tracking_active and sat_obj:
        logger = DataManager(selected_sat_name)
        base_freq = current_sat_info['frequency']
        loop_counter = 0

        while True:
            # Physics & Data
            pos = orbit_engine.get_position(sat_obj)
            is_visible = pos['elevation'] > 0
            
            mock_doppler = random.randint(-2000, 2000) 
            radio_core.set_doppler_freq(base_freq, mock_doppler)
            packet = decoder.get_mock_packet()
            telem = decoder.parse_frame(packet)
            if telem: logger.log_packet(telem, pos, mock_doppler)

            # UI METRICS (Fast)
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

            # RADAR UPDATE (Fast - 0.5s)
            fig_radar = create_radar_fig(pos['azimuth'], pos['elevation'], is_active=active_state)
            
            # FIX: Removed 'key' argument to prevent DuplicateKeyError
            # FIX: Changed use_container_width to match new Streamlit standards (or kept distinct)
            radar_placeholder.plotly_chart(fig_radar, use_container_width=True)
            
            # MAP UPDATE (Slow - 10s)
            if loop_counter % 20 == 0:
                track_data = orbit_engine.get_ground_track(sat_obj, duration_minutes=180)
                fig_map = create_map_fig(pos, track_data, st_lat, st_lon)
                
                # FIX: Removed 'key' argument here too
                map_placeholder.plotly_chart(fig_map, use_container_width=True)
            
            loop_counter += 1
            time.sleep(0.5)

# ==========================
# PASS PREDICTOR
# ==========================
elif app_mode == "Pass Predictor":
    st.header(f"📅 Schedule: {selected_sat_name}")
    if st.button("Calculate Next 24h"):
        with st.spinner("Calculating..."):
            passes = predictor.get_next_passes(sat_obj)
        if passes:
            st.success(f"Next AOS: {passes[0]['aos'].utc_datetime().strftime('%H:%M:%S UTC')}")
            data_rows = [[p['aos'].utc_datetime().strftime("%H:%M:%S"), f"{p['max_el']:.1f}°", p['duration_str']] for p in passes]
            st.table(pd.DataFrame(data_rows, columns=["Start (UTC)", "Max Elevation", "Duration"]))
        else: st.warning("No visible passes found.")

# ==========================
# DATA VAULT
# ==========================
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