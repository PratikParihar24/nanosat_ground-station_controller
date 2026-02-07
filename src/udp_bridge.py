import socket
import threading
import time

# --- Configuration ---
UDP_IP = "0.0.0.0"
UDP_PORT = 4210
BUFFER_SIZE = 1024

# --- Shared Memory (The "Latest" Data) ---
# This dictionary holds the most recent packet received.
# Streamlit will read from here.
current_telemetry = {
    "connected": False,
    "last_packet_time": 0,
    "pitch": 0.0,
    "roll": 0.0,
    "yaw": 0.0,      # Calculated or dummy
    "accel_z": 9.8,  # Gravity
    "light": 0       # Solar sensor
}

# Flag to ensure we only start the listener ONCE
_listener_running = False

def _udp_listener_loop():
    """
    Background thread that sits in a loop waiting for UDP packets.
    It updates the 'current_telemetry' dictionary instantly.
    """
    global current_telemetry
    
    # 1. Setup Socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.settimeout(1.0) # Check for stop signal every second
    
    print(f"✅ UDP Listener started on port {UDP_PORT}")
    
    while True:
        try:
            # 2. Wait for Data (Blocking, but safe inside a thread)
            data, addr = sock.recvfrom(BUFFER_SIZE)
            message = data.decode("utf-8").strip()
            
            # 3. Parse Packet: "SAT1,pitch,roll,light,accel_z"
            parts = message.split(',')
            
            if len(parts) >= 5 and parts[0] == "SAT1":
                # Update Shared Memory
                current_telemetry["pitch"] = float(parts[1])
                current_telemetry["roll"] = float(parts[2])
                current_telemetry["light"] = int(parts[3])
                current_telemetry["accel_z"] = float(parts[4])
                
                # Update Status
                current_telemetry["last_packet_time"] = time.time()
                current_telemetry["connected"] = True
                
        except socket.timeout:
            # No data received in last second
            pass
        except Exception as e:
            print(f"⚠️ UDP Error: {e}")

def start_listener():
    """
    Call this ONCE from your main app.py to start the background ear.
    """
    global _listener_running
    if not _listener_running:
        t = threading.Thread(target=_udp_listener_loop, daemon=True)
        t.start()
        _listener_running = True

def get_latest_data():
    """
    Streamlit calls this function to get the current state.
    It also handles the 'Signal Lost' logic.
    """
    global current_telemetry
    
    # Check for Timeout (Signal Lost > 3 seconds)
    if time.time() - current_telemetry["last_packet_time"] > 3.0:
        current_telemetry["connected"] = False
        
    return current_telemetry