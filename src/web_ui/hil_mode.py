import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
from src.udp_bridge import get_latest_data

# --- 3D HELPER FUNCTIONS ---
def get_rotation_matrix(pitch, roll, yaw):
    """Creates a 3D rotation matrix from Euler angles (Degrees)."""
    p, r, y = np.radians(pitch), np.radians(roll), np.radians(yaw)
    Rx = np.array([[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]])
    Ry = np.array([[np.cos(r), 0, np.sin(r)], [0, 1, 0], [-np.sin(r), 0, np.cos(r)]])
    Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
    return Rz @ Ry @ Rx

def create_3d_sat_fig(pitch, roll, yaw):
    """Generates a Plotly 3D cube."""
    vertices = np.array([
        [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
        [-1, -1, 1],  [1, -1, 1],  [1, 1, 1],  [-1, 1, 1]
    ]) * 0.5 

    R = get_rotation_matrix(pitch, roll, yaw)
    rotated_vertices = vertices @ R.T
    x, y, z = rotated_vertices[:,0], rotated_vertices[:,1], rotated_vertices[:,2]
    
    i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2]
    j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3]
    k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6]

    fig = go.Figure(data=[
        go.Mesh3d(x=x, y=y, z=z, i=i, j=j, k=k, color='#00FFFF', opacity=0.9, flatshading=True, name='CubeSat')
    ])
    
    fig.update_layout(
        scene=dict(xaxis=dict(visible=False, range=[-1,1]), yaxis=dict(visible=False, range=[-1,1]), zaxis=dict(visible=False, range=[-1,1]), bgcolor='rgba(0,0,0,0)', aspectmode='cube'), 
        margin=dict(l=0, r=0, b=0, t=0), paper_bgcolor='rgba(0,0,0,0)', height=400
    )
    return fig

# --- MAIN HIL FUNCTION ---
def run_hil_telemetry():
    st.markdown("""
    <h1 style='text-align: left; margin-top: -50px;'>🛰️ HIL TELEMETRY TWIN</h1>
    <p style='color: #00FF00;'>PROTOCOL: UDP:4210 | SOURCE: LIVE HARDWARE</p>
    <hr style='border-color: #00FF00; margin-top: -10px;'>
    """, unsafe_allow_html=True)
    
    # 1. Fetch Latest Data
    telemetry = get_latest_data()
    
    # 2. Metrics Grid
    k1, k2, k3, k4 = st.columns(4)
    
    status_text = "ONLINE" if telemetry['connected'] else "OFFLINE"
    status_color = "normal" if telemetry['connected'] else "off"
    
    k1.metric("Link Status", status_text, delta_color=status_color)
    k2.metric("Pitch", f"{telemetry['pitch']:.2f}°")
    k3.metric("Roll", f"{telemetry['roll']:.2f}°")
    k4.metric("Power State", "☀️ Charging" if telemetry['light'] > 500 else "🌑 Eclipse")
    
    st.markdown("---")
    
    # 3. Visuals (Cube & Data)
    v1, v2 = st.columns([2, 1])
    
    with v1:
        st.subheader("Digital Twin Orientation")
        fig = create_3d_sat_fig(telemetry['pitch'], telemetry['roll'], 0)
        # Using a static key here prevents blinking
        st.plotly_chart(fig, use_container_width=True, key="hil_cube_sat_final")
    
    with v2:
        st.subheader("Subsystem Health")
        g_force = telemetry['accel_z']
        g_stat = "STABLE"
        g_col = "normal"
        if abs(g_force) > 20: 
            g_stat = "🚀 LAUNCH"
            g_col = "off"
        elif abs(g_force) < 2:
            g_stat = "🌌 ZERO-G"
            g_col = "off"
        
        st.metric("G-Force (Z-Axis)", f"{g_force:.2f} m/s²", g_stat, delta_color=g_col)
        st.caption("Incoming Packet Stream:")
        st.code(f"ID: SAT1\nP: {telemetry['pitch']:.2f}\nR: {telemetry['roll']:.2f}\nL: {telemetry['light']}\nZ: {telemetry['accel_z']:.2f}", language="yaml")

    # 4. Live Update Loop (Frame Based)
    time.sleep(0.1)
    st.rerun()