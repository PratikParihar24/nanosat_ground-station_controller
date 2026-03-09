
A professional-grade, decoupled Ground Control Station (GCS) for tracking, commanding, and visualizing satellite telemetry. Built with Python, Streamlit, and FastAPI, this system supports both software-simulated orbital dynamics and real-time Hardware-in-the-Loop (HIL) IoT integration.

## 🌟 Key Features

* **Bidirectional Telemetry & Command:** Receive real-time orientation (Pitch/Roll/Yaw) and sensor data while simultaneously sending commands (Payload control, Solar Array deployment, System Ping) without blocking the UI.
* **Decoupled Architecture:** Utilizes a FastAPI backend acting as a data broker. It ingests fast UDP packets from the satellite and serves state to the Streamlit UI via HTTP, ensuring a smooth, crash-proof dashboard.
* **3D Digital Twin:** Real-time 3D visualization of the satellite's attitude using Plotly.
* **Autonomous Subsystems:** Features simulated day/night cycles with an "Auto-Sun" mode that automatically deploys and retracts solar panels based on light intensity.
* **The "Black Box" Data Vault:** Automatically records all telemetry and mission data into separated CSV logs (`mission_control/` for software tracking, `hil_side/` for hardware testing). Includes an in-app data analyzer and file manager.
* **Hardware-in-the-Loop (HIL) Ready:** Designed to interface seamlessly with terrestrial IoT mock-ups (ESP32/NodeMCU, MPU6050, LDR sensors) over local Wi-Fi.

## 🏗️ System Architecture

The project is split into three main microservices running concurrently:

1.  **The Satellite (UDP Client):** `sim_satellite.py` (or physical ESP32 hardware). Transmits telemetry at 10Hz to Port 4210 and listens for commands on Port 4220.
2.  **The Ground Backend (FastAPI):** `src/backend.py`. Listens to the UDP stream, logs data to the CSV Black Box, and hosts a REST API at `http://127.0.0.1:8000`.
3.  **The Mission UI (Streamlit):** `src/web_ui/app.py`. Fetches the state from the backend API, renders the 3D twin, and posts user commands back to the API.

## 🚀 Installation & Setup

**Prerequisites:** Python 3.8+

1. **Clone the repository and navigate to the project directory:**
   ```bash
   git clone <your-repo-url>
   cd ngsc_project

 * Create a virtual environment (recommended):
   python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

 * Install dependencies:
   pip install streamlit fastapi uvicorn pandas plotly requests numpy

🎮 Running the Simulation
To launch the full system, open three separate terminals and run the following commands from the root directory:
Terminal 1: Start the Satellite Simulator
python sim_satellite.py

Terminal 2: Start the Ground Backend (Broker & Logger)
uvicorn src.backend:app --reload

Terminal 3: Launch the Mission Control Dashboard
streamlit run src/web_ui/app.py

📂 Project Structure
ngsc_project/
├── data/
│   └── telemetry/
│       ├── hil_side/          # Hardware/Sim Digital Twin logs
│       └── mission_control/   # Orbital simulation logs
├── src/
│   ├── web_ui/
│   │   ├── app.py             # Main Streamlit Dashboard
│   │   └── hil_mode.py        # 3D Digital Twin & Command Console UI
│   ├── backend.py             # FastAPI UDP-to-HTTP Broker & Logger
│   ├── data_manager.py        # Handles CSV writing for Mission Control
│   ├── orbit_engine.py        # Orbital mechanics & tracking
│   ├── pass_predictor.py      # Calculates AOS/LOS times
│   ├── radio_core.py          # Doppler shift simulation
│   └── decoder.py             # Telemetry parsing
├── sim_satellite.py           # Python-based tumbling satellite sim
├── config/
│   └── satellites.json        # TLE data and frequency configurations
└── README.md

🛠️ Future Roadmap (IoT Integration)
The next phase of NGSC is replacing sim_satellite.py with a physical Terrestrial Nano-Sat Emulator.
 * Microcontroller: NodeMCU (ESP8266) / ESP32
 * Sensors: MPU6050 (Attitude/Gyro), LDR (Solar intensity simulation)
 * Payload: Addressable LEDs
👨‍💻 Author
Pratik Parihar

***


