# sim_satellite.py

import socket
import json
import time
import math
import threading
import random

# --- CONFIGURATION ---
TELEM_IP = "127.0.0.1"
TELEM_PORT = 4210       
COMMAND_PORT = 4220     

# --- SATELLITE STATE ---
state = {
    "pitch": 0.0,
    "roll": 0.0,
    "yaw": 0.0,
    "accel_z": 9.81,
    "light": 0,
    "status": {
        "led": "OFF",
        "solar": "RETRACTED",
        "mode": "MANUAL"
    }
}

def command_listener():
    """Background thread to listen for commands."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("127.0.0.1", COMMAND_PORT))
    print(f"[SAT] Listening for commands on port {COMMAND_PORT}...")
    
    while True:
        try:
            data, _ = sock.recvfrom(1024)
            command = data.decode('utf-8').strip()
            print(f"[SAT] CMD: {command}")
            
            if command == "LED_ON":
                state["status"]["led"] = "ON"
            elif command == "LED_OFF":
                state["status"]["led"] = "OFF"
            elif command == "DEPLOY_SOLAR":
                state["status"]["solar"] = "DEPLOYED"
                state["status"]["mode"] = "MANUAL"
            elif command == "RETRACT_SOLAR":
                state["status"]["solar"] = "RETRACTED"
                state["status"]["mode"] = "MANUAL"
            elif command == "AUTO_SOLAR":
                state["status"]["mode"] = "AUTO"
            elif command == "PING":
                print("[SAT] PONG!")
                
        except Exception as e:
            print(f"[SAT] Error: {e}")

def run_simulation():
    print(f"[SAT] Simulator Started. Target: {TELEM_IP}:{TELEM_PORT}")
    threading.Thread(target=command_listener, daemon=True).start()
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    t = 0
    
    while True:
        # 1. Physics
        state["pitch"] = 10 * math.sin(t * 0.5)
        state["roll"] = 45 * math.cos(t * 0.2)
        
        # 2. Solar Logic (FIXED: 10x Slower Day/Night Cycle)
        # 0.05 means a full cycle takes about 2 minutes instead of 12 seconds
        sun_intensity = 500 + 500 * math.sin(t * 0.05)
        
        # AUTOMATIC MODE
        if state["status"]["mode"] == "AUTO":
            # Hysteresis: Deploy at >400, Retract at <300 to prevent flickering
            if sun_intensity > 400:
                state["status"]["solar"] = "DEPLOYED"
            elif sun_intensity < 300:
                state["status"]["solar"] = "RETRACTED"
        
        # Light Sensor Reading
        if state["status"]["solar"] == "DEPLOYED":
            state["light"] = max(0, sun_intensity + 200)
        else:
            state["light"] = max(0, sun_intensity * 0.5)

        # 3. Send Data
        try:
            packet = json.dumps(state)
            sock.sendto(packet.encode('utf-8'), (TELEM_IP, TELEM_PORT))
        except: pass
            
        time.sleep(0.1)
        t += 0.1

if __name__ == "__main__":
    run_simulation()