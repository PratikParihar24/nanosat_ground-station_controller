# src/backend.py
from fastapi import FastAPI
from pydantic import BaseModel
import socket
import json
import threading
import time
import csv
import os
from datetime import datetime

app = FastAPI()

# --- CONFIGURATION ---
UDP_IP = "127.0.0.1"
UDP_RX_PORT = 4210
UDP_TX_PORT = 4220
BUFFER_SIZE = 1024

# --- THREAD SAFETY ---
state_lock = threading.Lock()

# --- LOGGING SETUP ---
LOG_DIR = os.path.abspath("data/telemetry/hil_side")
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
current_log_file = os.path.join(LOG_DIR, f"hil_session_{timestamp}.csv")

try:
    with open(current_log_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "pitch", "roll", "yaw", "light", "led_status", "solar_status", "mode"])
except Exception as e:
    print(f"[RECORDER] Error: {e}")

# --- STATE STORE ---
ground_state = {
    "connected": False,
    "last_packet_time": 0,
    "telemetry": {
        "pitch": 0.0,
        "roll": 0.0,
        "accel_z": 9.8,
        "light": 0,
        "status": {"led": "OFF", "solar": "RETRACTED", "mode": "MANUAL"}
    }
}

def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_RX_PORT))
    print(f"[BACKEND] Listening on {UDP_RX_PORT}...")
    
    while True:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            # CRITICAL FIX: Safe JSON Parsing
            packet = json.loads(data.decode('utf-8'))
            
            with state_lock:
                ground_state["last_packet_time"] = time.time()
                ground_state["connected"] = True
                ground_state["telemetry"]["pitch"] = packet.get("pitch", 0.0)
                ground_state["telemetry"]["roll"] = packet.get("roll", 0.0)
                ground_state["telemetry"]["light"] = packet.get("light", 0)
                if "status" in packet:
                    ground_state["telemetry"]["status"] = packet["status"]
            
            # Log to CSV
            with open(current_log_file, 'a', newline='') as f:
                writer = csv.writer(f)
                s = packet.get("status", {})
                writer.writerow([datetime.now().strftime("%H:%M:%S"), packet.get('pitch', 0), 
                                 packet.get('roll', 0), packet.get('yaw', 0), packet.get('light', 0), 
                                 s.get('led'), s.get('solar'), s.get('mode')])
                
        except Exception as e:
            print(f"[ERROR] Listener: {e}")

threading.Thread(target=udp_listener, daemon=True).start()

@app.get("/status")
def get_status():
    with state_lock:
        if time.time() - ground_state["last_packet_time"] > 2.0:
            ground_state["connected"] = False
        return ground_state

class Command(BaseModel):
    action: str

@app.post("/command")
def send_command(cmd: Command):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(cmd.action.encode('utf-8'), (UDP_IP, UDP_TX_PORT))
        print(f"[COMMAND SENT] {cmd.action}")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "message": str(e)}