import socket
import time
import math
import random

# Configuration
UDP_IP = "127.0.0.1" # Localhost (Talk to yourself)
UDP_PORT = 4210

print(f"🛰️ STARTING VIRTUAL SATELLITE SIMULATION...")
print(f"📡 Target: {UDP_IP}:{UDP_PORT}")

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

t = 0
try:
    while True:
        # 1. Simulate Physics (Sine waves to make it rotate gently)
        pitch = 5.0 * math.sin(t)       # Tilts up and down
        roll = 10.0 * math.cos(t / 2)   # Rocks side to side
        accel_z = 9.8 + random.uniform(-0.1, 0.1) # Gravity + Noise
        
        # Simulate Solar/Eclipse (Light goes high then low)
        light = 1024 if (int(t) % 20) < 10 else 50 

        # 2. Format Packet (EXACTLY like the Arduino code)
        # Format: "SAT1, Pitch, Roll, Light, AccelZ"
        packet = f"SAT1,{pitch:.2f},{roll:.2f},{light},{accel_z:.2f}"

        # 3. Send Packet
        sock.sendto(packet.encode(), (UDP_IP, UDP_PORT))
        
        print(f"Tx: {packet}")
        
        t += 0.1
        time.sleep(0.1) # 10Hz Update Rate

except KeyboardInterrupt:
    print("\n🛑 Simulation Stopped.")