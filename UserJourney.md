# 🛰️ NGSC V3.0 — The Complete Project Handbook

> **What is this document?**
> This is the single source of truth for understanding every screen, action, data flow, and technical decision in the Next-Generation Satellite Ground Control Station. Whether you're onboarding, debugging, or presenting this project — start here.

---

## Table of Contents

1. [Project Overview — The 30-Second Pitch](#1-project-overview--the-30-second-pitch)
2. [System Architecture — The Big Picture](#2-system-architecture--the-big-picture)
3. [How to Launch the System — Step by Step](#3-how-to-launch-the-system--step-by-step)
4. [Entry Point & Initialization Deep Dive](#4-entry-point--initialization-deep-dive)
5. [The Four Dashboard Modules — Full User Journey](#5-the-four-dashboard-modules--full-user-journey)
   - [5.1 Mission Control](#51-mission-control)
   - [5.2 Pass Predictor](#52-pass-predictor)
   - [5.3 Data Vault](#53-data-vault)
   - [5.4 HIL Telemetry (Digital Twin)](#54-hil-telemetry-digital-twin)
6. [The Complete Data Journey — Byte by Byte](#6-the-complete-data-journey--byte-by-byte)
   - [6.1 Downlink: Hardware → Dashboard](#61-downlink-hardware--dashboard)
   - [6.2 Uplink: Dashboard → Hardware](#62-uplink-dashboard--hardware)
   - [6.3 Simulation Mode Data Flow](#63-simulation-mode-data-flow)
7. [Module-by-Module Technical Reference](#7-module-by-module-technical-reference)
   - [7.1 `backend.py` — The FastAPI Broker](#71-backendpy--the-fastapi-broker)
   - [7.2 `udp_bridge.py` — The UDP Listener](#72-udp_bridgepy--the-udp-listener)
   - [7.3 `orbit_engine.py` — Orbital Mechanics](#73-orbit_enginepy--orbital-mechanics)
   - [7.4 `pass_predictor.py` — AOS/LOS Calculator](#74-pass_predictorpy--aoslos-calculator)
   - [7.5 `radio_core.py` — SDR & Doppler](#75-radio_corepy--sdr--doppler)
   - [7.6 `decoder.py` — Binary Telemetry Parser](#76-decoderpy--binary-telemetry-parser)
   - [7.7 `data_manager.py` — CSV Black Box](#77-data_managerpy--csv-black-box)
   - [7.8 `app.py` — The Streamlit Dashboard](#78-apppy--the-streamlit-dashboard)
   - [7.9 `hil_mode.py` — 3D Digital Twin UI](#79-hil_modepy--3d-digital-twin-ui)
   - [7.10 `sim_satellite.py` — Software Simulator](#710-sim_satellitepy--software-simulator)
   - [7.11 Arduino Firmware (`.ino` files)](#711-arduino-firmware-ino-files)
8. [Configuration Files Reference](#8-configuration-files-reference)
9. [State Management & Thread Safety](#9-state-management--thread-safety)
10. [Error Handling & Fault Tolerance](#10-error-handling--fault-tolerance)
11. [Complete File Map](#11-complete-file-map)

---

## 1. Project Overview — The 30-Second Pitch

**NGSC V3.0** (Next-Generation Satellite Ground Control Station) is a professional-grade ground control station that lets a mission operator:

- **Track real satellites** (ISS, NOAA 19, custom CubeSats) using orbital mechanics and TLE data
- **Visualize a 3D Digital Twin** that rotates in real-time based on physical IMU sensor data
- **Send commands** to hardware (turn on LEDs, deploy solar panels) through a button click
- **Record every telemetry packet** into a timestamped "Black Box" for post-mission analysis

**In plain English:** You open a web dashboard. It shows you where a satellite is in the sky, lets you talk to a physical microcontroller on your desk (pretending to be a satellite), and records everything that happens.

**The key insight:** The system bridges _theoretical orbital mechanics_ (predicting where the ISS is) with _physical IoT hardware_ (an ESP8266 with sensors on a breadboard). It's a full ground station, just scaled to a desk.

---

## 2. System Architecture — The Big Picture

The system uses a **Three-Tier Decoupled Architecture** — three independent processes that communicate over standard protocols:

```
┌─────────────────────────┐   Serial USB 115200    ┌─────────────────────────┐   HTTP :8000    ┌─────────────────────────┐
│     SPACE SEGMENT       │  ────────────────────►  │     GROUND BACKEND      │  ────────────►  │     MISSION UI          │
│                         │                         │                         │                 │                         │
│  NodeMCU ESP8266        │  ◄────────────────────  │   FastAPI Broker         │  ◄────────────  │  Streamlit Dashboard    │
│  MPU6050 + LDR + LED    │   Serial Uplink         │   src/backend.py        │   HTTP POST     │  src/web_ui/app.py      │
└─────────────────────────┘                         └─────────────────────────┘                 └─────────────────────────┘
       │                                                     │                                           │
       │ Transmits at 10Hz                                   │ CSV Logging                               │ Renders at 2Hz
       │ Real IMU + LDR data                                 │ REST API State                            │ Plotly 3D / Maps
       ▼                                                     ▼                                           ▼
  Physical Sensors                                  data/telemetry/hil_side/                     Browser (localhost:8501)
```

### Why Three Tiers?

| Problem | Solution |
|---------|----------|
| Serial I/O is blocking — if the UI waits for hardware, it freezes | The **backend** reads serial in a background thread; the UI just polls HTTP |
| Streamlit re-runs the entire script on every interaction | Expensive objects (OrbitEngine, RadioCore) are cached with `@st.cache_resource` |
| Hardware might disconnect mid-session | The backend has **exponential backoff reconnection** — it never crashes |

---

## 3. How to Launch the System — Step by Step

### Software Simulation Mode (No Hardware)

You need **three terminal windows** running simultaneously:

```
Terminal 1 — The Satellite Simulator (generates fake sensor data via UDP)
$ python sim_satellite.py
→ Sends JSON packets to UDP port 4210 at 10Hz

Terminal 2 — The Ground Backend (FastAPI API server)
$ uvicorn src.backend:app --reload
→ Starts at http://127.0.0.1:8000
→ Immediately spawns a background thread to read Serial (or generate synthetic data)

Terminal 3 — The Dashboard (Streamlit web app)
$ streamlit run src/web_ui/app.py
→ Opens at http://localhost:8501
→ Loads OrbitEngine, RadioCore, Decoder, PassPredictor on first run
```

### Hardware-in-the-Loop Mode (Real NodeMCU)

Replace Terminal 1 with the physical NodeMCU:
1. Upload `satellite_new.ino` via Arduino IDE
2. **Close the Arduino Serial Monitor** (Windows locks COM ports exclusively)
3. Set `COM_PORT` in `src/backend.py` to your actual port (e.g., `COM7`)
4. Run Terminal 2 and Terminal 3 as above

---

## 4. Entry Point & Initialization Deep Dive

### What happens when you run `streamlit run src/web_ui/app.py`?

Here is the exact initialization sequence, line by line:

```
Step 1: Path Setup (app.py:12-15)
├── Calculates project_root by going up two directories from app.py's location
└── Adds project_root to sys.path so `from src.xxx import` works

Step 2: Imports (app.py:18-23)
├── OrbitEngine    → Loads TLE data, creates Skyfield timescale
├── RadioCore      → Initializes SDR (or mock mode)
├── TelemetryDecoder → Prepares binary packet parser
├── DataManager    → CSV writer factory
├── PassPredictor  → Satellite pass calculator
└── hil_mode       → HIL Digital Twin UI components

Step 3: Page Config (app.py:26-31)
├── Sets page title to "NGSC Mission Control"
├── Sets layout to "wide" (full browser width)
└── Sidebar starts expanded

Step 4: System Initialization via @st.cache_resource (app.py:248-263)
│   get_system() runs ONCE, then is cached for the session lifetime:
│
├── 4a. Load satellites.json (config/satellites.json)
│   └── Parses satellite names, frequencies, and optional custom TLEs
│
├── 4b. Create OrbitEngine (orbit_engine.py:12-46)
│   ├── Load Skyfield timescale (downloads ~1MB ephemeris on first run)
│   ├── Read stations.conf → Ground station at 23.0225°N, 72.5714°E (Ahmedabad)
│   ├── Check if active_tles.txt exists and is < 24 hours old
│   │   ├── If stale → Download fresh TLEs from CelesTrak (with 3x retry)
│   │   └── If fresh → Use cached file
│   └── Parse all TLEs into Skyfield EarthSatellite objects
│
├── 4c. Create RadioCore(mock_mode=True) (radio_core.py:18-44)
│   └── In mock mode, no actual SDR hardware is accessed
│
├── 4d. Create TelemetryDecoder (decoder.py:26-29)
│   └── Initializes packet_count=0, error_count=0
│
└── 4e. Create PassPredictor(engine.station) (pass_predictor.py:6-12)
    └── Stores the ground station Topos object and creates its own timescale

Step 5: Load CSS (app.py:267-269)
└── Looks for assets/style.css — injects custom dark theme if found

Step 6: Render Sidebar (app.py:271-295)
├── Title: "NGSC V3.0"
├── Radio selector: Mission Control | Pass Predictor | Data Vault | HIL Telemetry
├── Satellite dropdown: ISS (ZARYA) | GTUSAT-1 | NOAA 19
└── Resolves selected satellite → calls orbit_engine.get_satellite_by_name()
    └── Uses 3-tier matching: Direct → Whitespace-stripped → Fuzzy (substring)
```

### What happens when you run `uvicorn src.backend:app --reload`?

```
Step 1: Module-level execution (backend.py:1-60)
├── Create FastAPI app instance
├── Detect SIMULATION_MODE (checks RENDER env var or SIMULATION_MODE="True")
├── Configure COM_PORT (default: COM7) and BAUD_RATE (115200)
├── Create threading locks: state_lock, serial_io_lock
├── Create shutdown event
├── Create LOG_DIR: data/telemetry/hil_side/
├── Open CSV file: hil_session_YYYYMMDD_HHMMSS.csv
│   └── Write header: timestamp, pitch, roll, yaw, light, led_status, solar_status, mode
└── Initialize ground_state dictionary (connected=False, zeroed telemetry)

Step 2: Start serial listener thread (backend.py:244)
└── threading.Thread(target=serial_listener, daemon=True).start()
    │
    ├── If SIMULATION_MODE:
    │   └── Run simulated_telemetry_loop() — generates sin/cos data at 10Hz
    │
    └── If REAL HARDWARE:
        └── Enter reconnection loop:
            ├── Try to open COM port
            │   ├── Success → Reset backoff, enter _serial_read_loop()
            │   │   └── Read lines, parse "TELEM:{json}", update ground_state
            │   └── Failure → Exponential backoff (1s → 2s → 4s → ... → 30s max)
            └── On serial error → Close port, mark disconnected, retry
```

---

## 5. The Four Dashboard Modules — Full User Journey

### 5.1 Mission Control

**What the user sees:** A satellite tracking dashboard with a polar radar, ground track map, and telemetry readouts.

**User Journey:**

```
1. User selects "Mission Control" from the sidebar
2. User selects a satellite (e.g., "ISS (ZARYA)") from the dropdown
   → app.py calls orbit_engine.get_satellite_by_name("ISS (ZARYA)")
   → Sidebar shows "✅ Locked: ISS (ZARYA)"

3. Dashboard renders in IDLE state:
   ├── Polar Radar: Shows satellite position (Az/El) as a static dot
   ├── Telemetry Link: Shows "--- MHz", "--- Hz", "---" for battery/temp
   └── Ground Track: 2D Mercator map with orbital path plotted

4. User clicks "ACTIVATE TRACKING" toggle
   → st.session_state["mc_tracking_toggle"] = True
   → Creates DataManager(satellite_name) → Opens CSV log file
   → Starts mission_control_live_panel() fragment at 2Hz

5. Every 0.5 seconds (fragment refresh):
   a. orbit_engine.get_position(sat_obj) → Calculates current Az/El/Range
   b. mock_doppler = random.randint(-2000, 2000) → Simulates frequency shift
   c. radio_core.set_doppler_freq(base_freq, mock_doppler) → Updates radio tuning
   d. decoder.get_mock_packet() → Generates fake binary telemetry
   e. decoder.parse_frame(packet) → Decodes voltage, current, temp
   f. logger.log_packet(telem, pos, mock_doppler) → Writes row to CSV
   g. UI updates: Radar dot moves, metrics refresh, map redraws every 10s

6. If elevation > 0° → "LOCKED" indicator, green radar dot
   If elevation ≤ 0° → "LOS" indicator, grey radar dot

7. User clicks "ACTIVATE TRACKING" off
   → _stop_tracking_session() → Closes CSV file, resets counters

8. User switches to another module
   → Tracking session auto-closes via module change detection (app.py:280-284)
```

**Code Flow Diagram:**

```
app.py:mission_control_live_panel() [runs every 0.5s]
    │
    ├── orbit_engine.get_position(sat_obj)        → Az, El, Range, Timestamp
    │       └── satellite - station → topocentric.altaz()
    │
    ├── radio_core.set_doppler_freq()              → Prints tuned frequency
    │
    ├── decoder.get_mock_packet()                  → 19-byte binary packet
    │   └── decoder.parse_frame(raw_bytes)         → {voltage, current, temp, msg}
    │       └── TelemetryPacket.parse() + linear conversions + clamping
    │
    ├── logger.log_packet(telem, pos, doppler)     → CSV row appended
    │   └── data_manager.DataManager._writer.writerow()
    │
    ├── create_radar_fig(az, el)                   → Plotly polar chart
    │
    └── create_map_fig(pos, track, lat, lon)       → Plotly Scattergeo [every 10th cycle]
        └── orbit_engine.get_ground_track()        → 180min of lat/lon points
```

### 5.2 Pass Predictor

**What the user sees:** A table of upcoming satellite passes with start times, max elevations, and durations.

**User Journey:**

```
1. User selects "Pass Predictor" from sidebar
2. User clicks "Calculate Next 24h"
   → predictor.get_next_passes(sat_obj, hours=24, min_elevation=10)

3. Calculation:
   a. Skyfield's satellite.find_events() scans next 24 hours
   b. Returns (time, event_type) pairs:
      - Event 0 = AOS (Rise above 10° horizon)
      - Event 1 = TCA (Maximum elevation)
      - Event 2 = LOS (Set below 10° horizon)
   c. Groups into complete passes (AOS → TCA → LOS)
   d. Calculates duration: (LOS - AOS) × 24 × 3600 seconds

4. Results displayed:
   ├── Success toast: "Next AOS: HH:MM:SS UTC"
   └── Table with columns: Start (UTC) | Max Elevation | Duration

5. If no passes found → "No visible passes found." warning
```

### 5.3 Data Vault

**What the user sees:** A file browser for archived telemetry CSV logs with data analysis charts.

**User Journey:**

```
1. User selects "Data Vault" from sidebar
2. User selects data source:
   ├── "Mission Control Logs" → data/telemetry/mission_control/
   └── "HIL Telemetry Logs"   → data/telemetry/hil_side/

3. File list loads (sorted newest-first, .csv files only)
4. User selects a log file from dropdown
5. Dashboard renders:
   ├── Full CSV data in an interactive table (pd.read_csv → st.dataframe)
   └── Data Analysis chart:
       ├── If "light" column exists → Line chart of light readings over time
       └── If "battery_voltage" column exists → Line chart of voltage over time

6. User can DELETE a file:
   → os.remove(file_path) → st.toast("Deleted") → st.rerun()
```

### 5.4 HIL Telemetry (Digital Twin)

**What the user sees:** A 3D rotating cube (representing the satellite), real-time sensor readouts, and a command console.

**User Journey:**

```
1. User selects "HIL Telemetry" from sidebar
   → Calls run_hil_telemetry() from hil_mode.py

2. Header renders:
   ├── "HIL DIGITAL TWIN" title
   ├── Backend URL display (http://127.0.0.1:8000)
   ├── "MODE: FRAGMENT 2Hz" indicator
   └── PING button (tests uplink latency)

3. Layout splits into two columns:
   ├── Left (60%): Live Telemetry Panel (fragment, refreshes every 0.5s)
   └── Right (40%): Static Command Controls

4. Live Telemetry Panel (hil_live_telemetry_panel, every 0.5s):
   a. Polls GET http://127.0.0.1:8000/status
      → Returns ground_state dict with pitch, roll, light, led, solar, mode
   b. Extracts telemetry values
   c. Renders 4 metric cards:
      ├── Telemetry Link: ACTIVE/STALE
      ├── Pitch: ±XX.XX°
      ├── Roll: ±XX.XX°
      └── Power: Generating (solar) / Draining (battery)
   d. Caption with backend URL, LED state, solar state
   e. 3D Plotly Mesh3d cube:
      → create_3d_sat_fig(pitch, roll)
      → Applies rotation matrices Rx(pitch) × Ry(roll) to 8 vertices
      → Renders as cyan translucent cube

5. Command Console (static, drawn once):
   ├── PAYLOAD SYSTEMS:
   │   └── LED toggle switch (ON/OFF)
   │       → on_led_toggle() → send_command("LED_ON" or "LED_OFF")
   │       → POST http://127.0.0.1:8000/command {action: "LED_ON"}
   │       → Backend writes "LED_ON\n" over Serial to NodeMCU
   │       → NodeMCU: digitalWrite(D5, HIGH)
   │
   └── SOLAR ARRAY:
       ├── OPEN button   → send_command("SOLAR_DEPLOY")
       ├── CLOSE button  → send_command("SOLAR_RETRACT")
       └── AUTO button   → send_command("MODE_AUTO")
           → NodeMCU enters autonomous mode based on LDR readings

6. Error Handling:
   ├── If backend unreachable for >3 consecutive pings → "BACKEND OFFLINE" error
   ├── If command fails → st.error("Failed to send command")
   └── Session caches requests.Session() to reuse TCP connections
```

---

## 6. The Complete Data Journey — Byte by Byte

### 6.1 Downlink: Hardware → Dashboard

This is the path real sensor data takes from the physical MPU6050 to the 3D cube on screen:

```
STEP 1: PHYSICS → BITS (NodeMCU, satellite_new.ino)
────────────────────────────────────────────────
MPU6050 sensor (I2C address 0x68) → Reads 6 bytes of raw accelerometer data
  ├── AcX (2 bytes, int16) — acceleration along X axis
  ├── AcY (2 bytes, int16) — acceleration along Y axis
  └── AcZ (2 bytes, int16) — acceleration along Z axis

Trigonometry converts raw g-forces to angles:
  pitch = -(atan2(AcX, sqrt(AcY² + AcZ²)) × 180) / π
  roll  = (atan2(AcY, AcZ) × 180) / π

LDR photoresistor on pin A0 → analogRead() → 0-1023 integer

ArduinoJson serializes state into JSON:
  TELEM:{"pitch":12.5,"roll":-3.2,"light":743,"status":{"led":"OFF","solar":"DEPLOYED","mode":"AUTO"}}

Serial.print("TELEM:") + serializeJson() + Serial.println()
  → Newline-terminated string sent over USB at 115200 baud
  → Happens every 100ms (TELEMETRY_INTERVAL = 100ms = 10Hz)


STEP 2: USB → PYTHON (backend.py)
────────────────────────────────────────────────
Background thread: serial_listener() → _serial_read_loop()
  │
  ├── serial_port.readline().decode("utf-8").strip()
  │   → Gets: 'TELEM:{"pitch":12.5,"roll":-3.2,"light":743,...}'
  │
  ├── _handle_telemetry_line(line)
  │   ├── Checks line.startswith("TELEM:") → strips prefix
  │   ├── json.loads(json_str) → Python dict
  │   ├── _apply_telemetry_packet(packet):
  │   │   └── With state_lock: updates ground_state dict
  │   │       ├── ground_state["connected"] = True
  │   │       ├── ground_state["telemetry"]["pitch"] = 12.5
  │   │       ├── ground_state["telemetry"]["roll"] = -3.2
  │   │       └── ground_state["telemetry"]["light"] = 743
  │   │
  │   └── _log_telemetry_packet(packet):
  │       └── CSV row: "14:23:45, 12.5, -3.2, 0.0, 743, OFF, DEPLOYED, AUTO"
  │           → Flushed immediately to data/telemetry/hil_side/hil_session_XXXXXXXX.csv


STEP 3: PYTHON → BROWSER (hil_mode.py)
────────────────────────────────────────────────
hil_live_telemetry_panel() [Streamlit fragment, runs every 0.5s]:
  │
  ├── get_backend_data()
  │   └── requests.get("http://127.0.0.1:8000/status", timeout=0.3)
  │       → GET /status endpoint (backend.py:247-252)
  │       → With state_lock: checks if last_packet_time > 2s ago
  │       → Returns JSON: {"connected": true, "telemetry": {"pitch": 12.5, ...}}
  │
  ├── Extract pitch=12.5, roll=-3.2
  │
  └── create_3d_sat_fig(12.5, -3.2)
      ├── Define 8 vertices of a unit cube
      ├── Build rotation matrices:
      │   Rx = [[1,0,0],[0,cos(p),-sin(p)],[0,sin(p),cos(p)]]  (pitch)
      │   Ry = [[cos(r),0,sin(r)],[0,1,0],[-sin(r),0,cos(r)]]  (roll)
      ├── rotated_vertices = vertices @ Ry @ Rx
      └── Plotly Mesh3d renders the rotated cube in the browser
```

### 6.2 Uplink: Dashboard → Hardware

This is the path a command takes from a button click to a physical LED turning on:

```
STEP 1: USER CLICK (hil_mode.py)
────────────────────────────────────────────────
User clicks LED toggle → on_led_toggle() callback fires
  └── send_command("LED_ON")
      └── requests.post("http://127.0.0.1:8000/command",
                        json={"action": "LED_ON"}, timeout=0.3)


STEP 2: API → SERIAL (backend.py:259-305)
────────────────────────────────────────────────
POST /command endpoint receives Command(action="LED_ON")
  │
  ├── If SIMULATION_MODE:
  │   └── Directly mutate ground_state["telemetry"]["status"]["led"] = "ON"
  │
  └── If REAL HARDWARE:
      ├── command_str = "LED_ON\n"
      ├── encoded = command_str.encode("utf-8")
      ├── With serial_io_lock:
      │   ├── Check serial_port is open
      │   ├── serial_port.write(encoded) → 7 bytes over USB
      │   └── serial_port.flush() → Ensure immediate transmission
      └── Return {"status": "success"}


STEP 3: SERIAL → HARDWARE (satellite_new.ino)
────────────────────────────────────────────────
NodeMCU loop() → Phase A: THE UPLINK
  ├── Serial.available() → true (7 bytes waiting)
  ├── cmd = Serial.readStringUntil('\n') → "LED_ON"
  ├── cmd.trim() → "LED_ON"
  └── if (cmd == "LED_ON"):
      ├── digitalWrite(LED_PIN, HIGH)  → D5 pin goes to 3.3V
      └── led_state = "ON"
      → Current flows: D5 → 220Ω resistor → LED anode → LED cathode → GND
      → LED physically lights up

Total latency: < 500ms (button click to LED on)
```

### 6.3 Simulation Mode Data Flow

When no hardware is connected, the system has two simulation paths:

**Path A: UDP Simulator (`sim_satellite.py` → `udp_bridge.py` → `app.py`)**
```
sim_satellite.py:
  └── Every 100ms:
      ├── pitch = 10 × sin(t × 0.5)        → Tumbling motion
      ├── roll = 45 × cos(t × 0.2)          → Slower roll
      ├── sun_intensity = 500 + 500 × sin(t × 0.05)  → 2-min day/night cycle
      └── sock.sendto(json.dumps(state), ("127.0.0.1", 4210))

udp_bridge.py:
  └── Background thread listening on UDP 4210
      ├── Parses: "SAT1,pitch,roll,light,accel_z"
      └── Updates current_telemetry dict (thread-safe)
```

**Path B: Built-in Simulation (`backend.py` simulated_telemetry_loop)**
```
backend.py (when SIMULATION_MODE=True):
  └── Every 100ms:
      ├── pitch = sin(t × 0.5) × 45.0
      ├── roll = cos(t × 0.3) × 45.0
      ├── yaw = (t × 10) % 360.0
      ├── light = |sin(t × 0.1)| × 1023
      └── Updates ground_state directly (no serial needed)
```

---

## 7. Module-by-Module Technical Reference

### 7.1 `backend.py` — The FastAPI Broker

**Location:** `src/backend.py` (318 lines)
**Purpose:** The central nervous system. Bridges serial hardware and the HTTP-based UI.

**Key Components:**

| Component | Lines | Purpose |
|-----------|-------|---------|
| `state_lock` | 25 | `threading.Lock()` — protects `ground_state` from race conditions |
| `serial_io_lock` | 26 | `threading.Lock()` — serializes all read/write access to the COM port |
| `ground_state` | 50-60 | The single source of truth for current telemetry |
| `_shutdown_event` | 28 | `threading.Event()` — signals all threads to stop gracefully |
| `serial_listener()` | 211-241 | Supervised background worker with auto-reconnect |
| `_serial_read_loop()` | 165-188 | Inner loop: reads lines, handles errors, calls `_handle_telemetry_line()` |
| `simulated_telemetry_loop()` | 190-208 | Generates synthetic sin/cos telemetry for cloud/testing |
| `GET /status` | 247-252 | Returns `ground_state` (with 2-second staleness check) |
| `POST /command` | 259-305 | Writes command string to serial port or mutates sim state |
| `shutdown_event()` | 308-317 | Graceful shutdown: sets event, closes port, closes log |

**Reconnection Policy:**
- Starts at 1 second delay
- Doubles each failure: 1s → 2s → 4s → 8s → 16s → 30s (capped)
- Uses `_shutdown_event.wait(delay)` — interruptible sleep that stops immediately on shutdown

---

### 7.2 `udp_bridge.py` — The UDP Listener

**Location:** `src/udp_bridge.py` (114 lines)
**Purpose:** Receives telemetry from `sim_satellite.py` over UDP. Used in software simulation mode.

**Key Functions:**

| Function | Purpose |
|----------|---------|
| `start_listener()` | Spawns background thread (idempotent — runs only once via `_listener_running` flag) |
| `_udp_listener_loop()` | Binds to `0.0.0.0:4210`, parses `SAT1,pitch,roll,light,accel_z` CSV packets |
| `get_latest_data()` | Returns a **copy** of `current_telemetry` (prevents external mutation). Marks as disconnected if no packet in 3 seconds |
| `stop_listener()` | Sets `_shutdown_event`, which breaks the socket timeout loop |

**Packet Format:** `SAT1,<pitch>,<roll>,<light>,<accel_z>[,<yaw>]`

---

### 7.3 `orbit_engine.py` — Orbital Mechanics

**Location:** `src/orbit_engine.py` (167 lines)
**Purpose:** The mathematical brain. Calculates satellite positions using SGP4/Skyfield.

**Key Methods:**

| Method | Input | Output | What it does |
|--------|-------|--------|--------------|
| `__init__()` | config path | — | Loads timescale, ground station, downloads/caches TLEs |
| `_update_tles()` | — | — | Downloads from CelesTrak if file is >24h old. 3x retry with exponential backoff |
| `get_satellite_by_name()` | name, custom_tle | EarthSatellite | 3-tier matching: exact → stripped → fuzzy. Custom TLE takes priority |
| `get_position()` | satellite | {az, el, range, time} | Calculates topocentric position relative to ground station |
| `get_ground_track()` | satellite, duration | {lat[], lon[], times[]} | Generates 180 minutes of sub-satellite points (lat/lon) at 60s intervals |

**TLE Priority System:**
1. Custom TLE from `satellites.json` (for private/fictional satellites like GTUSAT-1)
2. Public TLE from `config/active_tles.txt` (downloaded from CelesTrak)

---

### 7.4 `pass_predictor.py` — AOS/LOS Calculator

**Location:** `src/pass_predictor.py` (56 lines)
**Purpose:** Predicts when a satellite will be visible from the ground station.

**`get_next_passes(satellite, hours=24, min_elevation=10)`:**
- Uses Skyfield's `satellite.find_events()` — a mathematical scan of the next 24 hours
- Groups events into complete passes: AOS (rise) → TCA (peak) → LOS (set)
- Filters by minimum elevation (default: 10° above horizon, to account for buildings/terrain)
- Returns list of dicts: `{aos, aos_iso, tca, max_el, los, los_iso, duration_str}`

---

### 7.5 `radio_core.py` — SDR & Doppler

**Location:** `src/radio_core.py` (98 lines)
**Purpose:** Interfaces with RTL-SDR hardware for radio reception, with Doppler correction.

**Key Concepts:**
- **Doppler Effect:** A satellite moving at 7.6 km/s shifts radio frequency. Approaching = higher frequency, receding = lower
- **`set_doppler_freq(target_freq, doppler_shift)`:** Corrected = Target + Shift
- **Mock Mode:** If no RTL-SDR dongle is detected, prints frequency changes to console instead
- **Graceful Fallback:** Triple try/except — import fails? Mock. Device open fails? Mock. No driver? Mock.

---

### 7.6 `decoder.py` — Binary Telemetry Parser

**Location:** `src/decoder.py` (97 lines)
**Purpose:** Parses binary satellite telemetry packets using the `construct` library.

**Packet Structure (19 bytes total):**

| Offset | Field | Size | Type | Notes |
|--------|-------|------|------|-------|
| 0-3 | Sync Word | 4 bytes | `\x1A\xCF\xFC\x1D` | Magic number to identify valid packets |
| 4-5 | Battery Voltage | 2 bytes | uint16 big-endian | Raw value × 0.01 = Volts |
| 6-7 | Panel Current | 2 bytes | uint16 big-endian | Raw value × 0.001 = Amps |
| 8 | Internal Temp | 1 byte | uint8 | Raw value − 20 = °C |
| 9-18 | Status Message | 10 bytes | UTF-8 padded string | e.g., "ALL_OK" |

**Validation:** All values are clamped to safe ranges. If clamping occurs, error counter increments and a warning is logged.

---

### 7.7 `data_manager.py` — CSV Black Box

**Location:** `src/data_manager.py` (98 lines)
**Purpose:** Persistent CSV logging for Mission Control orbital tracking sessions.

**File Structure:**
```
data/telemetry/mission_control/ISS (ZARYA)_20260628_201500.csv
│
├── Header: timestamp, azimuth, elevation, range, doppler, voltage, temp
└── Rows:   14:23:45, 312.45, 67.22, 421.00, -1500, 7.84, 25
```

**Key Design:**
- File handle stays open for the entire session (no open/close per write)
- `flush()` called after every row — data survives a crash
- Supports context manager (`with DataManager(...) as dm:`)
- `close_tracking_logger()` — standalone function for cleanup (idempotent)

---

### 7.8 `app.py` — The Streamlit Dashboard

**Location:** `src/web_ui/app.py` (444 lines)
**Purpose:** The main entry point for the entire UI. Routes between 4 modules.

**Key Patterns:**

| Pattern | Where | Why |
|---------|-------|-----|
| `@st.cache_resource` | `get_system()` | Initialize expensive objects (OrbitEngine, etc.) once per session |
| `@st.fragment(run_every="0.5s")` | `mission_control_live_panel()` | Refresh only the live panel at 2Hz without rerunning the entire page |
| `st.session_state` | Throughout | Persist tracking state, logger, loop counter across reruns |
| Module change detection | Lines 277-284 | Auto-close tracking session when switching away from Mission Control |
| Throttled map refresh | Lines 231-242 | Ground track recalculates every 10th cycle (~5 seconds) instead of every 0.5s |

---

### 7.9 `hil_mode.py` — 3D Digital Twin UI

**Location:** `src/web_ui/hil_mode.py` (283 lines)
**Purpose:** Real-time 3D visualization and command console for hardware-in-the-loop mode.

**3D Cube Math (create_3d_sat_fig):**
1. Define 8 vertices of a unit cube (±0.5 on each axis)
2. Convert pitch/roll from degrees to radians
3. Build rotation matrices Rx (pitch around X) and Ry (roll around Y)
4. Multiply: `rotated = vertices @ Ry @ Rx`
5. Render as Plotly `Mesh3d` with 12 triangular faces

**Resilient HTTP Polling:**
- `get_backend_data()` uses a cached `requests.Session()` (connection pooling)
- Tracks `failed_pings` counter — returns stale data for up to 3 failures
- After 3 consecutive failures → returns `None` → "BACKEND OFFLINE" error
- On success → resets counter, caches `last_good_telemetry`

---

### 7.10 `sim_satellite.py` — Software Simulator

**Location:** `sim_satellite.py` (99 lines, project root)
**Purpose:** Simulates a tumbling satellite with a day/night cycle. Replaces physical hardware for testing.

**Physics Model:**
```python
pitch = 10 × sin(t × 0.5)           # ±10° oscillation, ~12.6s period
roll = 45 × cos(t × 0.2)            # ±45° oscillation, ~31.4s period
sun_intensity = 500 + 500 × sin(t × 0.05)  # Full cycle ≈ 2 minutes
```

**Autonomous Solar Logic (with Hysteresis):**
- Deploy threshold: light > 400
- Retract threshold: light < 300
- Deadband (300-400) prevents flutter in transitional lighting

**Networking:**
- Sends JSON over UDP to `127.0.0.1:4210` at 10Hz
- Listens for commands on UDP `127.0.0.1:4220` (background thread)

---

### 7.11 Arduino Firmware (`.ino` files)

**`satellite.ino` (113 lines) — Original firmware:**
- Direct I2C register access to MPU6050 (raw Wire.h calls)
- No fault tolerance — hangs if MPU6050 disconnects
- No temperature reading

**`satellite_new.ino` (176 lines) — Improved firmware:**
- Uses Adafruit MPU6050 library (cleaner, more reliable)
- **Fault tolerance:** If IMU fails, enters "degraded mode" — sends zeroed attitude but still transmits LDR and status data
- **Auto-recovery:** Retries IMU initialization every 5 seconds
- **I2C bus-clearing hack:** Toggles SCL pin 10 times on boot to unstick frozen I2C bus
- Adds temperature telemetry from MPU6050's built-in thermometer
- Staggered boot sequence: I2C init → 2-second delay → GPIO init (prevents voltage inrush crash)

---

## 8. Configuration Files Reference

### `config/stations.conf`
```ini
[GROUND_STATION]
name = Ahmedabad_Home_Base
latitude = 23.0225        # Ahmedabad, India
longitude = 72.5714
altitude = 53             # meters above sea level
min_elevation = 10.0      # ignore satellites below 10° (buildings block the view)
```

### `config/satellites.json`
```json
{
  "satellites": [
    {
      "name": "ISS (ZARYA)",           // Must match TLE file exactly
      "frequency": 145800000,          // 145.800 MHz (VHF amateur band)
      "description": "International Space Station"
    },
    {
      "name": "GTUSAT-1",
      "frequency": 437500000,          // 437.500 MHz (UHF CubeSat band)
      "custom_tle": ["1 99999U...", "2 99999..."]  // Override for fictional/private sats
    },
    {
      "name": "NOAA 19",
      "frequency": 137100000,          // 137.100 MHz (Weather satellite APT)
      "description": "Weather Satellite"
    }
  ]
}
```

### `config/active_tles.txt`
- Standard NORAD Two-Line Element format
- Auto-downloaded from CelesTrak every 24 hours
- Contains ~28 space station objects (ISS, CSS, Soyuz, Dragon, etc.)

---

## 9. State Management & Thread Safety

The system has **two critical shared resources** that require thread-safe access:

### Resource 1: `ground_state` (backend.py)

```python
ground_state = {
    "connected": False,          # Link status
    "last_packet_time": 0,       # Unix timestamp of last valid packet
    "telemetry": {
        "pitch": 0.0,            # Degrees
        "roll": 0.0,             # Degrees
        "accel_z": 9.8,          # m/s² (gravity reference)
        "light": 0,              # 0-1023 ADC value
        "status": {
            "led": "OFF",        # "ON" or "OFF"
            "solar": "RETRACTED", # "DEPLOYED" or "RETRACTED"
            "mode": "MANUAL"     # "MANUAL" or "AUTO"
        }
    }
}
```

**Protected by:** `state_lock` (threading.Lock)
**Writers:** `_apply_telemetry_packet()` (serial thread), `send_command()` (HTTP thread, sim mode only)
**Readers:** `get_status()` (HTTP thread)

### Resource 2: `serial_port` (backend.py)

**Protected by:** `serial_io_lock` (threading.Lock)
**Writers/Readers:** `_read_serial_line()` (serial thread), `send_command()` (HTTP thread)

### Why Two Locks?

Using a single lock would create a bottleneck — reading telemetry at 10Hz would block command sends. With two separate locks:
- `state_lock` is held for microseconds (dict update)
- `serial_io_lock` is held for milliseconds (I/O operation)
- Neither blocks the other

---

## 10. Error Handling & Fault Tolerance

| Failure Scenario | Where Handled | Recovery Strategy |
|-----------------|---------------|-------------------|
| COM port busy (Arduino IDE open) | `_open_serial_port()` | Exponential backoff retry (1s → 30s) |
| Serial cable unplugged | `_serial_read_loop()` | Catches `SerialException`, closes port, triggers reconnect |
| Malformed JSON packet | `_handle_telemetry_line()` | Catches `JSONDecodeError`, prints warning, continues |
| Corrupted binary bytes | `_serial_read_loop()` | Catches `UnicodeDecodeError`, skips packet |
| Backend unreachable | `get_backend_data()` | Returns cached `last_good_telemetry` for up to 3 failures |
| TLE download fails | `_update_tles()` | 3x retry with backoff, falls back to cached file |
| IMU sensor crashes | `satellite_new.ino` | Degraded mode — sends zeroed attitude, retries every 5s |
| I2C bus lockup | `satellite_new.ino` setup() | SCL bus-clearing hack (10 clock pulses on boot) |
| SDR dongle missing | `RadioCore.__init__()` | Falls back to mock mode automatically |
| Out-of-range telemetry | `TelemetryDecoder.parse_frame()` | Clamps to safe ranges, increments error counter |

---

## 11. Complete File Map

```
ngsc_project/
│
├── src/
│   ├── __init__.py                  # Package marker (empty)
│   ├── backend.py                   # FastAPI broker — Serial ↔ HTTP bridge (318 lines)
│   ├── udp_bridge.py                # UDP telemetry listener for sim mode (114 lines)
│   ├── orbit_engine.py              # SGP4/Skyfield orbital mechanics (167 lines)
│   ├── pass_predictor.py            # AOS/LOS satellite pass calculator (56 lines)
│   ├── radio_core.py                # RTL-SDR interface with Doppler (98 lines)
│   ├── decoder.py                   # Binary telemetry packet parser (97 lines)
│   ├── data_manager.py              # CSV Black Box logger (98 lines)
│   ├── utils.py                     # Placeholder (empty)
│   │
│   └── web_ui/
│       ├── __init__.py              # Package marker (empty)
│       ├── app.py                   # Main Streamlit dashboard — 4 modules (444 lines)
│       ├── hil_mode.py              # 3D Digital Twin & command console (283 lines)
│       ├── styles.css               # Custom dark theme CSS (204 lines)
│       └── assets/                  # Static assets directory
│
├── config/
│   ├── satellites.json              # Satellite names, frequencies, custom TLEs
│   ├── stations.conf                # Ground station coordinates (Ahmedabad)
│   └── active_tles.txt              # NORAD TLE data (auto-updated from CelesTrak)
│
├── data/
│   └── telemetry/
│       ├── hil_side/                # HIL hardware session logs (CSV)
│       └── mission_control/         # Orbital tracking session logs (CSV)
│
├── satellite.ino                    # NodeMCU firmware v1 — raw I2C (113 lines)
├── satellite_new.ino                # NodeMCU firmware v2 — Adafruit + fault tolerance (176 lines)
├── sim_satellite.py                 # Software satellite simulator (99 lines)
│
├── test_bridge.py                   # Tests UDP bridge listener
├── test_fire.py                     # Tests raw UDP command fire
├── test_telemetry.py                # Tests raw UDP packet reception
│
├── tests/
│   ├── test_decoder.py              # (empty — placeholder)
│   └── test_orbit.py                # (empty — placeholder)
│
├── requirements.txt                 # Pinned dependencies (32 lines)
├── README.md                        # Project documentation (396 lines)
└── .gitignore                       # Git ignore rules
```

---

> **End of UserJourney.md** — This document covers every screen, every function, every data path, and every failure mode in the NGSC V3.0 system. For interview preparation and theoretical concepts, see `Theory.md`.
