import time
from src.udp_bridge import start_listener, get_latest_data

# 1. Start the Background Thread
start_listener()

# 2. Read Data Loop
while True:
    data = get_latest_data()

    status = "🟢 ONLINE" if data['connected'] else "🔴 SIGNAL LOST"
    print(f"[{status}] Pitch: {data['pitch']:.2f} | Roll: {data['roll']:.2f}")

    time.sleep(0.5)
    