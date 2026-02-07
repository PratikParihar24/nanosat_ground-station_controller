# src/backend.py
from fastapi import FastAPI
from pydantic import BaseModel
import socket
import json
import threading
import time

app = FastAPI()

# --- CONFIGURATION ---
UDP_IP = "127.0.0.1"
UDP_RX_PORT = 4210  # Listen for Telemetry (From Satellite)
UDP_TX_PORT = 4220  # Send Commands (To Satellite)
BUFFER_SIZE = 1024

# --- STATE STORE (The "Truth") ---
# This dictionary lives in memory and holds the latest satellite data.
ground_state = {
    "connected": False,
    "last_packet_time": 0,
    "telemetry": {
        "pitch": 0.0,
        "roll": 0.0,
        "accel_z": 9.8,
        "light": 0,
        "status": {"led": "OFF", "solar": False}
    }
}

# --- BACKGROUND LISTENER ---
def udp_listener():
    """Constantly listens for UDP packets and updates ground_state."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_RX_PORT))
    print(f"[BACKEND] Listening for UDP on {UDP_RX_PORT}...")
    
    while True:
        try:
            data, _ = sock.recvfrom(BUFFER_SIZE)
            packet = json.loads(data.decode('utf-8'))
            
            # Update the State
            ground_state["last_packet_time"] = time.time()
            ground_state["connected"] = True
            
            # Update values if they exist in the packet
            ground_state["telemetry"]["pitch"] = packet.get("pitch", 0.0)
            ground_state["telemetry"]["roll"] = packet.get("roll", 0.0)
            ground_state["telemetry"]["accel_z"] = packet.get("accel_z", 9.8)
            ground_state["telemetry"]["light"] = packet.get("light", 0)
            
            if "status" in packet:
                ground_state["telemetry"]["status"] = packet["status"]
                
        except Exception as e:
            print(f"[ERROR] UDP Read Failed: {e}")

# Start the listener immediately in the background
threading.Thread(target=udp_listener, daemon=True).start()

# --- API ENDPOINTS (UI talks to these) ---

@app.get("/status")
def get_status():
    """The UI calls this to get the latest data."""
    # Check for timeout (2 seconds)
    if time.time() - ground_state["last_packet_time"] > 2.0:
        ground_state["connected"] = False
    return ground_state

class Command(BaseModel):
    action: str

@app.post("/command")
def send_command(cmd: Command):
    """The UI calls this to send a command."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(cmd.action.encode('utf-8'), (UDP_IP, UDP_TX_PORT))
        print(f"[COMMAND SENT] {cmd.action}")
        return {"status": "success", "sent": cmd.action}
    except Exception as e:
        return {"status": "error", "message": str(e)}