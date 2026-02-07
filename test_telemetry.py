import socket

UDP_IP = "0.0.0.0" # Listen to ALL interfaces
UDP_PORT = 4210

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

print(f"📡 Listening for Satellite Data on Port {UDP_PORT}...")

while True:
    try:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        message = data.decode("utf-8")
        
        # Parse the CSV string
        parts = message.split(',')
        if parts[0] == "SAT1":
            print(f"✅ RECEIVED | Pitch: {parts[1]} | Roll: {parts[2]} | Light: {parts[3]} | AccelZ: {parts[4]}")
        else:
            print(f"⚠️ Unknown Packet: {message}")
            
    except KeyboardInterrupt:
        print("\nStopping Ground Station...")
        break
    except Exception as e:
        print(f"Error: {e}")