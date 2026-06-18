# src/web_ui/app.py
import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
import json
import sys
import os
import random

# --- PATH SETUP ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../.."))
if project_root not in sys.path:
    sys.path.append(project_root)

# --- IMPORTS ---
from src.orbit_engine import OrbitEngine
from src.radio_core import RadioCore
from src.decoder import TelemetryDecoder
from src.data_manager import DataManager, close_tracking_logger
from src.pass_predictor import PassPredictor
from src.web_ui.hil_mode import run_hil_telemetry

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="NGSC Mission Control",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded",
)

MAP_REFRESH_INTERVAL = 20


# --- HELPER FUNCTIONS ---
def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def create_radar_fig(azimuth, elevation, is_active=False):
    plot_el = max(0, elevation)
    marker_color = "#00FF00" if is_active else "#444444"
    symbol = "cross" if is_active else "circle"
    opacity = 1.0 if is_active else 0.5

    fig = go.Figure()
    fig.add_trace(
        go.Scatterpolar(
            r=[90 - plot_el],
            theta=[azimuth],
            mode="markers",
            marker=dict(
                size=20,
                color=marker_color,
                symbol=symbol,
                line=dict(width=2, color="white"),
                opacity=opacity,
            ),
        )
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        polar=dict(
            bgcolor="rgba(20, 20, 30, 0.4)",
            radialaxis=dict(
                visible=True,
                range=[0, 90],
                showline=False,
                tickfont=dict(color="#888"),
                gridcolor="#333",
            ),
            angularaxis=dict(
                direction="clockwise", rotation=90, color="#00FFFF", gridcolor="#444"
            ),
        ),
        showlegend=False,
        height=350,
        margin=dict(l=20, r=20, t=20, b=20),
        autosize=True,
    )
    return fig


def create_map_fig(pos, ground_track, st_lat, st_lon):
    idx = len(ground_track["lat"]) // 2
    sat_lat = ground_track["lat"][idx]
    sat_lon = ground_track["lon"][idx]

    fig = go.Figure()
    fig.add_trace(
        go.Scattergeo(
            lat=ground_track["lat"],
            lon=ground_track["lon"],
            mode="lines",
            line=dict(width=2, color="#00FFFF"),
            hoverinfo="none",
        )
    )
    fig.add_trace(
        go.Scattergeo(
            lat=[st_lat],
            lon=[st_lon],
            mode="markers",
            marker=dict(size=10, color="#FF00FF", symbol="diamond"),
            hoverinfo="text",
            text=["Ahmedabad Station"],
        )
    )
    fig.add_trace(
        go.Scattergeo(
            lat=[sat_lat],
            lon=[sat_lon],
            mode="markers",
            marker=dict(
                size=15,
                color="#00FF00",
                symbol="circle-open-dot",
                line=dict(width=3, color="white"),
            ),
            hoverinfo="text",
            text=["Satellite"],
        )
    )
    fig.update_layout(
        geo=dict(
            projection_type="natural earth",
            showland=True,
            landcolor="rgb(20, 20, 20)",
            showocean=True,
            oceancolor="rgb(10, 10, 15)",
            showcountries=True,
            countrycolor="rgb(50, 50, 50)",
            bgcolor="rgba(0,0,0,0)",
        ),
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
        height=400,
        autosize=True,
    )
    return fig


def _ensure_tracking_logger(satellite_name):
    if not st.session_state.get("tracking_initialized"):
        st.session_state.tracking_initialized = True
        st.session_state.tracking_loop_count = 0
        st.session_state.tracking_satellite = satellite_name
        st.session_state.tracking_logger = DataManager(satellite_name)
    elif st.session_state.get("tracking_satellite") != satellite_name:
        close_tracking_logger(st.session_state.get("tracking_logger"))
        st.session_state.tracking_satellite = satellite_name
        st.session_state.tracking_loop_count = 0
        st.session_state.tracking_logger = DataManager(satellite_name)
    return st.session_state.tracking_logger


def _stop_tracking_session():
    close_tracking_logger(st.session_state.get("tracking_logger"))
    st.session_state.tracking_initialized = False
    st.session_state.tracking_loop_count = 0
    if "tracking_logger" in st.session_state:
        del st.session_state.tracking_logger
    if "tracking_satellite" in st.session_state:
        del st.session_state.tracking_satellite


