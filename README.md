# 🛰️ NGSC V3.0 — Next-Generation Satellite Ground Control Station

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![ESP32](https://img.shields.io/badge/ESP32-IoT_Ready-E7352C?style=for-the-badge&logo=espressif&logoColor=white)

**A professional-grade, decoupled Ground Control Station (GCS) for tracking, commanding, and visualizing satellite telemetry.**

Built with Python, Streamlit, and FastAPI — supporting both software-simulated orbital dynamics and real-time Hardware-in-the-Loop (HIL) IoT integration.

</div>

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Mission Scenario](#-mission-scenario-a-day-in-the-life-of-a-ground-operator)
- [Key Features](#-key-features)
- [System Architecture](#️-system-architecture)
- [Data Flow](#-data-flow)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Running the System](#-running-the-system)
- [Hardware-in-the-Loop (HIL)](#️-hardware-in-the-loop-hil)
- [Future Roadmap](#-future-roadmap)
- [Author](#-author)

---

## 🌐 Overview

NGSC V3.0 bridges the gap between theoretical orbital mechanics and physical IoT hardware engineering. It provides mission operators with real-time satellite tracking, a 3D Digital Twin for attitude visualization, an autonomous command & control suite, and a persistent "Black Box" data vault — all running on a crash-proof, non-blocking architecture.

---

## 🎯 Mission Scenario: A Day in the Life of a Ground Operator

> **Role:** Mission Operator | **Ground Station:** Ahmedabad, India | **Target:** ISS (ZARYA) | **Mission Clock:** T-00:00

---

**① T-00:00 — Pre-Pass Setup**

The operator opens the NGSC dashboard. Before anything is visible on screen, the orbital engine has already pulled the latest TLE data for the ISS and run it through the SGP4 propagator — factoring in Earth's oblateness, atmospheric drag, and the ground station's exact coordinates.

The result appears instantly: *next Acquisition of Signal (AOS) in 4 minutes, 22 seconds. Maximum elevation: 67°. Loss of Signal (LOS) in 9 minutes.* The satellite's predicted ground track plots across the 2D map. There are nine minutes of contact. The clock starts.

---

**② T+04:22 — Signal Acquisition**

The ISS crests the horizon. Azimuth 312°, Elevation 2° and climbing. The moment contact begins, the Doppler module activates — the ISS is closing at 7.6 km/s, so the carrier frequency is currently shifted **+3.4 kHz** above nominal. NGSC calculates this automatically and logs it. A real radio operator would retune their hardware to match. Here, it's handled in the background without a single manual input.

---

**③ T+05:10 — Live Telemetry Floods In**

Ten packets per second arrive at the FastAPI backend. Each one carries the satellite's live orientation. The 3D cube on the dashboard responds immediately — rotating in real time as the numbers change. **Pitch: +12°. Roll: −4°.** The solar intensity sensor reads **680** — well above the deploy threshold of 400.

The autonomous sun-tracking logic fires without any operator input. The dashboard updates: *Solar Array → DEPLOYED.* On the HIL breadboard sitting on the desk, a relay physically clicks. Software state and physical hardware are now in sync.

---

**④ T+07:45 — Operator Sends an Uplink Command**

The operator clicks **"Payload ON"** in the command console. The UI posts the command to the FastAPI endpoint, which immediately transmits a UDP packet to the satellite on Port 4220. The system sends a heartbeat ping simultaneously to measure round-trip latency.

**340 milliseconds later** — the LED on the ESP32 lights up. Command acknowledged. The Black Box logs the event with a precise timestamp. The entire chain — button click → backend → UDP → hardware → confirmation — completed in under half a second.

---

**⑤ T+09:00 — Loss of Signal**

Elevation drops back to 2°. The ISS dips below the horizon. LOS confirmed. As the satellite passes out of range, the light sensor readings fall and the solar array automatically retracts — no command needed.

The session ends. **5,400 telemetry packets. Nine minutes of live attitude data. Every command sent and every response received** — all archived automatically in `/data/telemetry/hil_side/`, ready for post-pass analysis in the onboard Data Vault.

---

> *Total contact window: 9 minutes. Zero UI freezes. Zero dropped commands. One complete, timestamped mission log — ready for review.*

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| **Bidirectional Telemetry & C2** | Receive real-time orientation (Pitch/Roll) and sensor data while simultaneously sending uplink commands (payload control, solar array deployment, system ping) without blocking the UI |
| **Decoupled Architecture** | FastAPI backend acts as a data broker — ingests fast UDP packets from the satellite and serves state to Streamlit via HTTP, ensuring a smooth, crash-proof dashboard |
| **3D Digital Twin** | Real-time 3D visualization of the satellite's attitude using Plotly, driven by live Euler angle data |
| **Autonomous Subsystems** | Simulated day/night cycles with an "Auto-Sun" mode that automatically deploys and retracts solar panels based on sensed light thresholds using hysteresis logic |
| **Black Box Data Vault** | Automatically records every telemetry packet into mission-specific CSV logs, separated by mode (`mission_control/` for orbital sims, `hil_side/` for hardware testing) |
| **HIL Ready** | Designed to interface seamlessly with terrestrial IoT mock-ups (ESP32, MPU6050, LDR sensors) over local Wi-Fi via UDP |

---

## 🏗️ System Architecture

NGSC uses a **Three-Tier Decoupled Architecture**. This design allows the Ground Station to handle high-frequency telemetry streams without causing UI lag or blocking.

```
┌─────────────────────┐      UDP :4210      ┌─────────────────────┐      HTTP :8000     ┌─────────────────────┐
│                     │  ──────────────────► │                     │  ──────────────────► │                     │
│   SPACE SEGMENT     │                     │   GROUND BACKEND     │                     │   MISSION UI        │
│                     │                     │                     │                     │                     │
│  sim_satellite.py   │  ◄────────────────── │   FastAPI Broker    │  ◄────────────────── │  Streamlit Dashboard│
│  or ESP32 Hardware  │      UDP :4220       │   src/backend.py    │      HTTP POST       │  src/web_ui/app.py  │
└─────────────────────┘                     └─────────────────────┘                     └─────────────────────┘
        │                                           │
        │  Sensors, Attitude Physics,               │  UDP Ingestion, CSV Logging,
        │  Command Execution                        │  REST API State Management
        ▼                                           ▼
   Transmits at 10Hz                        Black Box Data Vault
```

### Architectural Layers

| Layer | Component | Protocol | Function |
|---|---|---|---|
| **Space Segment** | `sim_satellite.py` / ESP32 Hardware | UDP (Port 4210 / 4220) | Attitude physics, sensor data generation, command execution |
| **Ground Backend** | FastAPI Data Broker | HTTP / UDP | Central hub; logs all telemetry to CSV and manages Uplink/Downlink state |
| **User Interface** | Streamlit Dashboard | HTTP (Port 8501) | 3D visualizations, orbital ground tracks, command console |

---

## 🔄 Data Flow

**Downlink (Telemetry):**
```
Sensors → ESP32 → UDP Broadcast → FastAPI Backend → CSV Logger & HTTP State → Streamlit UI
```

**Uplink (Commanding):**
```
Streamlit UI (Button Click) → FastAPI Endpoint → UDP Transmit → ESP32 → Hardware Actuation
```

**Telemetry Packet Schema (JSON over UDP):**
```json
{
  "pitch": 12.5,
  "roll": -3.2,
  "yaw": 0.0,
  "light": 650,
  "status": {
    "led": "OFF",
    "solar": "DEPLOYED"
  }
}
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / UI** | Python, Streamlit, Plotly, Pandas |
| **Backend / Middleware** | Python, FastAPI, Uvicorn |
| **Communication** | UDP (telemetry), HTTP/REST (UI ↔ backend), Wi-Fi (hardware) |
| **Hardware (Space Segment)** | ESP32/NodeMCU, MPU6050 (IMU), LDR (Photoresistor), LEDs |
| **Scientific Libraries** | Skyfield/Ephem (orbital math), NumPy (matrix transformations) |

---

## 📂 Project Structure

```
ngsc_project/
│
├── data/
│   └── telemetry/
│       ├── hil_side/               # Hardware / Digital Twin logs
│       └── mission_control/        # Orbital simulation logs
│
├── src/
│   ├── web_ui/
│   │   ├── app.py                  # Main Streamlit Dashboard
│   │   └── hil_mode.py             # 3D Digital Twin & Command Console UI
│   │
│   ├── backend.py                  # FastAPI UDP-to-HTTP Broker & Logger
│   ├── data_manager.py             # CSV writing for Mission Control
│   ├── orbit_engine.py             # Orbital mechanics & tracking
│   ├── pass_predictor.py           # AOS/LOS window calculation
│   ├── radio_core.py               # Doppler shift simulation
│   └── decoder.py                  # Telemetry parsing
│
├── config/
│   └── satellites.json             # TLE data and frequency configurations
│
├── sim_satellite.py                # Python-based tumbling satellite simulator
├── requirements.txt                # Full pinned dependency manifest
└── README.md
```

---

## 🚀 Installation & Setup

### Prerequisites

- Python **3.8+**
- `pip` package manager

### Steps

**1. Clone the repository:**
```bash
git clone <your-repo-url>
cd ngsc_project
```

**2. Create and activate a virtual environment (recommended):**
```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

**3. Install all dependencies:**

First, make sure the `requirements.txt` is in your project root, then run:
```bash
pip install -r requirements.txt
```

This installs the full dependency stack:

| Category | Packages |
|---|---|
| **Orbit & Math** | `skyfield`, `numpy`, `sgp4` |
| **Radio & Signal** | `pyrtlsdr`, `scipy`, `construct` |
| **Frontend & Data** | `streamlit`, `pandas`, `plotly` |
| **Backend** | `fastapi`, `uvicorn` |
| **Utilities** | `pyserial`, `requests` |

> ⚠️ **Note on NumPy:** The project pins `numpy>=1.26.0,<2.0.0` intentionally. NumPy 2.0+ introduced breaking API changes that affect several dependencies. Do not manually upgrade NumPy beyond the `1.x` series.

---

## 🎮 Running the System

The system runs as **three concurrent microservices**. Open three separate terminals from the project root directory.

**Terminal 1 — Start the Satellite Simulator (Space Segment):**
```bash
python sim_satellite.py
```

**Terminal 2 — Start the Ground Backend (Broker & Logger):**
```bash
uvicorn src.backend:app --reload
```
> Backend API will be live at `http://127.0.0.1:8000`

**Terminal 3 — Launch the Mission Control Dashboard:**
```bash
streamlit run src/web_ui/app.py
```
> Dashboard will open at `http://localhost:8501`

---

## ⚙️ Hardware-in-the-Loop (HIL)

The next phase of NGSC replaces `sim_satellite.py` with a physical **Terrestrial Nano-Sat Emulator** running on an ESP32.

### Hardware Bill of Materials

| Component | Role | Interface |
|---|---|---|
| ESP32 / NodeMCU | Flight Computer | Wi-Fi / UDP |
| MPU6050 (IMU) | Attitude Sensor (Pitch/Roll) | I2C (GPIO 21/22) |
| LDR Photoresistor | Sun Sensor / Solar Intensity | Analog ADC (GPIO 34) |
| LED | Mission Payload | Digital GPIO (GPIO 2) |

### Wiring Summary

```
MPU6050  →  ESP32
  VCC    →  3.3V  (⚠️ NOT 5V)
  GND    →  GND
  SCL    →  GPIO 22
  SDA    →  GPIO 21

LDR Circuit (Voltage Divider)
  LDR leg 1   →  3.3V
  LDR leg 2   →  GPIO 34
  10kΩ Res    →  GPIO 34 → GND

LED Payload
  Anode (+)   →  220Ω Resistor → GPIO 2
  Cathode (−) →  GND
```

### Autonomous Solar Array Logic (Hysteresis)

To prevent mechanical flutter in fluctuating light conditions:

```
Deploy threshold  : Light ADC > 400  →  DEPLOY solar panels
Retract threshold : Light ADC < 300  →  RETRACT solar panels
```

> The deadband between 300–400 prevents rapid cycling.

---

## 🔭 Future Roadmap

- [ ] **RF Integration** — Replace Wi-Fi UDP with LoRa or NRF24L01 transceivers to simulate real radio constraints and packet loss
- [ ] **Battery Management System (BMS)** — Add Li-Po batteries with voltage divider circuits to transmit real hardware power drain data
- [ ] **Automated Ground Station Tracking** — Output Azimuth/Elevation data to servo motors to physically aim an antenna at passing satellites
- [ ] **Magnetometer Integration** — Add HMC5883L or MPU9250 for true 3-axis attitude including yaw
- [ ] **WebSocket Telemetry** — Replace Streamlit HTTP polling with WebSocket streaming for sub-100ms UI refresh rates

---

## 👨‍💻 Author

**Pratik Parihar**

> Built as part of the NGSC V3.0 — Ground Control Station & HIL Satellite Simulation Project.

---

<div align="center">
<i>If you found this project useful, consider giving it a ⭐ on GitHub!</i>
</div>
