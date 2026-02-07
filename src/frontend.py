# src/frontend.py
import streamlit as st
import requests
import time
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# --- CONFIG ---
BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="NGSC Mission Control", page_icon="🛰️", layout="wide")

# --- API HELPERS ---
def get_telemetry():
    """Fetch JSON from Backend."""
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=1)
        if response.status_code == 200:
            return response.json()
    except:
        return None
    return None

def send_command(action):
    """Post command to Backend."""
    try:
        requests.post(f"{BACKEND_URL}/command", json={"action": action})
        return True
    except:
        return False

# --- 3D VISUALIZATION ---
def create_3d_sat(pitch, roll):
    # Simple Cube Logic
    r_pitch = np.radians(pitch)
    r_roll = np.radians(roll)
    
    # Rotation Matrix (Simplified)
    c, s = np.cos(r_pitch), np.sin(r_pitch)
    Ry = np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    c, s = np.cos(r_roll), np.sin(r_roll)
    Rx = np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    
    # Vertices of a cube
    v = np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],
                  [-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]]) * 0.5
    
    v_rot = v @ Rx @ Ry  # Rotate
    
    fig = go.Figure(data=[
        go.Mesh3d(
            x=v_rot[:,0], y=v_rot[:,1], z=v_rot[:,2],
            color='#00FFFF', opacity=0.9, flatshading=True,
            i=[7,0,0,0,4,4,6,6,4,0,3,2],
            j=[3,4,1,2,5,6,5,2,0,1,6,3],
            k=[0,7,2,3,6,7,1,1,5,5,7,6]
        )
    ])
    fig.update_layout(scene=dict(
        xaxis=dict(visible=False, range=[-1,1]),
        yaxis=dict(visible=False, range=[-1,1]),
        zaxis=dict(visible=False, range=[-1,1]),
        bgcolor='rgba(0,0,0,0)'
    ), margin=dict(l=0,r=0,b=0,t=0), height=300, paper_bgcolor='rgba(0,0,0,0)')
    return fig

# --- MAIN UI ---
st.title("🛰️ NGSC Mission Control (Decoupled)")

# 1. Get Data
data = get_telemetry()

if not data:
    st.error("⚠️ BACKEND OFFLINE (Is 'uvicorn src.backend:app' running?)")
    st.stop()

# 2. Parse Data
telemetry = data["telemetry"]
status = telemetry.get("status", {})
led_state = status.get("led", "OFF")
solar_state = status.get("solar", False)
connected = data["connected"]

# 3. Header Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Link Status", "ONLINE" if connected else "OFFLINE", delta_color="normal" if connected else "off")
c2.metric("Pitch", f"{telemetry['pitch']:.2f}°")
c3.metric("Roll", f"{telemetry['roll']:.2f}°")
c4.metric("Power", "⚡ Solar" if solar_state else "🔋 Battery")

st.divider()

# 4. Main Body
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live Orientation")
    st.plotly_chart(create_3d_sat(telemetry['pitch'], telemetry['roll']), use_container_width=True)

with col2:
    st.subheader("Command Center")
    
    # Status Indicators
    s1, s2 = st.columns(2)
    if led_state == "ON":
        s1.success("💡 LED: ON")
    else:
        s1.info("⚫ LED: OFF")
        
    if solar_state:
        s2.success("☀️ PANELS: OPEN")
    else:
        s2.warning("🔒 PANELS: CLOSED")
    
    st.write("") # Spacer

    # Controls
    if st.button("📡 PING SATELLITE", use_container_width=True):
        send_command("PING")
        st.toast("Ping Sent!")
        
    c_a, c_b = st.columns(2)
    if c_a.button("🟢 LED ON", use_container_width=True):
        send_command("LED_ON")
    if c_b.button("🔴 LED OFF", use_container_width=True):
        send_command("LED_OFF")
        
    if st.button("🚀 DEPLOY SOLAR ARRAYS", use_container_width=True):
        send_command("DEPLOY_SOLAR")

# 5. Auto-Refresh
time.sleep(0.5)
st.rerun()