@st.fragment(run_every="0.5s")
def mission_control_live_panel(sat_obj, satellite_name, base_freq, st_lat, st_lon):
    """Decoupled 2Hz panel: physics, logging, metrics, radar, and throttled map."""
    if not st.session_state.get("mc_tracking_toggle", False) or sat_obj is None:
        return

    logger = _ensure_tracking_logger(satellite_name)
    loop_counter = st.session_state.tracking_loop_count

    pos = orbit_engine.get_position(sat_obj)
    is_visible = pos["elevation"] > 0

    mock_doppler = random.randint(-2000, 2000)
    radio_core.set_doppler_freq(base_freq, mock_doppler)
    packet = decoder.get_mock_packet()
    telem = decoder.parse_frame(packet)

    voltage = 0
    temp = 0
    if telem:
        logger.log_packet(telem, pos, mock_doppler)
        voltage = telem.get("voltage", 0)
        temp = telem.get("temp", 0)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Polar Radar")
        c1, c2, c3 = st.columns(3)
        c1.metric("Azimuth", f"{pos['azimuth']:.2f}°")
        if is_visible:
            c2.metric("Elevation", f"{pos['elevation']:.2f}°", "LOCKED")
        else:
            c2.metric(
                "Elevation",
                f"{pos['elevation']:.2f}°",
                "LOS",
                delta_color="inverse",
            )
        c3.metric("Range", f"{pos['distance_km']:.0f} km")

        active_state = is_visible
        st.plotly_chart(
            create_radar_fig(pos["azimuth"], pos["elevation"], is_active=active_state),
            use_container_width=True,
        )

    with col2:
        st.subheader("Telemetry Link")
        st.metric("Frequency", f"{(base_freq + mock_doppler) / 1e6:.6f} MHz")
        st.metric("Doppler", f"{mock_doppler} Hz")
        st.divider()
        if is_visible:
            st.metric("Battery", f"{voltage:.2f} V")
            st.metric("Temp", f"{temp} °C")
        else:
            st.metric("Battery", "No Signal")
            st.metric("Temp", "No Signal")

    st.subheader("Global Ground Track")
    if loop_counter % MAP_REFRESH_INTERVAL == 0:
        track_data = orbit_engine.get_ground_track(sat_obj, duration_minutes=180)
        st.session_state.mc_cached_track = track_data
        st.session_state.mc_cached_track_pos = pos

    track_data = st.session_state.get("mc_cached_track")
    track_pos = st.session_state.get("mc_cached_track_pos", pos)
    if track_data:
        st.plotly_chart(
            create_map_fig(track_pos, track_data, st_lat, st_lon),
            use_container_width=True,
        )

    st.session_state.tracking_loop_count = loop_counter + 1


# --- INIT ---
@st.cache_resource
def get_system():
    try:
        with open(os.path.join(project_root, "config/satellites.json"), "r") as f:
            sat_data = json.load(f)
            sat_map = {s["name"]: s for s in sat_data["satellites"]}
    except OSError:
        st.stop()
    engine = OrbitEngine()
    return (
        sat_map,
        engine,
        RadioCore(mock_mode=True),
        TelemetryDecoder(),
        PassPredictor(engine.station),
    )


sat_map, orbit_engine, radio_core, decoder, predictor = get_system()
css_path = os.path.join(current_dir, "assets", "style.css")
if os.path.exists(css_path):
    load_css(css_path)

# --- SIDEBAR ---
st.sidebar.title("NGSC V3.0")
app_mode = st.sidebar.radio(
    "Select Module", ["Mission Control", "Pass Predictor", "Data Vault", "HIL Telemetry"]
)

if "last_module" not in st.session_state:
    st.session_state.last_module = app_mode

if st.session_state.last_module != app_mode:
    if st.session_state.last_module == "Mission Control":
        _stop_tracking_session()
    st.session_state.last_module = app_mode
    st.rerun()

st.sidebar.divider()
selected_sat_name = st.sidebar.selectbox("Active Satellite", list(sat_map.keys()))
current_sat_info = sat_map[selected_sat_name]
custom_tle = current_sat_info.get("custom_tle", None)
sat_obj = orbit_engine.get_satellite_by_name(selected_sat_name, custom_tle_lines=custom_tle)
if sat_obj:
    st.sidebar.success(f"Locked: {selected_sat_name}")

st_lat = float(orbit_engine.config["GROUND_STATION"]["latitude"])
st_lon = float(orbit_engine.config["GROUND_STATION"]["longitude"])

