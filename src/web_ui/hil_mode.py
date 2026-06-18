# src/web_ui/hil_mode.py

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import requests
import os

# --- CONFIG ---
# Default to localhost for testing, but use the cloud URL if deployed
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

# --- CUSTOM CSS ---
def inject_hil_css():
    st.markdown(
        """
        <style>
        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        div.block-container {
            padding-top: 1.5rem !important;
        }
        div.stButton > button {
            width: 100%;
            border-radius: 6px;
            height: 3.2em;
            font-weight: 600;
        }
        .status-text {
            padding-top: 12px;
            font-size: 0.9em;
            font-weight: 500;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# --- API HELPERS ---
@st.cache_resource
def get_http_session():
    return requests.Session()

def get_backend_data():
    session = get_http_session()
    
    if "failed_pings" not in st.session_state:
        st.session_state.failed_pings = 0
    if "last_good_telemetry" not in st.session_state:
        st.session_state.last_good_telemetry = None

    try:
        response = session.get(f"{API_URL}/status", timeout=0.3)
        if response.status_code == 200:
            data = response.json()
            st.session_state.last_good_telemetry = data
            st.session_state.failed_pings = 0
            return data
    except requests.exceptions.RequestException:
        st.session_state.failed_pings += 1

    if st.session_state.failed_pings > 3:
        return None
        
    return st.session_state.last_good_telemetry


def send_command(cmd_string):
    session = get_http_session()
    headers = {"X-API-Key": "NGSC-SECURE-KEY-2026"}
    try:
        session.post(f"{API_URL}/command", json={"command": cmd_string, "action": cmd_string}, headers=headers, timeout=0.3)
        return True
    except requests.exceptions.RequestException:
        return False


def _parse_solar_status(solar_raw):
    if solar_raw is True:
        return "DEPLOYED"
    if solar_raw is False:
        return "RETRACTED"
    return solar_raw


# --- 3D VISUALIZATION ---
def create_3d_sat_fig(pitch, roll):
    vertices = (
        np.array(
            [
                [-1, -1, -1],
                [1, -1, -1],
                [1, 1, -1],
                [-1, 1, -1],
                [-1, -1, 1],
                [1, -1, 1],
                [1, 1, 1],
                [-1, 1, 1],
            ]
        )
        * 0.5
    )
    p, r = np.radians(pitch), np.radians(roll)
    Rx = np.array([[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]])
    Ry = np.array([[np.cos(r), 0, np.sin(r)], [0, 1, 0], [-np.sin(r), 0, np.cos(r)]])
    rv = vertices @ Ry @ Rx
    x, y, z = rv[:, 0], rv[:, 1], rv[:, 2]

    fig = go.Figure(
        data=[
            go.Mesh3d(
                x=x,
                y=y,
                z=z,
                color="#00FFFF",
                opacity=0.9,
                flatshading=True,
                i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
                j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
                k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            )
        ]
    )

    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-1, 1]),
            yaxis=dict(visible=False, range=[-1, 1]),
            zaxis=dict(visible=False, range=[-1, 1]),
            bgcolor="rgba(0,0,0,0)",
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        autosize=True,
    )
    return fig


@st.fragment(run_every="0.5s")
def hil_live_telemetry_panel():
    """Decoupled 2Hz panel: polls backend and rebuilds metrics + 3D mesh only."""
    data = get_backend_data()
    if not data:
        st.error("BACKEND OFFLINE - Run 'uvicorn src.backend:app --reload'")
        return

    telemetry = data.get("telemetry", {})
    status = telemetry.get("status", {})
    led_state = status.get("led", "OFF")
    solar_status = _parse_solar_status(status.get("solar", "RETRACTED"))
    solar_mode = status.get("mode", "MANUAL")
    pitch = telemetry.get("pitch", 0.0)
    roll = telemetry.get("roll", 0.0)
    link_active = data.get("connected", False)

    link_label = "ACTIVE" if link_active else "STALE"
    link_delta = "normal" if link_active else "inverse"

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Telemetry Link", link_label, delta_color=link_delta)
    m2.metric("Pitch", f"{pitch:.2f}°")
    m3.metric("Roll", f"{roll:.2f}°")

    if solar_status == "DEPLOYED":
        m4.metric("Power", "Generating", "Solar")
    else:
        m4.metric("Power", "Draining", "Battery", delta_color="inverse")

    st.caption(
        f"Backend: {API_URL} | LED: {led_state} | Solar: {solar_status} ({solar_mode})"
    )
    st.plotly_chart(create_3d_sat_fig(pitch, roll), use_container_width=True)


def _init_led_toggle_from_backend():
    if "led_switch_widget" in st.session_state:
        return
    data = get_backend_data()
    led_state = "OFF"
    if data:
        led_state = data.get("telemetry", {}).get("status", {}).get("led", "OFF")
    st.session_state.led_switch_widget = led_state == "ON"


def _render_hil_controls():
    """Static command panel — drawn once; fragment picks up state changes at 2Hz."""
    _init_led_toggle_from_backend()

    with st.container(border=True):
        st.caption("PAYLOAD SYSTEMS")

        pl_c1, pl_c2 = st.columns([1, 1.5])

        with pl_c1:
            def on_led_toggle():
                new_state = st.session_state.led_switch_widget
                result = send_command("LED_ON" if new_state else "LED_OFF")
                if result:
                    st.toast(f"LED {'ON' if new_state else 'OFF'} command sent")
                else:
                    st.error("Failed to send command")
                    st.session_state.led_switch_widget = not new_state

            st.toggle(
                "LED Power",
                key="led_switch_widget",
                on_change=on_led_toggle,
            )

        with pl_c2:
            st.markdown(
                '<div class="status-text">State: <b style="color:#888">SYNCING...</b></div>',
                unsafe_allow_html=True,
            )

    st.write("")

    with st.container(border=True):
        st.caption("SOLAR ARRAY")
        st.info("Command mode active — status updates in live panel.")

        b1, b2, b3 = st.columns(3)
        with b1:
            if st.button("OPEN"):
                send_command("SOLAR_DEPLOY")
                st.toast("Deploy command sent")
        with b2:
            if st.button("CLOSE"):
                send_command("SOLAR_RETRACT")
                st.toast("Retract command sent")
        with b3:
            if st.button("AUTO", type="secondary"):
                send_command("MODE_AUTO")
                st.toast("Auto mode command sent")


def run_hil_telemetry():
    inject_hil_css()

    c_title, c_status, c_ping = st.columns([5, 2, 1.5])

    with c_title:
        st.markdown(
            "<h2 style='margin:0; padding:0;'>HIL DIGITAL TWIN</h2>",
            unsafe_allow_html=True,
        )

    with c_status:
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 5px;">
                <span style="font-size: 0.8em; color: #888;">{API_URL}</span><br>
                <b>MODE: <span style="color: #00FFFF;">FRAGMENT 2Hz</span></b>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c_ping:
        st.write("")
        if st.button("PING", help="Test uplink latency"):
            if send_command("PING"):
                st.toast("Ping sent — check terminal.")
            else:
                st.error("Ping failed — backend unreachable.")

    st.markdown("---")

    col_vis, col_ctrl = st.columns([1.5, 1])

    with col_vis:
        hil_live_telemetry_panel()

    with col_ctrl:
        _render_hil_controls()
