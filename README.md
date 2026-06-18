# 🛰️ NGSC V3.0 — Next-Generation Satellite Ground Control Station

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![NodeMCU](https://img.shields.io/badge/NodeMCU-ESP8266-E7352C?style=for-the-badge&logo=espressif&logoColor=white)

**A professional-grade, decoupled Ground Control Station (GCS) for tracking, commanding, and visualizing satellite telemetry.**

Built with Python, Streamlit, and FastAPI — supporting both software-simulated orbital dynamics and real-time Hardware-in-the-Loop (HIL) IoT integration via Serial USB.

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

NGSC V3.0 bridges the gap between theoretical orbital mechanics and physical IoT hardware engineering. It provides mission operators with real-time satellite tracking, a 3D Digital Twin for live attitude visualization, an autonomous command and control suite, and a persistent "Black Box" data vault — all running on a crash-proof, non-blocking architecture.

The HIL phase replaces the software simulator with a physical NodeMCU (ESP8266) connected via Serial USB, streaming real IMU data from an MPU6050 sensor directly to the dashboard at 10Hz.

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

Ten packets per second arrive at the FastAPI backend over the Serial bridge. Each one carries real IMU data from the physical MPU6050 sensor. The 3D cube on the dashboard responds immediately — rotating in real time as the board tilts. **Pitch: +12°. Roll: −4°.** The LDR solar sensor reads **680** — well above the deploy threshold of 600.

The autonomous sun-tracking logic fires without any operator input. The dashboard updates: *Solar Array → DEPLOYED.* Software state and physical sensor data are now in sync.

---

**④ T+07:45 — Operator Sends an Uplink Command**

The operator clicks **"Payload ON"** in the command console. The UI posts the command to the FastAPI endpoint, which writes it over the Serial connection to the NodeMCU. The Black Box logs the event with a precise timestamp.

The LED on the breadboard lights up. The entire chain — button click → backend → Serial → NodeMCU → physical hardware — completes in under half a second.

---

**⑤ T+09:00 — Loss of Signal**

Elevation drops back to 2°. The ISS dips below the horizon. LOS confirmed. As ambient light falls, the LDR reading drops and the solar array automatically retracts — no command needed.

The session ends. **5,400 telemetry packets. Nine minutes of live attitude data. Every command sent and every response received** — all archived automatically in `/data/telemetry/hil_side/`, ready for post-pass analysis in the onboard Data Vault.

---

> *Total contact window: 9 minutes. Zero UI freezes. Zero dropped commands. One complete, timestamped mission log — ready for review.*

---

## 🌟 Key Features

| Feature | Description |
|---|---|
| **Bidirectional Telemetry & C2** | Receive real-time orientation (Pitch/Roll) and sensor data at 10Hz while simultaneously sending uplink commands (payload control, solar array deployment) without blocking the UI |
| **Decoupled Architecture** | FastAPI backend acts as a data broker — ingests Serial telemetry from the NodeMCU and serves state to Streamlit via HTTP, ensuring a smooth, crash-proof dashboard |
| **3D Digital Twin** | Real-time 3D visualization of the satellite's attitude using Plotly, driven by live MPU6050 Euler angle data |
| **Autonomous Subsystems** | "Auto-Sun" mode automatically deploys and retracts solar panels based on live LDR readings using hysteresis logic to prevent mechanical flutter |
| **Black Box Data Vault** | Automatically records every telemetry packet into mission-specific CSV logs, separated by mode (`mission_control/` for orbital sims, `hil_side/` for hardware testing) |
| **HIL Ready** | Full Hardware-in-the-Loop integration with NodeMCU ESP8266, MPU6050 IMU, and LDR sensor over Serial USB |
| **Thread-Safe Pipeline** | All shared state between the Serial listener thread and HTTP handlers is protected with `threading.Lock()` — zero race conditions at 10Hz data rates |

---

## 🏗️ System Architecture

NGSC uses a **Three-Tier Decoupled Architecture**. The Serial bridge runs in a background thread, completely independent of the UI refresh cycle — the dashboard never blocks waiting for hardware data.

```
┌──────────────────────┐   Serial USB 115200   ┌──────────────────────┐   HTTP :8000   ┌──────────────────────┐
│                      │  ───────────────────► │                      │ ─────────────► │                      │
│   SPACE SEGMENT      │                       │   GROUND BACKEND     │                │   MISSION UI         │
│                      │                       │                      │ ◄───────────── │                      │
│  NodeMCU ESP8266     │ ◄───────────────────  │   FastAPI Broker     │   HTTP POST    │  Streamlit Dashboard │
│  MPU6050 + LDR + LED │   Serial Uplink       │   src/backend.py     │                │  src/web_ui/app.py   │
└──────────────────────┘                       └──────────────────────┘                └──────────────────────┘
         │                                               │
         │  Real IMU Data, LDR Readings,                 │  Serial Ingestion, CSV Logging,
         │  LED & Solar Command Execution                │  REST API State Management
         ▼                                               ▼
    Transmits at 10Hz                           Black Box Data Vault
```

### Architectural Layers

| Layer | Component | Protocol | Function |
|---|---|---|---|
| **Space Segment** | NodeMCU ESP8266 Hardware | Serial USB (115200 baud) | Real IMU attitude data, LDR solar sensing, LED command execution |
| **Ground Backend** | FastAPI + Serial Bridge | HTTP / Serial | Ingests telemetry, logs to CSV, manages shared state, serves REST API |
| **User Interface** | Streamlit Dashboard | HTTP (Port 8501) | 3D Digital Twin, orbital ground tracks, command console |

---

## 🔄 Data Flow

**Downlink (Telemetry) — Hardware → Dashboard:**
```
MPU6050 + LDR → NodeMCU → Serial USB → udp_bridge.py (background thread) → Shared State → FastAPI /status → Streamlit UI
```

**Uplink (Commanding) — Dashboard → Hardware:**
```
Streamlit UI (Button Click) → HTTP POST /command → FastAPI → Serial Write → NodeMCU → Physical Actuation
```

**Telemetry Packet Schema — JSON over Serial, prefixed and newline-terminated:**
```
TELEM:{"pitch": 12.5, "roll": -3.2, "light": 743, "status": {"led": "OFF", "solar": "DEPLOYED", "mode": "AUTO"}}
```

> The `TELEM:` prefix and `\n` newline terminator ensure Python's `readline()` always receives a complete, parseable packet — never a fragment. This prevents `JSONDecodeError` crashes in the listener thread.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend / UI** | Python, Streamlit, Plotly, Pandas |
| **Backend / Middleware** | Python, FastAPI, Uvicorn |
| **Communication** | Serial USB 115200 baud (HIL telemetry & commands), HTTP/REST (UI ↔ backend) |
| **Hardware (Space Segment)** | NodeMCU ESP8266 (ESP-12E), MPU6050 (IMU via I2C), LDR (Photoresistor), LED |
| **Scientific Libraries** | Skyfield / Ephem (orbital math), NumPy (matrix transformations) |
| **Arduino Libraries** | Adafruit MPU6050, Adafruit Unified Sensor, ArduinoJson 6.x, Wire.h |

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
│   ├── backend.py                  # FastAPI Serial-to-HTTP Broker & Logger
│   ├── udp_bridge.py               # Serial listener thread & shared state manager
│   ├── data_manager.py             # CSV writing for Mission Control
│   ├── orbit_engine.py             # Orbital mechanics & tracking
│   ├── pass_predictor.py           # AOS/LOS window calculation
│   ├── radio_core.py               # Doppler shift simulation
│   └── decoder.py                  # Telemetry parsing & input validation
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
- Arduino IDE **2.x** (for firmware upload only)

### Steps

**1. Clone the repository:**
```bash
git clone https://github.com/PratikParihar24/nanosat_ground-station_controller.git
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

### Software Simulation Mode

The system runs as **three concurrent microservices**. Open three separate terminals from the project root directory.

**Terminal 1 — Start the Satellite Simulator:**
```bash
python sim_satellite.py
```

**Terminal 2 — Start the Ground Backend:**
```bash
uvicorn src.backend:app --reload
```
> Backend API live at `http://127.0.0.1:8000`

**Terminal 3 — Launch the Mission Control Dashboard:**
```bash
streamlit run src/web_ui/app.py
```
> Dashboard opens at `http://localhost:8501`

### HIL Hardware Mode

Replace Terminal 1 with the physical NodeMCU. Upload the firmware via Arduino IDE, **close the Serial Monitor**, then start the backend and dashboard as above. The backend will automatically detect the NodeMCU on the configured COM port.

---

## ⚙️ Hardware-in-the-Loop (HIL)

The HIL phase replaces `sim_satellite.py` with a physical **Terrestrial Nano-Sat Emulator** — a NodeMCU ESP8266 on a breadboard, connected to the laptop via Serial USB.

> ⚠️ **Port Hand-off Protocol:** Windows treats COM ports as exclusive resources. **Always close the Arduino IDE Serial Monitor before starting the Python backend.** Running both simultaneously causes `Access Denied` errors.

---

### Finding Your COM Port

Open **Device Manager → Ports (COM & LPT)**. The NodeMCU will appear as:
```
USB-Serial CH340 (COMX)   or   Silicon Labs CP210x (COMX)
```
Update the `COM_PORT` variable in `src/backend.py` with the correct port number. Check this every time the NodeMCU is plugged into a different USB port.

---

### Hardware Bill of Materials

| Component | Role | Interface |
|---|---|---|
| NodeMCU ESP8266 (ESP-12E) | Flight Computer | Serial USB → Laptop |
| MPU6050 (IMU) | Attitude Sensor — Pitch & Roll | I2C via D2 (SDA) and D1 (SCL) |
| LDR Photoresistor | Sun Sensor / Solar Intensity | Analog ADC — A0 (only analog pin) |
| 10kΩ Resistor | Voltage divider pull-down for LDR | — |
| 220Ω Resistor | Current limiter for LED | — |
| LED | Mission Payload | Digital GPIO — D5 |

---

### Wiring Summary

```
MPU6050  →  NodeMCU
  VCC    →  3.3V  (⚠️ NOT 5V — will damage the sensor)
  GND    →  GND
  SCL    →  D1
  SDA    →  D2

⚠️  Use Female-to-Male jumper wires directly onto the MPU6050 SDA/SCL pins.
    Do NOT route I2C lines through the breadboard — clips lose tension
    and create air gaps that corrupt high-speed I2C signals.

LDR Circuit (Voltage Divider)
  LDR leg 1   →  3.3V
  LDR leg 2   →  A0  (range: 0–1023 on NodeMCU ESP8266)
  10kΩ Res    →  A0 → GND

LED Payload
  Anode  (+)  →  220Ω Resistor → D5
  Cathode (−) →  GND
```

---

### Autonomous Solar Array Logic (Hysteresis)

Thresholds are calibrated for the NodeMCU's **0–1023 ADC range**. Values were determined empirically — bright desk light reads 920–950, full shadow reads 150–200.

```
Deploy threshold  : Light ADC > 600  →  DEPLOY solar panels
Retract threshold : Light ADC < 400  →  RETRACT solar panels
```

> The 200-point deadband between 400–600 prevents rapid flutter in fluctuating ambient light.

---

### Arduino IDE Setup

**1. Add ESP8266 board support** — go to `File → Preferences` and add to "Additional Boards Manager URLs":
```
http://arduino.esp8266.com/stable/package_esp8266com_index.json
```
Then `Tools → Board → Boards Manager` → search "esp8266" → install **ESP8266 by ESP8266 Community (3.x)**.

**2. Select board:** `Tools → Board → ESP8266 Boards → NodeMCU 1.0 (ESP-12E Module)`

**3. Install libraries** via `Tools → Manage Libraries`:
- `Adafruit MPU6050`
- `Adafruit Unified Sensor`
- `ArduinoJson` by Benoit Blanchon — **version 6.x**

**4. Upload firmware, then immediately close Serial Monitor before starting the Python backend.**

---

### Known Hardware Constraints

| Constraint | Detail |
|---|---|
| **Yaw is always 0.0** | The MPU6050 accelerometer cannot detect yaw — gravity has no horizontal component to measure rotation around the vertical axis. True yaw requires a magnetometer (see Roadmap). |
| **ADC range 0–1023** | The NodeMCU has one analog pin (A0) with a 1V max input mapped to 0–1023. This differs from the ESP32's 0–4095 range — do not use ESP32-calibrated thresholds. |
| **I2C bus lockup** | If the MPU6050 loses power mid-transmission, the I2C bus can freeze with SDA stuck HIGH. A 10-second cold boot (full USB removal) is required to recover. |
| **Staggered boot required** | The MPU6050 must initialise before the LED pin is configured. Simultaneous initialisation causes a voltage inrush that crashes the sensor on startup. |

---

## 🔭 Future Roadmap

- [ ] **RF Integration** — Replace Serial USB with LoRa or NRF24L01 transceivers to simulate true radio constraints and packet loss
- [ ] **Battery Management System (BMS)** — Add Li-Po batteries with voltage divider circuits to transmit real hardware power drain data
- [ ] **Automated Ground Station Tracking** — Output Azimuth/Elevation data to servo motors to physically aim an antenna at passing satellites
- [ ] **Magnetometer Integration** — Add HMC5883L or upgrade to MPU9250 for true 3-axis attitude including yaw
- [ ] **WebSocket Telemetry** — Replace Streamlit HTTP polling with WebSocket streaming for sub-100ms UI refresh rates

---

## 👨‍💻 Author

**Pratik Parihar**

> Built as part of the NGSC V3.0 — Ground Control Station & HIL Satellite Simulation Project.

---

<div align="center">
<i>If you found this project useful, consider giving it a ⭐ on GitHub!</i>
</div>