# ==========================
# MISSION CONTROL
# ==========================
if app_mode == "Mission Control":
    st.markdown(
        f"""
    <h1 style='text-align: left; margin-top: -50px;'>MISSION CONTROL</h1>
    <p style='color: #00FFFF;'>STATUS: ONLINE | STATION: AHMEDABAD | TRACKING: {selected_sat_name}</p>
    <hr style='border-color: #00FFFF; margin-top: -10px;'>
    """,
        unsafe_allow_html=True,
    )

    tracking_active = st.toggle("ACTIVATE TRACKING", key="mc_tracking_toggle")

    if not tracking_active and st.session_state.get("tracking_initialized"):
        _stop_tracking_session()

    if tracking_active and sat_obj:
        mission_control_live_panel(
            sat_obj,
            selected_sat_name,
            current_sat_info["frequency"],
            st_lat,
            st_lon,
        )
    elif sat_obj:
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Polar Radar")
            pos = orbit_engine.get_position(sat_obj)
            c1, c2, c3 = st.columns(3)
            c1.metric("Azimuth", f"{pos['azimuth']:.2f}°")
            c2.metric("Elevation", f"{pos['elevation']:.2f}°")
            c3.metric("Range", f"{pos['distance_km']:.0f} km")
            st.plotly_chart(
                create_radar_fig(pos["azimuth"], pos["elevation"], is_active=False),
                use_container_width=True,
            )

        with col2:
            st.subheader("Telemetry Link")
            st.metric("Frequency", "--- MHz")
            st.metric("Doppler", "--- Hz")
            st.divider()
            st.metric("Battery", "---")
            st.metric("Temp", "---")

        st.subheader("Global Ground Track")
        track_data = orbit_engine.get_ground_track(sat_obj, duration_minutes=180)
        st.plotly_chart(
            create_map_fig(pos, track_data, st_lat, st_lon),
            use_container_width=True,
        )

# ==========================
# PASS PREDICTOR
# ==========================
elif app_mode == "Pass Predictor":
    st.header(f"Schedule: {selected_sat_name}")
    if st.button("Calculate Next 24h"):
        with st.spinner("Calculating..."):
            passes = predictor.get_next_passes(sat_obj)
        if passes:
            st.success(
                f"Next AOS: {passes[0]['aos'].utc_datetime().strftime('%H:%M:%S UTC')}"
            )
            data_rows = [
                [
                    p["aos"].utc_datetime().strftime("%H:%M:%S"),
                    f"{p['max_el']:.1f}°",
                    p["duration_str"],
                ]
                for p in passes
            ]
            st.table(
                pd.DataFrame(
                    data_rows, columns=["Start (UTC)", "Max Elevation", "Duration"]
                )
            )
        else:
            st.warning("No visible passes found.")

# ==========================
# DATA VAULT
# ==========================
elif app_mode == "Data Vault":
    st.header("Data Vault")

    data_source = st.radio(
        "Data Source:", ["Mission Control Logs", "HIL Telemetry Logs"], horizontal=True
    )

    base_log_dir = os.path.join(project_root, "data/telemetry")
    if data_source == "HIL Telemetry Logs":
        log_dir = os.path.join(base_log_dir, "hil_side")
    else:
        log_dir = os.path.join(base_log_dir, "mission_control")

    files = []
    if os.path.exists(log_dir):
        all_items = sorted(os.listdir(log_dir), reverse=True)
        files = [
            f
            for f in all_items
            if f.endswith(".csv") and os.path.isfile(os.path.join(log_dir, f))
        ]

    if files:
        c1, c2 = st.columns([3, 1])
        with c1:
            selected_file = st.selectbox("Select Log File", files)
        with c2:
            st.write("")
            st.write("")
            if st.button("DELETE FILE", type="primary", key="vault_delete"):
                try:
                    os.remove(os.path.join(log_dir, selected_file))
                    st.toast(f"Deleted {selected_file}")
                    time.sleep(1)
                    st.rerun()
                except OSError as e:
                    st.error(f"Error deleting file: {e}")

        if selected_file:
            file_path = os.path.join(log_dir, selected_file)
            if os.path.exists(file_path):
                df_log = pd.read_csv(file_path)
                st.dataframe(df_log, width="stretch")

                if not df_log.empty:
                    st.subheader("Data Analysis")
                    if "light" in df_log.columns:
                        st.line_chart(df_log, x="timestamp", y="light")
                    elif "battery_voltage" in df_log.columns:
                        st.line_chart(df_log, x="timestamp", y="battery_voltage")
            else:
                st.warning("File deleted.")
    else:
        st.info(f"No log files found in {data_source}.")

# ==========================
# HIL TELEMETRY
# ==========================
elif app_mode == "HIL Telemetry":
    run_hil_telemetry()
