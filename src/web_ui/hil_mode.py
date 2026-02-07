# src/web_ui/hil_mode.py

import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
import requests 

# --- CONFIG ---
BACKEND_URL = "http://127.0.0.1:8000"

# --- CUSTOM CSS ---
def inject_hil_css():
    st.markdown("""
        <style>
        /* 1. Compact Metrics */
        div[data-testid="stMetric"] {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        /* 2. Fix Top Padding */
        div.block-container {
            padding-top: 1.5rem !important;
        }

        /* 3. Uniform Button Height */
        div.stButton > button {
            width: 100%;
            border-radius: 6px;
            height: 3.2em;
            font-weight: 600;
        }

        /* 4. Vertical Alignment Helper for Status Text */
        .status-text {
            padding-top: 12px; /* Pushes text down to align with Toggle */
            font-size: 0.9em;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

# --- API HELPERS ---
def get_backend_data():
    try:
        response = requests.get(f"{BACKEND_URL}/status", timeout=0.2)
        if response.status_code == 200: return response.json()
    except: return None

def send_command(action):
    try:
        requests.post(f"{BACKEND_URL}/command", json={"action": action}, timeout=0.2)
        return True
    except: return False

# --- 3D VISUALIZATION ---
def create_3d_sat_fig(pitch, roll):
    vertices = np.array([[-1,-1,-1],[1,-1,-1],[1,1,-1],[-1,1,-1],[-1,-1,1],[1,-1,1],[1,1,1],[-1,1,1]]) * 0.5 
    p, r = np.radians(pitch), np.radians(roll)
    Rx = np.array([[1,0,0],[0,np.cos(p),-np.sin(p)],[0,np.sin(p),np.cos(p)]])
    Ry = np.array([[np.cos(r),0,np.sin(r)],[0,1,0],[-np.sin(r),0,np.cos(r)]])
    rv = vertices @ Ry @ Rx
    x,y,z = rv[:,0], rv[:,1], rv[:,2]
    
    fig = go.Figure(data=[go.Mesh3d(x=x, y=y, z=z, color='#00FFFF', opacity=0.9, flatshading=True, i=[7,0,0,0,4,4,6,6,4,0,3,2], j=[3,4,1,2,5,6,5,2,0,1,6,3], k=[0,7,2,3,6,7,1,1,5,5,7,6])])
    
    fig.update_layout(
        scene=dict(
            xaxis=dict(visible=False, range=[-1,1]), 
            yaxis=dict(visible=False, range=[-1,1]), 
            zaxis=dict(visible=False, range=[-1,1]), 
            bgcolor='rgba(0,0,0,0)', 
            aspectmode='cube'
        ), 
        margin=dict(l=0,r=0,b=0,t=0), 
        height=380, 
        paper_bgcolor='rgba(0,0,0,0)', 
        autosize=True
    )
    return fig

# --- MAIN HIL FUNCTION ---
def run_hil_telemetry():
    inject_hil_css()
    
    # 1. FETCH DATA
    data = get_backend_data()
    if not data:
        st.error("⚠️ BACKEND OFFLINE - Run 'uvicorn src.backend:app --reload'")
        if st.button("Retry"): st.rerun()
        return

    # Parse
    telemetry = data["telemetry"]
    status = telemetry.get("status", {})
    led_state = status.get("led", "OFF")
    solar_raw = status.get("solar", "RETRACTED")
    solar_mode = status.get("mode", "MANUAL")
    
    if solar_raw == True: solar_status = "DEPLOYED"
    elif solar_raw == False: solar_status = "RETRACTED"
    else: solar_status = solar_raw

    pitch = telemetry.get("pitch", 0.0)
    roll = telemetry.get("roll", 0.0)

    # 2. HEADER ROW (Refined Alignment)
    # [5, 2, 1.5] ratio pushes the Ping button closer to the text
    c_title, c_status, c_ping = st.columns([5, 2, 1.5])
    
    with c_title:
        st.markdown("<h2 style='margin:0; padding:0;'>🛰️ HIL DIGITAL TWIN</h2>", unsafe_allow_html=True)
    
    with c_status:
        # Using markdown with a div ensures the text block aligns better vertically
        st.markdown(
            f"""
            <div style="text-align: right; padding-top: 5px;">
                <span style="font-size: 0.8em; color: #888;">{BACKEND_URL}</span><br>
                <b>STATUS: <span style="color: #00FF00;">ONLINE</span></b>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    with c_ping:
        st.write("")
        if st.button("📡 PING", help="Test Uplink Latency"):
            send_command("PING")
            st.toast("Ping Sent! Check Terminal.")

    st.markdown("---")

    # 3. METRICS ROW
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Telemetry Link", "ACTIVE", delta_color="normal")
    m2.metric("Pitch", f"{pitch:.2f}°")
    m3.metric("Roll", f"{roll:.2f}°")
    
    if solar_status == "DEPLOYED":
        m4.metric("Power", "Generating", "Solar")
    else:
        m4.metric("Power", "Draining", "Battery", delta_color="inverse")

    st.write("") 

    # 4. MAIN DASHBOARD
    col_vis, col_ctrl = st.columns([1.5, 1])
    
    # --- LEFT: 3D VIEW ---
    with col_vis:
        st.plotly_chart(create_3d_sat_fig(pitch, roll))

    # --- RIGHT: CONTROL PANEL ---
    with col_ctrl:
        
        # --- PAYLOAD SECTION (Perfectly Aligned) ---
        with st.container(border=True):
            st.caption("📦 PAYLOAD SYSTEMS")
            
            pl_c1, pl_c2 = st.columns([1, 1.5])
            
            with pl_c1:
                is_led_on = (led_state == "ON")
                # The Toggle Switch
                new_led = st.toggle("LED Power", value=is_led_on)
                if new_led != is_led_on:
                    send_command("LED_ON" if new_led else "LED_OFF")
                    st.rerun()
            
            with pl_c2:
                # The Status Text (Using CSS class for alignment)
                if is_led_on:
                    st.markdown('<div class="status-text">State: <b style="color:#00FF00">ACTIVE</b></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="status-text">State: <b style="color:#666">OFFLINE</b></div>', unsafe_allow_html=True)

        st.write("") 

        # --- SOLAR SECTION (Grid Layout) ---
        with st.container(border=True):
            st.caption("☀️ SOLAR ARRAY")
            
            # Status Badge
            if solar_mode == "AUTO":
                st.info(f"🤖 AUTO MODE | {solar_status}")
            else:
                if solar_status == "DEPLOYED":
                    st.success(f"✋ MANUAL | {solar_status}")
                else:
                    st.warning(f"✋ MANUAL | {solar_status}")

            st.write("") # tiny spacer
            
            # 3-Column Grid for perfect button alignment
            b1, b2, b3 = st.columns(3)
            
            with b1:
                if st.button("🚀 OPEN"):
                    send_command("DEPLOY_SOLAR")
                    st.rerun()
            with b2:
                if st.button("🔒 CLOSE"):
                    send_command("RETRACT_SOLAR")
                    st.rerun()
            with b3:
                # Secondary style for the "Mode" button to distinguish it
                if st.button("🤖 AUTO", type="secondary"):
                    send_command("AUTO_SOLAR")
                    st.rerun()

    # Auto-Refresh
    time.sleep(0.5)
    st.rerun()