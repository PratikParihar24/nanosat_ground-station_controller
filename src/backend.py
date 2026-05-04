# src/backend.py
from fastapi import FastAPI
from pydantic import BaseModel
import serial # pip install pyserial
import json
import threading
import time
import csv
import os
from datetime import datetime

app = FastAPI()

# --- UMBILICAL CORD (SERIAL) CONFIGURATION ---
COM_PORT = os.environ.get("ARDUINO_COM_PORT", "COM7")  # <--- CHANGE THIS OR SET ENV VAR
BAUD_RATE = 115200

# --- SYSTEM CONFIGURATION ---
state_lock = threading.Lock()
serial_port = None
_shutdown_event = threading.Event()

# --- LOGGING SETUP ---
LOG_DIR = os.path.abspath("data/telemetry/hil_side")
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
current_log_file = os.path.join(LOG_DIR, f"hil_session_{timestamp}.csv")

# Open file once and keep it open for the session
_log_file = None
_log_writer = None

try:
    _log_file = open(current_log_file, 'w', newline='')
    _log_writer = csv.writer(_log_file)
    _log_writer.writerow(["timestamp", "pitch", "roll", "yaw", "light", "led_status", "solar_status", "mode"])
    _log_file.flush()
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

# Connect to the umbilical cord
try:
    serial_port = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
    print(f"[BACKEND] Hardline Umbilical Connected on {COM_PORT} at {BAUD_RATE} baud.")
except Exception as e:
    print(f"\n[CRITICAL ERROR] Could not open {COM_PORT}.")
    print("Is the Arduino IDE Serial Monitor open? IT MUST BE CLOSED!\n")

def serial_listener():
    global serial_port, _log_file, _log_writer
    if not serial_port: return
    
    while not _shutdown_event.is_set():
        try:
            if serial_port.in_waiting > 0:
                line = serial_port.readline().decode('utf-8').strip()
                
                # We filter for our specific telemetry packets
                if line.startswith("TELEM:"):
                    json_str = line.replace("TELEM:", "")
                    try:
                        packet = json.loads(json_str)
                    except json.JSONDecodeError as e:
                        print(f"[WARN] Malformed JSON packet: {e}")
                        continue
                    
                    with state_lock:
                        ground_state["last_packet_time"] = time.time()
                        ground_state["connected"] = True
                        ground_state["telemetry"]["pitch"] = packet.get("pitch", 0.0)
                        ground_state["telemetry"]["roll"] = packet.get("roll", 0.0)
                        ground_state["telemetry"]["light"] = packet.get("light", 0)
                        if "status" in packet:
                            ground_state["telemetry"]["status"] = packet["status"]
                    
                    # Log to CSV using persistent file handle
                    if _log_writer:
                        s = packet.get("status", {})
                        try:
                            _log_writer.writerow([
                                datetime.now().strftime("%H:%M:%S"), 
                                packet.get('pitch', 0), 
                                packet.get('roll', 0), 
                                packet.get('yaw', 0), 
                                packet.get('light', 0), 
                                s.get('led'), 
                                s.get('solar'), 
                                s.get('mode')
                            ])
                            _log_file.flush()  # Ensure data is written immediately
                        except Exception as e:
                            print(f"[ERROR] CSV write failed: {e}")
                        
        except UnicodeDecodeError as e:
            print(f"[WARN] Invalid bytes in serial buffer: {e}")
        except serial.SerialException as e:
            print(f"[ERROR] Serial connection lost: {e}")
            break
        except Exception as e:
            print(f"[ERROR] Serial listener: {e}")
    
    # Cleanup
    if _log_file:
        _log_file.close()
        _log_file = None
        _log_writer = None
    print("🛑 Serial listener stopped.")

# Start the listener in the background
threading.Thread(target=serial_listener, daemon=True).start()

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
        if serial_port and serial_port.is_open:
            # Send the command followed by a newline so the NodeMCU knows it's finished
            command_str = f"{cmd.action}\n"
            bytes_written = serial_port.write(command_str.encode('utf-8'))
            serial_port.flush()  # Ensure data is sent immediately
            
            if bytes_written != len(command_str):
                print(f"[WARN] Incomplete write: {bytes_written}/{len(command_str)} bytes")
                return {"status": "error", "message": "Incomplete write"}
            
            print(f"[HARDLINE FIRED] {cmd.action} over {COM_PORT}")
            return {"status": "success"}
        else:
            return {"status": "error", "message": "Umbilical disconnected."}
    except serial.SerialException as e:
        print(f"[COMMAND ERROR] Serial exception: {e}")
        return {"status": "error", "message": f"Serial error: {str(e)}"}
    except Exception as e:
        print(f"[COMMAND ERROR] {e}")
        return {"status": "error", "message": str(e)}


@app.on_event("shutdown")
def shutdown_event():
    """Graceful shutdown handler."""
    global serial_port, _shutdown_event
    print("[INFO] Shutting down...")
    _shutdown_event.set()
    
    if serial_port and serial_port.is_open:
        serial_port.close()
        print("[INFO] Serial port closed.")
    
    if _log_file:
        _log_file.close()
        print("[INFO] Log file closed.")