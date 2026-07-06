# 🎓 NGSC V3.0 — Theory & Interview Bible

> **What is this document?**
> The single source of truth for every concept, technology, pattern, algorithm, and design decision in the NGSC V3.0 project — written as interview preparation material. If a question can be asked about this project, the answer is here.

---

## Table of Contents

1. [Project Identity — The Elevator Pitch](#1-project-identity--the-elevator-pitch)
2. [Core Concepts & Domain Theory](#2-core-concepts--domain-theory)
   - [2.1 Orbital Mechanics & SGP4](#21-orbital-mechanics--sgp4)
   - [2.2 Two-Line Element Sets (TLEs)](#22-two-line-element-sets-tles)
   - [2.3 Satellite Pass Prediction (AOS/LOS)](#23-satellite-pass-prediction-aoslos)
   - [2.4 Doppler Effect in Satellite Communications](#24-doppler-effect-in-satellite-communications)
   - [2.5 Attitude Determination (IMU / Euler Angles)](#25-attitude-determination-imu--euler-angles)
   - [2.6 Hardware-in-the-Loop (HIL) Testing](#26-hardware-in-the-loop-hil-testing)
   - [2.7 Telemetry, Tracking & Command (TT&C)](#27-telemetry-tracking--command-ttc)
3. [Architecture & Design Patterns](#3-architecture--design-patterns)
   - [3.1 Three-Tier Decoupled Architecture](#31-three-tier-decoupled-architecture)
   - [3.2 Data Broker / Mediator Pattern](#32-data-broker--mediator-pattern)
   - [3.3 Observer Pattern via HTTP Polling](#33-observer-pattern-via-http-polling)
   - [3.4 Graceful Degradation & Fallback Pattern](#34-graceful-degradation--fallback-pattern)
   - [3.5 Exponential Backoff with Jitter](#35-exponential-backoff-with-jitter)
   - [3.6 Singleton Initialization (Idempotent Start)](#36-singleton-initialization-idempotent-start)
   - [3.7 Producer–Consumer Pattern (Serial Thread)](#37-producerconsumer-pattern-serial-thread)
   - [3.8 Digital Twin Pattern](#38-digital-twin-pattern)
   - [3.9 Hysteresis in Control Systems](#39-hysteresis-in-control-systems)
   - [3.10 Protocol Framing (TELEM: Prefix)](#310-protocol-framing-telem-prefix)
4. [Tech Stack — Deep Theory](#4-tech-stack--deep-theory)
   - [4.1 Python & CPython Runtime](#41-python--cpython-runtime)
   - [4.2 FastAPI & ASGI (Uvicorn)](#42-fastapi--asgi-uvicorn)
   - [4.3 Streamlit — Reactive UI Framework](#43-streamlit--reactive-ui-framework)
   - [4.4 Skyfield — Astronomical Computation](#44-skyfield--astronomical-computation)
   - [4.5 Plotly — Interactive Visualization](#45-plotly--interactive-visualization)
   - [4.6 PySerial — Serial Communication](#46-pyserial--serial-communication)
   - [4.7 Construct — Declarative Binary Parsing](#47-construct--declarative-binary-parsing)
   - [4.8 NumPy — Numerical Computing](#48-numpy--numerical-computing)
   - [4.9 Arduino / ESP8266 Platform](#49-arduino--esp8266-platform)
   - [4.10 I2C Protocol](#410-i2c-protocol)
5. [Algorithms & Data Structures](#5-algorithms--data-structures)
   - [5.1 SGP4 Orbital Propagator](#51-sgp4-orbital-propagator)
   - [5.2 Topocentric Coordinate Transform](#52-topocentric-coordinate-transform)
   - [5.3 3D Rotation Matrices (Euler Angles)](#53-3d-rotation-matrices-euler-angles)
   - [5.4 Accelerometer-to-Angle Trigonometry](#54-accelerometer-to-angle-trigonometry)
   - [5.5 Doppler Shift Calculation](#55-doppler-shift-calculation)
   - [5.6 Voltage Divider (LDR Circuit)](#56-voltage-divider-ldr-circuit)
   - [5.7 Linear Calibration (y = mx + c)](#57-linear-calibration-y--mx--c)
   - [5.8 Value Clamping (Range Validation)](#58-value-clamping-range-validation)
   - [5.9 Sub-Satellite Point Calculation](#59-sub-satellite-point-calculation)
   - [5.10 Fuzzy String Matching (Satellite Lookup)](#510-fuzzy-string-matching-satellite-lookup)
6. [Concurrency & Thread Safety](#6-concurrency--thread-safety)
   - [6.1 Threading Model](#61-threading-model)
   - [6.2 Lock Granularity — Why Two Locks?](#62-lock-granularity--why-two-locks)
   - [6.3 Daemon Threads](#63-daemon-threads)
   - [6.4 threading.Event for Graceful Shutdown](#64-threadingevent-for-graceful-shutdown)
   - [6.5 The GIL and Why It Matters Here](#65-the-gil-and-why-it-matters-here)
7. [Networking & Communication Protocols](#7-networking--communication-protocols)
   - [7.1 Serial UART (RS-232 / USB CDC)](#71-serial-uart-rs-232--usb-cdc)
   - [7.2 UDP Datagrams](#72-udp-datagrams)
   - [7.3 HTTP/REST API](#73-httprest-api)
   - [7.4 Protocol Comparison Table](#74-protocol-comparison-table)
8. [Embedded Systems & IoT Concepts](#8-embedded-systems--iot-concepts)
   - [8.1 NodeMCU ESP8266 Architecture](#81-nodemcu-esp8266-architecture)
   - [8.2 MPU6050 IMU — 6-Axis Inertial Measurement](#82-mpu6050-imu--6-axis-inertial-measurement)
   - [8.3 Analog-to-Digital Conversion (ADC)](#83-analog-to-digital-conversion-adc)
   - [8.4 GPIO & Digital Output](#84-gpio--digital-output)
   - [8.5 I2C Bus Recovery](#85-i2c-bus-recovery)
   - [8.6 Staggered Boot Sequence](#86-staggered-boot-sequence)
9. [Data Engineering & Persistence](#9-data-engineering--persistence)
   - [9.1 CSV as a Flight Recorder ("Black Box")](#91-csv-as-a-flight-recorder-black-box)
   - [9.2 Write-Through Flush Strategy](#92-write-through-flush-strategy)
   - [9.3 TLE File Caching](#93-tle-file-caching)
10. [Error Handling & Fault Tolerance](#10-error-handling--fault-tolerance)
11. [Testing Strategy](#11-testing-strategy)
12. [DevOps & Deployment](#12-devops--deployment)
13. [Interview Questions & Answers — By Topic](#13-interview-questions--answers--by-topic)
    - [13.1 Architecture & Design](#131-architecture--design)
    - [13.2 Concurrency & Threading](#132-concurrency--threading)
    - [13.3 Networking & Protocols](#133-networking--protocols)
    - [13.4 Embedded Systems & IoT](#134-embedded-systems--iot)
    - [13.5 Algorithms & Math](#135-algorithms--math)
    - [13.6 Python & Frameworks](#136-python--frameworks)
    - [13.7 System Design & Trade-offs](#137-system-design--trade-offs)
    - [13.8 Debugging & Problem Solving](#138-debugging--problem-solving)
    - [13.9 Behavioral / Project-Based](#139-behavioral--project-based)

---

## 1. Project Identity — The Elevator Pitch

**NGSC V3.0** (Next-Generation Satellite Ground Control Station) is a full-stack ground control station that bridges theoretical orbital mechanics with physical IoT hardware. It enables a mission operator to:

- **Track real satellites** (ISS, NOAA 19, custom CubeSats) using SGP4 propagation and TLE data from CelesTrak
- **Visualize a 3D Digital Twin** that rotates in real time based on live MPU6050 accelerometer data streamed from an ESP8266 at 10Hz
- **Send uplink commands** to physical hardware (LED on/off, solar panel deploy/retract) from the browser, through FastAPI, over Serial USB — end-to-end latency under 500ms
- **Autonomously manage subsystems** — the solar array deploys/retracts based on live LDR readings using hysteresis control, with no human input
- **Record every telemetry packet** into a timestamped CSV "Black Box" for post-mission analysis

**The tech stack spans three domains:** web development (FastAPI + Streamlit + Plotly), scientific computing (Skyfield + SGP4 + NumPy), and embedded systems (Arduino C++ on ESP8266 with I2C sensors).

---

## 2. Core Concepts & Domain Theory

### 2.1 Orbital Mechanics & SGP4

**What is orbital mechanics?**
The branch of physics and engineering that predicts the motion of objects orbiting a central body (Earth). Satellites in Low Earth Orbit (LEO) travel at ~7.6 km/s, completing one orbit every ~90 minutes.

**What is SGP4?**
The **Simplified General Perturbations Model 4** is the standard algorithm used by NORAD and NASA to predict satellite positions. It accounts for:

| Perturbation | Cause | Effect |
|---|---|---|
| **J2 oblateness** | Earth is not a perfect sphere — it bulges at the equator | Orbital plane precesses (rotates) over time |
| **Atmospheric drag** | Residual atmosphere at LEO altitudes (200–2000 km) | Orbit decays, altitude decreases |
| **Solar radiation pressure** | Photons exert force on satellite surfaces | Slight orbital perturbation for large surface-area sats |
| **Third-body effects** | Gravitational pull from the Moon and Sun | Long-term orbit shape changes |

**How it's used in NGSC:**
`orbit_engine.py` loads TLE data and passes it to Skyfield's `EarthSatellite` class, which internally runs SGP4 propagation to compute the satellite's position at any given time.

```python
# orbit_engine.py — core usage
satellite = EarthSatellite(tle_line1, tle_line2, name, self.ts)
topocentric = (satellite - self.station).at(self.ts.now())
alt, az, distance = topocentric.altaz()
```

**Key distinction:** SGP4 outputs are in the **TEME** (True Equator, Mean Equinox) reference frame. Skyfield handles the conversion to topocentric (observer-relative) coordinates automatically.

---

### 2.2 Two-Line Element Sets (TLEs)

**What is a TLE?**
A standardized data format that encodes a satellite's orbital parameters in exactly two lines of 69 characters each. Created by NORAD for tracking ~30,000 objects in orbit.

**Format breakdown:**
```
Line 1: 1 25544U 98067A   24025.50000000  .00000000  00000-0  00000-0 0  9991
         │ │     │         │               │           │         │
         │ │     │         │               │           │         └── Element set number
         │ │     │         │               │           └── B* drag term
         │ │     │         │               └── Mean motion derivative
         │ │     │         └── Epoch (year + day fraction in UTC)
         │ │     └── International designator (launch year + piece)
         │ └── NORAD Catalog Number (unique ID per object)
         └── Line number

Line 2: 2 25544  51.6400 120.0000 0005000 100.0000 250.0000 15.50000000    16
         │ │     │        │        │       │        │        │
         │ │     │        │        │       │        │        └── Revolution number
         │ │     │        │        │       │        └── Mean motion (revs/day)
         │ │     │        │        │       └── Mean anomaly (degrees)
         │ │     │        │        └── Argument of perigee (degrees)
         │ │     │        └── Eccentricity (decimal point assumed)
         │ │     └── Right Ascension of Ascending Node (RAAN, degrees)
         │ └── Inclination (degrees)
         └── Line number
```

**Six Keplerian elements** encoded in a TLE:

| Element | Symbol | Meaning |
|---------|--------|---------|
| Inclination | *i* | Tilt of the orbital plane relative to the equator |
| RAAN | *Ω* | Where the orbit crosses the equator going north |
| Eccentricity | *e* | Shape of the orbit (0 = circle, 0–1 = ellipse) |
| Argument of Perigee | *ω* | Where the closest point to Earth is in the orbit |
| Mean Anomaly | *M* | Where the satellite is along its orbit at epoch |
| Mean Motion | *n* | How many orbits per day |

**In NGSC:**
- TLEs are auto-downloaded from CelesTrak (`celestrak.org`) every 24 hours
- Custom TLEs can be specified in `satellites.json` for private/fictional satellites
- TLE freshness is critical — accuracy degrades within days due to atmospheric drag variations

---

### 2.3 Satellite Pass Prediction (AOS/LOS)

**Core terminology:**

| Term | Full Name | Meaning |
|------|-----------|---------|
| **AOS** | Acquisition of Signal | Moment the satellite rises above the minimum elevation angle |
| **LOS** | Loss of Signal | Moment the satellite sets below the minimum elevation angle |
| **TCA** | Time of Closest Approach | When the satellite reaches maximum elevation (shortest distance) |
| **Elevation** | — | Angle above the horizon (0° = horizon, 90° = directly overhead) |
| **Azimuth** | — | Compass bearing (0°/360° = North, 90° = East, 180° = South, 270° = West) |

**How `pass_predictor.py` works:**
1. Skyfield's `satellite.find_events()` numerically scans the next 24 hours
2. It returns event codes: 0 = Rise, 1 = Culmination, 2 = Set
3. Events are grouped into complete passes (AOS → TCA → LOS)
4. Duration is calculated: `(LOS_time - AOS_time) × 24 × 3600` seconds
5. Minimum elevation filter (default 10°) removes low passes that are blocked by terrain/buildings

**Why 10° minimum elevation?**
Radio signals at low elevation travel through more atmosphere (longer path length), suffer more attenuation and multipath interference, and are typically blocked by buildings and trees. Professional ground stations rarely track below 5–10°.

---

### 2.4 Doppler Effect in Satellite Communications

**The physics:**
When a source of electromagnetic waves moves relative to an observer, the observed frequency shifts:
- **Approaching** (positive radial velocity) → frequency **increases**
- **Receding** (negative radial velocity) → frequency **decreases**

**The formula:**
```
f_observed = f_transmitted × (1 + v_radial / c)
```
Where `c` = speed of light (3 × 10⁸ m/s) and `v_radial` = satellite's radial velocity relative to the ground station.

**Scale in LEO:** The ISS moves at ~7.6 km/s. At 145.8 MHz (VHF), the maximum Doppler shift is approximately ±3.4 kHz. At 437.5 MHz (UHF), it's approximately ±10 kHz.

**In NGSC:**
`radio_core.py` implements: `corrected_freq = target_freq + doppler_shift`

In the current implementation, the Doppler value is simulated with `random.randint(-2000, 2000)` in Mission Control mode. In a real deployment, it would be calculated from the satellite's range-rate.

---

### 2.5 Attitude Determination (IMU / Euler Angles)

**What is attitude?**
A spacecraft's orientation in 3D space, expressed as three angles:

| Axis | Angle | Motion |
|------|-------|--------|
| **Pitch** | Rotation around X-axis | Nose up/down |
| **Roll** | Rotation around Y-axis | Tilting left/right |
| **Yaw** | Rotation around Z-axis | Turning left/right |

**How the MPU6050 measures it:**
The MPU6050 is a 6-axis IMU containing a 3-axis accelerometer and a 3-axis gyroscope. The accelerometer measures the direction of gravity. When the sensor is tilted, the gravity vector projects differently onto the three axes:

```
pitch = -atan2(Ax, sqrt(Ay² + Az²)) × (180 / π)
roll  =  atan2(Ay, Az) × (180 / π)
```

**Why yaw is always 0.0:**
The accelerometer cannot detect rotation around the vertical axis (yaw), because gravity has no horizontal component. Yaw detection requires a **magnetometer** (compass) or integrating gyroscope data over time (which accumulates drift).

**In NGSC:**
Both the Arduino firmware (`satellite.ino`, `satellite_new.ino`) and the 3D visualization (`hil_mode.py`) use these exact formulas. The firmware calculates angles on the microcontroller, and the dashboard applies the same angles to rotate a 3D cube mesh using rotation matrices.

---

### 2.6 Hardware-in-the-Loop (HIL) Testing

**Definition:**
A testing methodology where part of the system is real physical hardware while the rest is simulated in software. It sits between pure software simulation and full system integration testing.

**NGSC's HIL setup:**
- **Real hardware:** NodeMCU ESP8266 with MPU6050 (IMU), LDR (light sensor), LED (payload), connected via USB Serial
- **Simulated:** Orbital position (SGP4), radio link (Doppler), telemetry decoding (binary packets)
- **The bridge:** FastAPI backend ingests real sensor data over Serial and serves it to the Streamlit dashboard over HTTP

**Why HIL matters for interviews:**
It demonstrates understanding of system integration, embedded systems communication, and the ability to work across hardware/software boundaries — a key skill for IoT, robotics, and aerospace roles.

---

### 2.7 Telemetry, Tracking & Command (TT&C)

**TT&C** is the fundamental discipline of satellite operations:

| Component | Direction | NGSC Implementation |
|-----------|-----------|---------------------|
| **Telemetry** | Satellite → Ground | MPU6050/LDR data streamed over Serial at 10Hz, parsed by `backend.py` |
| **Tracking** | Ground computation | SGP4 propagation via `orbit_engine.py`, position displayed on radar/map |
| **Command** | Ground → Satellite | HTTP POST → FastAPI → Serial write → NodeMCU executes command |

**Downlink packet format:**
```
TELEM:{"pitch":12.5,"roll":-3.2,"light":743,"status":{"led":"OFF","solar":"DEPLOYED","mode":"AUTO"}}
```

**Uplink command format:**
```
LED_ON\n
SOLAR_DEPLOY\n
MODE_AUTO\n
```

---

## 3. Architecture & Design Patterns

### 3.1 Three-Tier Decoupled Architecture

**The three tiers:**

| Tier | Component | Technology | Protocol |
|------|-----------|------------|----------|
| **Space Segment** | NodeMCU ESP8266 | Arduino C++ | Serial USB (115200 baud) |
| **Ground Backend** | FastAPI Broker | Python + Uvicorn | HTTP REST + Serial |
| **Mission UI** | Streamlit Dashboard | Python + Plotly | HTTP (port 8501) |

**Why decoupled?**
1. **No UI freeze:** Serial I/O is blocking. If the Streamlit process directly read from the COM port, the web page would freeze every time it waited for hardware data. The backend handles Serial in a background thread; the UI just makes fast HTTP GETs.
2. **Independent scaling:** The backend and frontend can run on different machines. In cloud deployment, the backend runs on Render with `SIMULATION_MODE=True`.
3. **Failure isolation:** If the hardware disconnects, the backend reconnects silently while the UI continues showing last-known data. The UI never crashes.

**Interview framing:**
> "I chose a three-tier architecture because the two primary I/O channels — Serial USB to hardware and HTTP to the browser — have fundamentally different timing characteristics. Serial is synchronous and blocking; HTTP is request-response. By introducing a FastAPI middleware layer, I decoupled these concerns. The backend reads serial data in a daemon thread and exposes it via a REST endpoint, so the Streamlit UI never blocks on hardware I/O."

---

### 3.2 Data Broker / Mediator Pattern

**What it is:**
The FastAPI backend acts as a **data broker** — it sits between the hardware and the UI, ingesting data from one protocol (Serial) and serving it through another (HTTP). Neither the hardware nor the UI need to know about each other.

**Implementation in `backend.py`:**
- `ground_state` dictionary is the shared data store
- Serial thread writes to it (producer)
- HTTP endpoint reads from it (consumer)
- `state_lock` ensures thread-safe access

**Why not direct communication?**
- Serial ports are exclusive resources on Windows — only one process can open a COM port
- Streamlit re-runs the entire Python script on every user interaction — it can't hold a persistent Serial connection
- The broker enables future extensibility: swap Serial for LoRa, WebSocket, or MQTT without changing the UI

---

### 3.3 Observer Pattern via HTTP Polling

**In the traditional Observer pattern**, subjects notify observers of state changes. NGSC implements a **polling-based variant**:

- **Subject:** `ground_state` in `backend.py`
- **Observer:** `hil_mode.py` fragment that polls `GET /status` every 0.5 seconds
- **Why polling instead of WebSockets?** Streamlit doesn't natively support WebSocket subscriptions. The `@st.fragment(run_every="0.5s")` decorator provides a clean 2Hz polling mechanism that's sufficient for real-time visualization without the complexity of a WebSocket setup.

**Trade-off analysis:**

| Approach | Latency | Complexity | Streamlit Compatible |
|----------|---------|------------|---------------------|
| HTTP Polling (2Hz) | 250–500ms | Low | ✅ Yes |
| WebSocket Push | <50ms | High | ❌ Requires custom components |
| Server-Sent Events | <100ms | Medium | ❌ Not natively supported |

---

### 3.4 Graceful Degradation & Fallback Pattern

**Principle:** When a component fails, the system continues operating at reduced capability rather than crashing entirely.

**Examples in NGSC:**

| Component | Failure | Degraded Behavior |
|-----------|---------|-------------------|
| RTL-SDR dongle missing | `RadioCore.__init__()` | Falls back to mock mode — prints frequency changes to console |
| MPU6050 sensor crash | `satellite_new.ino` | Sends zeroed pitch/roll but continues LDR + status telemetry |
| Backend unreachable | `hil_mode.py` | Returns cached `last_good_telemetry` for up to 3 consecutive failures |
| TLE download fails | `orbit_engine.py` | Uses stale cached TLE file instead of crashing |
| COM port busy | `backend.py` | Exponential backoff retry — keeps trying without operator intervention |

**The `RadioCore` triple-fallback is exemplary:**
```python
# Level 1: Import fails (no driver installed)
try:
    from rtlsdr import RtlSdr
    HAS_SDR = True
except ImportError:
    HAS_SDR = False

# Level 2: Constructor — device open fails
if not self.mock_mode:
    try:
        self.sdr = RtlSdr()
    except Exception:
        self.mock_mode = True  # Fall back to mock

# Level 3: Runtime — any method call fails
if not self.mock_mode:
    self.sdr.center_freq = corrected_freq
else:
    print(f"[RADIO] Tuning to: {corrected_freq/1e6:.6f} MHz")
```

---

### 3.5 Exponential Backoff with Jitter

**What it is:**
A reconnection strategy where wait time doubles after each failure, preventing thundering herd problems and reducing resource waste.

**Implementation in `backend.py`:**
```python
RECONNECT_MIN_DELAY_S = 1.0
RECONNECT_MAX_DELAY_S = 30.0

def _wait_for_reconnect(delay_s: float) -> float:
    if _shutdown_event.wait(delay_s):  # Interruptible sleep!
        return delay_s
    return min(delay_s * 2, RECONNECT_MAX_DELAY_S)
```

**Progression:** 1s → 2s → 4s → 8s → 16s → 30s → 30s → 30s (capped)

**Key design detail:** The backoff uses `threading.Event.wait()` instead of `time.sleep()`. This means:
- During normal operation, it sleeps for the backoff duration
- On shutdown, `_shutdown_event.set()` immediately wakes the thread, allowing a clean exit
- This is a **critical interview point** — it shows understanding of interruptible blocking vs. hard sleep

**Also in TLE downloads (`orbit_engine.py`):**
```python
retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
```
This uses `urllib3`'s built-in retry with backoff for HTTP downloads.

---

### 3.6 Singleton Initialization (Idempotent Start)

**Problem:** In `udp_bridge.py`, `start_listener()` might be called multiple times (Streamlit re-runs the script). Starting multiple listener threads would cause port binding conflicts.

**Solution:** A module-level boolean flag ensures the thread starts exactly once:
```python
_listener_running = False

def start_listener():
    global _listener_running
    if not _listener_running:
        t = threading.Thread(target=_udp_listener_loop, daemon=True)
        t.start()
        _listener_running = True
```

**In Streamlit's context:** `@st.cache_resource` on `get_system()` in `app.py` achieves the same goal for expensive objects like `OrbitEngine`. The decorator ensures the function body runs once per session, returning the cached result on subsequent calls.

---

### 3.7 Producer–Consumer Pattern (Serial Thread)

**The classic concurrency pattern applied:**

| Role | Component | Data |
|------|-----------|------|
| **Producer** | Serial listener thread (`_serial_read_loop`) | Reads lines from COM port, parses JSON, updates `ground_state` |
| **Consumer** | HTTP handler (`GET /status`) | Reads `ground_state` and returns it to the UI |
| **Buffer** | `ground_state` dictionary | Holds the latest telemetry (latest-value semantics — not a queue) |
| **Synchronization** | `state_lock` (threading.Lock) | Ensures atomic reads and writes |

**Why latest-value, not a queue?**
The UI only cares about the *current* state. There's no need to process every historical packet in order — we want the freshest data on screen. This is a deliberate design choice: we sacrifice guaranteed delivery for minimal latency.

---

### 3.8 Digital Twin Pattern

**Definition:** A virtual replica of a physical object that updates in real time based on sensor data from the physical counterpart.

**In NGSC:**
- **Physical twin:** NodeMCU ESP8266 with MPU6050 on a breadboard
- **Digital twin:** A 3D Plotly Mesh3d cube in the browser
- **Synchronization:** MPU6050 → pitch/roll → Serial → FastAPI → HTTP → Streamlit → Rotation matrices → 3D rendering
- **Update rate:** Physical hardware transmits at 10Hz; the digital twin renders at 2Hz (Streamlit fragment limit)

**The math bridge:**
```python
# hil_mode.py — create_3d_sat_fig()
p, r = np.radians(pitch), np.radians(roll)
Rx = [[1, 0, 0], [0, cos(p), -sin(p)], [0, sin(p), cos(p)]]
Ry = [[cos(r), 0, sin(r)], [0, 1, 0], [-sin(r), 0, cos(r)]]
rotated_vertices = vertices @ Ry @ Rx
```

---

### 3.9 Hysteresis in Control Systems

**What is hysteresis?**
A control technique where the activation and deactivation thresholds are different, creating a "deadband" that prevents rapid switching (flutter) in noisy or transitional conditions.

**In NGSC (solar array control):**

```
        RETRACT                  DEADBAND                  DEPLOY
    ◄──────────────┤           (no change)          ├──────────────►
        < 400                   400 – 600                  > 600

    [────────────────────────────────────────────────────────────]
    0                                                         1023
                        LDR ADC Reading
```

**Without hysteresis:** If the threshold were a single value (e.g., 500), flickering ambient light would cause the solar array to rapidly deploy/retract/deploy/retract — causing mechanical wear and electrical noise.

**With hysteresis:** The 200-point deadband (400–600) means:
- Once deployed (light > 600), it stays deployed until light drops below 400
- Once retracted (light < 400), it stays retracted until light exceeds 600
- In the 400–600 zone, the previous state is maintained

**This is implemented identically in three places:**
1. `satellite.ino` (original firmware) — thresholds: 600/400
2. `satellite_new.ino` (improved firmware) — thresholds: 600/400
3. `sim_satellite.py` (simulator) — thresholds: 400/300

---

### 3.10 Protocol Framing (TELEM: Prefix)

**Problem:** Serial communication is a raw byte stream. There's no built-in concept of "message boundaries." Partial reads or buffer overflows can deliver incomplete JSON, causing `json.JSONDecodeError`.

**Solution:** A simple framing protocol:
```
TELEM:{"pitch":12.5,"roll":-3.2,"light":743,...}\n
│      │                                        │
│      └── Payload (valid JSON)                 └── Newline terminator
└── Frame prefix (identifies packet type)
```

**Why this works:**
1. `Serial.println()` on the Arduino appends `\r\n`
2. Python's `serial.readline()` reads until `\n`, guaranteeing a complete line
3. The `TELEM:` prefix lets the parser ignore debug prints, boot messages, and other serial noise
4. `_handle_telemetry_line()` checks `line.startswith("TELEM:")` before attempting JSON parse

**This is effectively a simplified version of SLIP/COBS framing used in embedded systems.**

---

## 4. Tech Stack — Deep Theory

### 4.1 Python & CPython Runtime

**Why Python for a ground station?**
- Rapid prototyping across three domains (web, science, hardware)
- Rich ecosystem: Skyfield for orbital math, PySerial for hardware, FastAPI for APIs
- Acceptable performance for 10Hz data rates (CPython handles this easily)

**Version constraint:** Python 3.8+ is required for the `str | None` union type syntax used in `backend.py:140`.

**NumPy version pinning:** `numpy>=1.26.0,<2.0.0` — NumPy 2.0 introduced breaking C API changes that affected Skyfield and SciPy. This is a real-world dependency management decision.

---

### 4.2 FastAPI & ASGI (Uvicorn)

**FastAPI** is a modern Python web framework based on ASGI (Asynchronous Server Gateway Interface), using Pydantic for request/response validation and automatic OpenAPI documentation.

**Key concepts used in NGSC:**

| Concept | Usage |
|---------|-------|
| `@app.get("/status")` | Endpoint decorator — maps HTTP GET to Python function |
| `@app.post("/command")` | Maps HTTP POST with JSON body |
| `BaseModel` (Pydantic) | `Command(action: str)` — validates and deserializes request body |
| `@app.on_event("shutdown")` | Lifecycle hook for graceful cleanup |
| Uvicorn ASGI server | Runs the FastAPI app with `--reload` for development |

**Why FastAPI over Flask?**
- Automatic request validation via Pydantic (no manual `request.json.get()`)
- Automatic OpenAPI/Swagger docs at `/docs`
- Native async support (though NGSC uses sync handlers with threading)
- Better performance under concurrent requests

**Concurrency model in NGSC:**
FastAPI with Uvicorn runs in a single process. The serial listener is a standard `threading.Thread`. HTTP request handlers are called from Uvicorn's event loop but execute synchronously (they acquire locks and return quickly).

---

### 4.3 Streamlit — Reactive UI Framework

**Streamlit's execution model:**
Every user interaction (button click, slider move, text input) **re-runs the entire Python script** from top to bottom. This is fundamentally different from traditional web frameworks.

**Implications for NGSC:**
- Expensive initializations must be cached: `@st.cache_resource` on `get_system()`
- Mutable state must use `st.session_state` (survives re-runs)
- Real-time updates require `@st.fragment(run_every="0.5s")` — a partial re-render mechanism

**Key Streamlit APIs used:**

| API | Purpose in NGSC |
|-----|-----------------|
| `@st.cache_resource` | Cache OrbitEngine, RadioCore (created once, reused across re-runs) |
| `@st.fragment(run_every="0.5s")` | 2Hz live panel without full page re-run |
| `st.session_state` | Persist tracking state, logger handles, loop counters |
| `st.plotly_chart()` | Render Plotly figures (radar, map, 3D cube) |
| `st.metric()` | Display key-value pairs with delta indicators |
| `st.toggle()` / `st.button()` | User input elements |
| `st.sidebar` | Navigation and satellite selection |
| `st.set_page_config(layout="wide")` | Full-width layout |

**`@st.fragment` is critical:**
Without it, the entire page (sidebar, all modules, all charts) would re-render 2× per second. With `@st.fragment`, only the decorated function re-runs at the specified interval, leaving the rest of the page static. This is what makes the 2Hz live telemetry panel performant.

---

### 4.4 Skyfield — Astronomical Computation

**What Skyfield does:**
A high-precision astronomical library that can compute the position of any celestial body (stars, planets, satellites) as seen from any point on Earth.

**Key classes used:**

| Class | Purpose |
|-------|---------|
| `load.timescale()` | Creates a time system that handles UTC, TDB, and leap seconds |
| `Topos(lat, lon, elevation)` | Defines the ground station as a point on Earth's surface |
| `EarthSatellite(line1, line2)` | Creates a satellite object from TLE data |
| `satellite.at(time)` | Computes the satellite's geocentric position at a specific time |
| `(satellite - station).at(time).altaz()` | Computes azimuth, elevation, and range relative to the observer |
| `satellite.find_events()` | Finds rise/set/culmination events over a time span |
| `geocentric.subpoint()` | Converts geocentric position to latitude/longitude (sub-satellite point) |

**Skyfield vs. Ephem vs. poliastro:**
Skyfield was chosen because it provides the simplest API for TLE-based satellite tracking, handles time systems correctly (leap seconds, UT1), and integrates SGP4 seamlessly.

---

### 4.5 Plotly — Interactive Visualization

**Three Plotly chart types used:**

| Chart | Module | Purpose |
|-------|--------|---------|
| `go.Scatterpolar` | Mission Control | Polar radar showing satellite azimuth/elevation |
| `go.Scattergeo` | Mission Control | World map with orbital ground track |
| `go.Mesh3d` | HIL Digital Twin | 3D rotating cube representing satellite attitude |

**The 3D cube rendering is the most complex:**
- 8 vertices of a unit cube are defined as a NumPy array
- Rotation matrices are constructed from pitch and roll angles
- Matrix multiplication (`vertices @ Ry @ Rx`) produces rotated vertex positions
- 12 triangular faces are specified via `i`, `j`, `k` index arrays
- Plotly renders this as a WebGL mesh in the browser

---

### 4.6 PySerial — Serial Communication

**Serial fundamentals:**
- **Baud rate:** 115200 bits/second (standard for Arduino USB)
- **Protocol:** 8N1 (8 data bits, No parity, 1 stop bit) — the default
- **Flow control:** None
- **Encoding:** UTF-8

**Key PySerial APIs in NGSC:**

| Method | Usage |
|--------|-------|
| `serial.Serial(port, baud, timeout=1)` | Open COM port with 1-second read timeout |
| `serial_port.readline()` | Read until newline (blocking, respects timeout) |
| `serial_port.write(encoded)` | Write bytes to the serial port |
| `serial_port.flush()` | Wait until all output bytes are transmitted |
| `serial_port.in_waiting` | Number of bytes in the input buffer (non-blocking check) |
| `serial_port.is_open` | Check if the port is still valid |

**Windows COM port exclusivity:**
Windows treats COM ports as exclusive resources — only one process can open a COM port at a time. This is why the README emphasizes closing the Arduino Serial Monitor before starting the Python backend. NGSC's error handling specifically warns about this scenario.

---

### 4.7 Construct — Declarative Binary Parsing

**What `construct` does:**
Instead of manually slicing byte arrays with `struct.unpack()`, `construct` lets you declare a packet schema and parse/build binary data declaratively.

**NGSC's telemetry packet schema:**
```python
TelemetryPacket = Struct(
    "sync_word" / Const(b"\x1A\xCF\xFC\x1D"),  # 4 bytes — magic number
    "battery_voltage" / Int16ub,                  # 2 bytes — unsigned 16-bit big-endian
    "panel_current" / Int16ub,                    # 2 bytes
    "internal_temp" / Int8ub,                     # 1 byte — unsigned 8-bit
    "status_msg" / PaddedString(10, "utf-8")      # 10 bytes — zero-padded UTF-8
)
```

**Total packet size:** 4 + 2 + 2 + 1 + 10 = **19 bytes**

**Sync word (`\x1A\xCF\xFC\x1D`):**
A magic number that identifies the start of a valid packet. If the parser receives noise or a corrupted stream, the sync word mismatch causes an immediate parse failure — preventing garbage data from being interpreted as valid telemetry. This pattern is standard in aerospace protocols (CCSDS uses `0x1ACFFC1D` as well).

---

### 4.8 NumPy — Numerical Computing

**Usage in NGSC:**
NumPy is used in `hil_mode.py` for 3D rotation matrix operations:

```python
# 8 vertices × 3 coordinates = (8, 3) array
vertices = np.array([[-1,-1,-1], [1,-1,-1], ...]) * 0.5

# 3×3 rotation matrices
Rx = np.array([[1,0,0], [0,cos(p),-sin(p)], [0,sin(p),cos(p)]])
Ry = np.array([[cos(r),0,sin(r)], [0,1,0], [-sin(r),0,cos(r)]])

# Matrix multiplication: rotate all 8 vertices at once
rotated = vertices @ Ry @ Rx  # (8,3) @ (3,3) @ (3,3) = (8,3)
```

**Why NumPy over manual loops?**
- `@` operator performs matrix multiplication in optimized C code (BLAS/LAPACK)
- Vectorized operation on all 8 vertices simultaneously
- Clean, readable code that maps directly to the mathematical notation

---

### 4.9 Arduino / ESP8266 Platform

**NodeMCU ESP8266 (ESP-12E) specs:**

| Feature | Value |
|---------|-------|
| CPU | Tensilica L106, 80 MHz (single-core) |
| RAM | 80 KB user-accessible |
| Flash | 4 MB |
| WiFi | 802.11 b/g/n (2.4 GHz) — not used in NGSC |
| GPIO | 11 digital pins |
| ADC | 1 analog pin (A0), 10-bit (0–1023), 1V max |
| Serial | 115200 baud over USB (CH340/CP2102 USB-to-UART) |

**Arduino execution model:**
1. `setup()` runs once at boot — hardware initialization
2. `loop()` runs continuously — the main program loop
3. No operating system — bare-metal execution
4. Cooperative multitasking (no preemptive threads)

---

### 4.10 I2C Protocol

**Inter-Integrated Circuit (I2C)** is a synchronous, multi-master, multi-slave serial protocol used for short-distance communication between chips.

**In NGSC:**
- **Master:** NodeMCU (ESP8266)
- **Slave:** MPU6050 (address 0x68)
- **Lines:** SDA (data, pin D2) and SCL (clock, pin D1)
- **Speed:** 100 kHz (standard mode, set in `satellite_new.ino`)

**How a read works (from `satellite.ino`):**
```cpp
Wire.beginTransmission(0x68);  // Start talking to device at address 0x68
Wire.write(0x3B);              // Tell it to start at register 0x3B (ACCEL_XOUT_H)
Wire.endTransmission(false);   // Send a repeated START (don't release the bus)
Wire.requestFrom(0x68, 6);     // Read 6 bytes: AcX(2) + AcY(2) + AcZ(2)
```

**Registers being read:**

| Register | Address | Data |
|----------|---------|------|
| ACCEL_XOUT_H | 0x3B | X acceleration, high byte |
| ACCEL_XOUT_L | 0x3C | X acceleration, low byte |
| ACCEL_YOUT_H | 0x3D | Y acceleration, high byte |
| ACCEL_YOUT_L | 0x3E | Y acceleration, low byte |
| ACCEL_ZOUT_H | 0x3F | Z acceleration, high byte |
| ACCEL_ZOUT_L | 0x40 | Z acceleration, low byte |

Each 16-bit value is reconstructed: `int16_t AcX = Wire.read() << 8 | Wire.read();`

---

## 5. Algorithms & Data Structures

### 5.1 SGP4 Orbital Propagator

**Algorithm classification:** Numerical integration with analytical perturbation corrections

**Input:** Six Keplerian elements + epoch time (from TLE)
**Output:** Position and velocity vectors in TEME frame at any requested time

**Computational complexity:** O(1) per position calculation — it's a closed-form analytical model, not an iterative simulation

**Accuracy:** ~1 km position error after 1 day for LEO satellites. Degrades rapidly beyond 3–5 days due to unpredictable atmospheric drag variations.

---

### 5.2 Topocentric Coordinate Transform

**What it does:** Converts a satellite's position from Earth-centered coordinates to coordinates relative to a specific ground observer.

**The chain in Skyfield:**
```
EarthSatellite.at(time)              → Geocentric position (TEME)
(satellite - station).at(time)       → Topocentric position vector
topocentric.altaz()                  → (Altitude/Elevation, Azimuth, Distance)
```

**Internally, this involves:**
1. Computing the satellite's TEME position via SGP4
2. Computing the ground station's ITRF position from WGS84 coordinates
3. Rotating from TEME to ITRF (accounts for Earth's rotation)
4. Subtracting the station vector to get the relative vector
5. Rotating into the local horizon frame (SEZ or ENU)
6. Converting to spherical coordinates (azimuth, elevation, range)

---

### 5.3 3D Rotation Matrices (Euler Angles)

**Rotation around X-axis (pitch):**
```
Rx(θ) = | 1     0       0    |
         | 0   cos(θ)  -sin(θ)|
         | 0   sin(θ)   cos(θ)|
```

**Rotation around Y-axis (roll):**
```
Ry(θ) = | cos(θ)   0   sin(θ)|
         |   0      1     0   |
         |-sin(θ)   0   cos(θ)|
```

**Combined rotation:** `R = Ry × Rx` (applied right-to-left: first pitch, then roll)

**In NGSC (`hil_mode.py`):**
```python
rotated_vertices = vertices @ Ry @ Rx
```
Note: Python's `@` operator performs matrix multiplication. The `vertices` array is shape (8, 3), and each rotation matrix is (3, 3), so the result is (8, 3) — all 8 cube vertices rotated in one operation.

**Gimbal lock caveat:** Euler angles suffer from gimbal lock when pitch approaches ±90°. This is acceptable for NGSC because the MPU6050's accelerometer-only solution already loses accuracy near vertical orientations.

---

### 5.4 Accelerometer-to-Angle Trigonometry

**The math:**
When a 3-axis accelerometer is stationary, it measures only gravity (1g ≈ 9.81 m/s²). The gravity vector projects onto each axis proportionally to the tilt:

```
pitch = -atan2(Ax, √(Ay² + Az²)) × (180/π)
roll  =  atan2(Ay, Az) × (180/π)
```

**Why `atan2` instead of `atan`?**
`atan2(y, x)` returns the correct angle in all four quadrants (-180° to +180°), while `atan(y/x)` only covers -90° to +90° and fails when x = 0 (division by zero).

**Why the `sqrt(Ay² + Az²)` in pitch?**
This accounts for the combined gravitational component perpendicular to the X-axis, providing a more accurate pitch measurement than simply using `atan2(Ax, Az)`, which would be affected by roll.

---

### 5.5 Doppler Shift Calculation

**Formula used in `radio_core.py`:**
```python
corrected_freq = target_freq + doppler_shift
```

**Full physics formula:**
```
f_observed = f_transmitted × (c + v_observer) / (c + v_source)
```

For satellite communications where velocities are much smaller than *c*, the approximation simplifies to:
```
Δf ≈ f × (v_radial / c)
```

**Example:** ISS at 145.8 MHz, approaching at 7.6 km/s:
```
Δf = 145.8 × 10⁶ × (7600 / 3 × 10⁸) = +3,694 Hz ≈ +3.7 kHz
```

---

### 5.6 Voltage Divider (LDR Circuit)

**Circuit:**
```
3.3V ──── LDR ──── A0 ──── 10kΩ ──── GND
```

**The formula:**
```
V_out = V_in × R_fixed / (R_LDR + R_fixed)
```

**How it works:**
- In bright light: LDR resistance drops → more voltage at A0 → higher ADC reading
- In darkness: LDR resistance increases → less voltage at A0 → lower ADC reading
- The 10kΩ resistor provides a reference against which the LDR's variable resistance is measured

**ADC conversion:** NodeMCU maps 0–1V input to 0–1023 digital value (10-bit resolution). The internal voltage divider on the NodeMCU already scales 3.3V to the 1V ADC range.

---

### 5.7 Linear Calibration (y = mx + c)

**In `decoder.py`, raw sensor values are converted to engineering units:**
```python
voltage = raw_voltage * 0.01    # Scale factor (m = 0.01)
current = raw_current * 0.001   # Scale factor (m = 0.001)
temp = raw_temp - 20            # Offset (c = -20)
```

This is the standard **transfer function** used in sensor calibration: the raw digital value is linearly mapped to a physical quantity. The scale factors (`0.01`, `0.001`) and offsets (`-20`) are determined during sensor characterization.

---

### 5.8 Value Clamping (Range Validation)

**Implementation in `decoder.py`:**
```python
voltage = max(VOLTAGE_MIN, min(VOLTAGE_MAX, raw_voltage))
```

**This is a defensive programming technique:**
- Clamps values to physically plausible ranges (e.g., battery voltage: 0–15V)
- Prevents corrupt sensor data from propagating through the system
- Logs a warning when clamping occurs (indicates a sensor fault)
- Increments an error counter for diagnostics

---

### 5.9 Sub-Satellite Point Calculation

**What it is:** The point on Earth's surface directly below the satellite (the satellite's "shadow" projected onto the ground).

**In `orbit_engine.py`:**
```python
geocentric = satellite.at(t_vector)    # Compute position at multiple times
subpoint = geocentric.subpoint()       # Project onto Earth's surface
lat = subpoint.latitude.degrees        # Array of latitudes
lon = subpoint.longitude.degrees       # Array of longitudes
```

**Used for:** Drawing the orbital ground track on the 2D world map. NGSC computes 180 minutes of sub-satellite points at 60-second intervals, spanning ±90 minutes from the current time.

---

### 5.10 Fuzzy String Matching (Satellite Lookup)

**`orbit_engine.py` implements a three-tier satellite name resolution:**

```python
# Tier 1: Exact match
if name in self.satellites:
    return self.satellites[name]

# Tier 2: Whitespace-stripped match
for key in self.satellites.keys():
    if key.strip() == name.strip():
        return self.satellites[key]

# Tier 3: Substring match (case-insensitive)
for key in self.satellites.keys():
    if name.upper() in key.strip().upper():
        return self.satellites[key]
```

**Why three tiers?**
TLE files from different sources have inconsistent whitespace padding and naming conventions. The ISS might appear as `"ISS (ZARYA)"`, `"ISS (ZARYA)  "`, or just be searched as `"ISS"`. The tiered approach ensures maximum flexibility without false positives.

---

## 6. Concurrency & Thread Safety

### 6.1 Threading Model

**NGSC's concurrency architecture:**

```
Main Thread (Uvicorn event loop)
├── Handles HTTP requests (GET /status, POST /command)
└── Started by: uvicorn src.backend:app

Daemon Thread (Serial listener)
├── Reads serial data at 10Hz
├── Updates ground_state (thread-safe via state_lock)
├── Logs to CSV
└── Started by: threading.Thread(target=serial_listener, daemon=True).start()
```

**Two critical shared resources:**
1. `ground_state` dictionary — read by HTTP handlers, written by serial thread
2. `serial_port` object — read by serial thread, written to by command handler

---

### 6.2 Lock Granularity — Why Two Locks?

**`state_lock`** protects `ground_state` (dict reads/writes — microsecond operations):
- **Writers:** `_apply_telemetry_packet()` (serial thread), `send_command()` (HTTP thread, sim only)
- **Readers:** `get_status()` (HTTP thread)

**`serial_io_lock`** protects `serial_port` (I/O operations — millisecond operations):
- **Readers/Writers:** `_read_serial_line()` (serial thread), `send_command()` (HTTP thread)

**Why not a single lock?**
If one lock protected both resources, reading telemetry at 10Hz would block command sends, and vice versa. With two locks:
- `state_lock` is held for microseconds (dict update)
- `serial_io_lock` is held for milliseconds (I/O)
- Neither blocks the other
- This is an example of **fine-grained locking** — maximizing concurrency by minimizing critical section overlap

---

### 6.3 Daemon Threads

**What they are:** Threads that are automatically killed when the main thread exits. Set via `daemon=True`.

**Why used in NGSC:**
The serial listener thread should not prevent the process from shutting down. If the main Uvicorn process receives SIGTERM, daemon threads are terminated immediately — no manual join() needed.

**Caveat:** Daemon threads can be killed mid-write, potentially corrupting output. NGSC mitigates this with `flush()` after every CSV write and a proper `shutdown_event()` handler.

---

### 6.4 threading.Event for Graceful Shutdown

**`_shutdown_event = threading.Event()`** is used throughout `backend.py`:

```python
# In the serial listener loop:
while not _shutdown_event.is_set():
    ...

# In the backoff sleep (interruptible!):
def _wait_for_reconnect(delay_s):
    if _shutdown_event.wait(delay_s):  # Returns True if event is set
        return delay_s
    return min(delay_s * 2, MAX_DELAY)

# On shutdown:
@app.on_event("shutdown")
def shutdown_event():
    _shutdown_event.set()    # Wakes up all waiting threads immediately
    _close_serial_port()
```

**Key advantage over `time.sleep()`:** `Event.wait()` returns immediately when the event is set, allowing clean shutdown without waiting for the full sleep duration. `time.sleep()` would block for the entire duration, delaying process exit.

---

### 6.5 The GIL and Why It Matters Here

**The Global Interpreter Lock (GIL)** prevents multiple threads from executing Python bytecode simultaneously. However, the GIL is **released during I/O operations** (file reads, socket operations, serial communication).

**Why NGSC's threading still works:**
- The serial listener spends most of its time in `serial_port.readline()` — a blocking I/O call that releases the GIL
- The HTTP handler spends most of its time in Uvicorn's event loop — also I/O-bound
- The locks (`state_lock`, `serial_io_lock`) protect dict updates that are already atomic at the bytecode level, but the locks add explicit correctness guarantees
- This is a classic I/O-bound threading use case where the GIL is not a bottleneck

---

## 7. Networking & Communication Protocols

### 7.1 Serial UART (RS-232 / USB CDC)

**Used for:** Hardware ↔ Backend communication (NodeMCU ↔ Python)

**Parameters in NGSC:**
| Parameter | Value |
|-----------|-------|
| Baud rate | 115200 bps |
| Data bits | 8 |
| Parity | None |
| Stop bits | 1 |
| Flow control | None |
| Encoding | UTF-8 |

**Why 115200 baud?**
It's the standard Arduino Serial baud rate. At 115200 bps with 8N1 encoding (10 bits per byte including start/stop), the effective throughput is ~11.5 KB/s. A typical NGSC telemetry packet is ~100 bytes, so 10Hz transmission uses only ~1 KB/s — well within capacity.

---

### 7.2 UDP Datagrams

**Used for:** Software simulator (`sim_satellite.py`) → UDP bridge (`udp_bridge.py`)

**Configuration:**
```python
TELEM_IP = "127.0.0.1"
TELEM_PORT = 4210    # Telemetry downlink
COMMAND_PORT = 4220  # Command uplink
BUFFER_SIZE = 1024
```

**Why UDP over TCP?**
- **No connection setup:** UDP is connectionless — the simulator can start sending immediately without a handshake
- **Acceptable packet loss:** For real-time telemetry, a dropped packet is preferable to a delayed one. The next packet will arrive in 100ms anyway
- **Lower latency:** No TCP congestion control, window sizing, or ACK waiting
- **Simulates real radio:** In actual satellite communication, the downlink is one-way broadcast — there's no TCP handshake with a satellite

---

### 7.3 HTTP/REST API

**Used for:** Backend ↔ Dashboard communication

**Endpoints:**

| Method | Path | Request Body | Response | Purpose |
|--------|------|-------------|----------|---------|
| GET | `/status` | — | `{connected, telemetry: {pitch, roll, light, status}}` | Poll current state |
| POST | `/command` | `{action: "LED_ON"}` | `{status: "success"}` | Send uplink command |

**Polling rate:** 2Hz (every 0.5 seconds, set by `@st.fragment(run_every="0.5s")`)

**Timeout:** 300ms (`timeout=0.3` in `requests.get()`) — prevents the UI from hanging if the backend is slow or unreachable.

---

### 7.4 Protocol Comparison Table

| Property | Serial UART | UDP | HTTP/REST |
|----------|-------------|-----|-----------|
| **Connection type** | Point-to-point, exclusive | Connectionless, multicast-capable | Request-response, connection-pooled |
| **Reliability** | Hardware-level (USB) | Unreliable (best-effort) | TCP-reliable (underneath) |
| **Latency** | <1ms | <1ms (localhost) | 1–50ms |
| **Ordering** | Guaranteed (FIFO) | Not guaranteed | Guaranteed (per connection) |
| **Use in NGSC** | NodeMCU ↔ Backend | Simulator ↔ Bridge | Backend ↔ Dashboard |

---

## 8. Embedded Systems & IoT Concepts

### 8.1 NodeMCU ESP8266 Architecture

**Key hardware features relevant to NGSC:**
- **Single-core processor** — no parallel execution. The `loop()` function must complete quickly to maintain 10Hz telemetry rate
- **Single ADC pin (A0)** — can only read one analog sensor. The LDR gets the only analog channel
- **3.3V logic** — the MPU6050 must be powered at 3.3V, not 5V (damage risk)
- **USB-to-UART chip** (CH340 or CP2102) — converts USB to Serial UART for Python communication
- **Non-volatile flash** — stores the firmware; survives power cycles

---

### 8.2 MPU6050 IMU — 6-Axis Inertial Measurement

**What it contains:**
- 3-axis accelerometer (measures gravitational force → tilt angles)
- 3-axis gyroscope (measures angular velocity → rotation rate)
- Built-in temperature sensor
- Built-in Digital Motion Processor (DMP) — not used in NGSC

**Accelerometer range:** ±2g (set in `satellite_new.ino` via `mpu.setAccelerometerRange(MPU6050_RANGE_2_G)`)

**Low-pass filter:** 21 Hz bandwidth (`mpu.setFilterBandwidth(MPU6050_BAND_21_HZ)`) — filters out vibration noise above 21 Hz while passing through attitude changes (which are slower)

---

### 8.3 Analog-to-Digital Conversion (ADC)

**NodeMCU's ADC:**
- **Resolution:** 10 bits (0–1023)
- **Input range:** 0–1V (internal voltage divider scales 3.3V down)
- **Single channel:** Only pin A0

**LDR reading interpretation:**
```
0    = Total darkness (maximum LDR resistance)
~200 = Full shadow
~600 = Threshold for solar deploy
~950 = Bright desk light
1023 = Maximum light (minimum LDR resistance)
```

---

### 8.4 GPIO & Digital Output

**LED control circuit:**
```
D5 (GPIO14) → 220Ω → LED anode → LED cathode → GND
```

**Current calculation:**
```
I = (V_out - V_led) / R = (3.3V - 2.0V) / 220Ω ≈ 5.9 mA
```
This is within the ESP8266's GPIO current limit (12 mA per pin).

---

### 8.5 I2C Bus Recovery

**Problem:** If the MPU6050 loses power mid-I2C-transaction, the SDA line can become stuck LOW (the slave was in the middle of transmitting a 0 bit). The bus is now deadlocked — the master can't send a START condition.

**Solution in `satellite_new.ino`:**
```cpp
// Bus-clearing hack for stuck I2C lines
pinMode(D1, OUTPUT);  // D1 = SCL
for (int i = 0; i < 10; i++) {
    digitalWrite(D1, HIGH);
    delay(5);
    digitalWrite(D1, LOW);
    delay(5);
}
```

**How it works:** By manually toggling the SCL (clock) line 10 times, the stuck slave eventually clocks out its remaining bits and releases SDA, allowing normal I2C communication to resume.

---

### 8.6 Staggered Boot Sequence

**Problem:** Simultaneously initializing the I2C bus and the GPIO pins causes a voltage inrush that can crash the MPU6050 sensor on startup.

**Solution in `satellite_new.ino`:**
```cpp
Wire.begin(D2, D1);    // Step 1: Initialize I2C
Wire.setClock(100000);
delay(2000);            // Step 2: Wait 2 seconds
pinMode(LED_PIN, OUTPUT);  // Step 3: Initialize GPIO
```

The 2-second delay allows the MPU6050 to stabilize before additional current draw from the LED circuit.

---

## 9. Data Engineering & Persistence

### 9.1 CSV as a Flight Recorder ("Black Box")

**Why CSV?**
- Human-readable without special tools
- Directly importable into Excel, Pandas, MATLAB
- Append-only writes are naturally crash-safe
- Small file sizes for 10Hz data (each row ≈ 80 bytes → ~2.8 MB/hour)

**Two log directories:**

| Path | Source | Columns |
|------|--------|---------|
| `data/telemetry/hil_side/` | Hardware sessions | timestamp, pitch, roll, yaw, light, led_status, solar_status, mode |
| `data/telemetry/mission_control/` | Orbital tracking | timestamp, azimuth, elevation, range, doppler, voltage, temp |

**File naming:** `{satellite_name}_{YYYYMMDD_HHMMSS}.csv` — ensures unique filenames and chronological sorting.

---

### 9.2 Write-Through Flush Strategy

**In both `backend.py` and `data_manager.py`:**
```python
self._writer.writerow([...])
self._file.flush()  # Force OS to write to disk NOW
```

**Why `flush()` after every row?**
Without it, Python's `csv.writer` buffers data in memory. If the process crashes, the buffered data is lost. With `flush()`, data survives crashes — at most one row (100ms of data) can be lost.

**Trade-off:** `flush()` on every write is slower than buffered writing, but at 10Hz (100 writes/second), the overhead is negligible on modern SSDs.

---

### 9.3 TLE File Caching

**`orbit_engine.py` caching logic:**
```python
if not os.path.exists(self.tle_file):
    download()  # File doesn't exist
elif time.time() - os.path.getmtime(self.tle_file) > 86400:
    download()  # File is older than 24 hours
else:
    use_cached()  # File is fresh
```

**Why 24-hour refresh?**
- TLE accuracy degrades over days due to atmospheric drag variations
- CelesTrak updates TLEs multiple times per day
- 24 hours is a practical balance between freshness and avoiding excessive network requests
- If the download fails, the stale file is used as a fallback (graceful degradation)

---

## 10. Error Handling & Fault Tolerance

**Complete failure matrix:**

| Failure Scenario | Component | Detection | Recovery | Recovery Time |
|---|---|---|---|---|
| COM port busy (Arduino IDE open) | `_open_serial_port()` | `SerialException` | Exponential backoff retry | 1s–30s |
| Serial cable unplugged mid-session | `_serial_read_loop()` | `SerialException` | Close port, mark disconnected, retry | 1s–30s |
| Malformed JSON from NodeMCU | `_handle_telemetry_line()` | `json.JSONDecodeError` | Log warning, skip packet, continue | Immediate |
| Corrupted bytes in serial buffer | `_serial_read_loop()` | `UnicodeDecodeError` | Skip packet, continue | Immediate |
| Backend HTTP unreachable | `get_backend_data()` | `RequestException` | Return cached data (up to 3 failures) | Immediate |
| After 3 consecutive HTTP failures | `get_backend_data()` | `failed_pings > 3` | Show "BACKEND OFFLINE" error | Manual restart |
| TLE download timeout | `_update_tles()` | `requests.Timeout` | Use cached TLE file | Immediate |
| TLE download connection error | `_update_tles()` | `ConnectionError` | 3x retry with backoff, use cache | 1–3s per retry |
| IMU sensor power loss (I2C freeze) | `satellite_new.ino` | `initMpu()` returns false | Degraded mode + 5s retry | 5s |
| I2C bus lockup (SDA stuck) | `satellite_new.ino setup()` | — | SCL bus-clearing hack (10 pulses) | 100ms |
| RTL-SDR dongle missing | `RadioCore.__init__()` | `ImportError` or `Exception` | Mock mode (print to console) | Immediate |
| Out-of-range telemetry values | `decoder.parse_frame()` | Value > MAX or < MIN | Clamp to safe range, log warning | Immediate |
| CSV log file write failure | `_log_telemetry_packet()` | `Exception` | Print error, skip row, continue | Immediate |

---

## 11. Testing Strategy

**NGSC uses manual integration tests and debug scripts:**

| File | Purpose | How to Run |
|------|---------|------------|
| `test_bridge.py` | Tests UDP bridge listener — starts the listener and prints received data | `python test_bridge.py` |
| `test_telemetry.py` | Tests raw UDP packet reception — binds to port 4210 and dumps packets | `python test_telemetry.py` |
| `test_fire.py` | Tests raw UDP command fire to a specific IP | `python test_fire.py` |
| `tests/test_decoder.py` | Placeholder for decoder unit tests | (empty) |
| `tests/test_orbit.py` | Placeholder for orbital math unit tests | (empty) |

**Testing philosophy:**
The project prioritizes end-to-end integration testing (run all three services, verify data flows) over unit testing. This is appropriate for a hardware-integrated project where the most critical bugs occur at system boundaries (serial communication, JSON parsing, thread synchronization).

---

## 12. DevOps & Deployment

### Development Container
The `.devcontainer/devcontainer.json` enables one-click GitHub Codespaces deployment:
- Base image: `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`
- Auto-installs all dependencies from `requirements.txt`
- Auto-starts Streamlit on port 8501
- Configures port forwarding for the dashboard

### Cloud Deployment (Render)
The backend detects cloud deployment via environment variables:
```python
SIMULATION_MODE = os.getenv("RENDER") is not None or os.getenv("SIMULATION_MODE") == "True"
```
In simulation mode, the serial listener generates synthetic sin/cos telemetry instead of reading from a COM port — enabling the system to run without any hardware.

### Environment Variables

| Variable | Purpose | Default |
|----------|---------|---------|
| `RENDER` | Detected automatically on Render.com | — |
| `SIMULATION_MODE` | Force simulation mode | `"False"` |
| `ARDUINO_COM_PORT` | Override COM port | `"COM7"` |
| `API_URL` | Backend URL for the frontend | `"http://127.0.0.1:8000"` |

---

## 13. Interview Questions & Answers — By Topic

### 13.1 Architecture & Design

---

**Q1: Explain the architecture of your ground station project.**

**A:** NGSC uses a three-tier decoupled architecture. The Space Segment is a NodeMCU ESP8266 with sensors that transmits telemetry at 10Hz over Serial USB. The Ground Backend is a FastAPI application that ingests serial data in a background thread and exposes it via REST endpoints. The Mission UI is a Streamlit dashboard that polls the backend at 2Hz and renders real-time visualizations. The key architectural insight is that serial I/O is blocking and synchronous, while the web UI needs to be responsive and non-blocking — the FastAPI broker bridges these two incompatible I/O models.

---

**Q2: Why didn't you use WebSockets instead of HTTP polling?**

**A:** Streamlit's execution model re-runs the entire script on every interaction, which isn't naturally compatible with persistent WebSocket connections. The `@st.fragment(run_every="0.5s")` decorator provides 2Hz polling with minimal code complexity. At 500ms intervals, the perceived latency (250ms average) is acceptable for human-observed telemetry. The README roadmap includes WebSocket migration as a future improvement for sub-100ms refresh rates, likely using a custom Streamlit component or migrating to a different frontend framework.

---

**Q3: What is the Data Broker pattern, and how did you implement it?**

**A:** The Data Broker pattern introduces a middleware component that decouples data producers from data consumers. In NGSC, the FastAPI backend is the broker: it ingests telemetry from the serial port (producer) and serves it to the Streamlit dashboard (consumer) via HTTP. The `ground_state` dictionary acts as the shared data store. Neither the hardware nor the UI needs to know about the other's protocol, timing, or failure modes — they both just talk to the broker.

---

**Q4: How does your system handle switching between simulation and real hardware?**

**A:** The backend detects `SIMULATION_MODE` via environment variables (`RENDER` or `SIMULATION_MODE`). In simulation mode, the serial listener thread runs `simulated_telemetry_loop()` instead of attempting to open a COM port — generating synthetic sin/cos telemetry at 10Hz. The command handler directly mutates `ground_state` instead of writing to serial. This allows identical frontend code to work in both modes without any UI-level conditional logic.

---

**Q5: How is the Digital Twin pattern implemented in your project?**

**A:** The Digital Twin manifests as a 3D Plotly Mesh3d cube in the browser that mirrors the physical orientation of the NodeMCU on the desk. The MPU6050 accelerometer measures gravity-projected pitch and roll on the microcontroller. These angles travel through Serial → FastAPI → HTTP → Streamlit. The `create_3d_sat_fig()` function constructs 3×3 rotation matrices from the angles, multiplies them against 8 cube vertex coordinates using NumPy matrix operations (`vertices @ Ry @ Rx`), and renders the result as a 3D mesh. The update cycle is: physical sensor at 10Hz → backend processing → frontend render at 2Hz.

---

### 13.2 Concurrency & Threading

---

**Q6: How do you handle thread safety in your system?**

**A:** I use two separate `threading.Lock()` objects with fine-grained locking. `state_lock` protects the `ground_state` dictionary (microsecond-duration holds for dict reads/writes). `serial_io_lock` protects the serial port object (millisecond-duration holds for I/O operations). Using two locks instead of one prevents the telemetry read path from blocking the command write path. Both resources have clearly defined writers and readers, and locks are always acquired in the same order to prevent deadlocks.

---

**Q7: Why use `threading.Event` instead of `time.sleep` for backoff delays?**

**A:** `time.sleep(30)` is not interruptible — if the process receives a shutdown signal during a 30-second sleep, it must wait the full duration before exiting. `threading.Event.wait(30)` returns immediately when `_shutdown_event.set()` is called, enabling graceful sub-second shutdown. This is critical for the serial listener thread, which might be in the middle of a 30-second backoff delay when the process receives SIGTERM.

---

**Q8: Does the GIL affect your system's performance?**

**A:** No, because NGSC is I/O-bound, not CPU-bound. The GIL is released during all I/O operations — serial reads, socket operations, HTTP requests. The serial listener thread spends most of its time blocked in `serial_port.readline()` (waiting for hardware data), during which the GIL is free for the HTTP handler thread. The only GIL-contended operations are the dict updates to `ground_state`, which take microseconds. If the system were CPU-bound (e.g., real-time signal processing), I would use `multiprocessing` instead.

---

**Q9: What is a daemon thread, and why do you use one?**

**A:** A daemon thread is automatically killed when all non-daemon threads exit. I set the serial listener thread as `daemon=True` so that when Uvicorn's main thread shuts down, the serial thread doesn't prevent the process from exiting. Without `daemon=True`, a background thread performing a blocking `readline()` could keep the process alive indefinitely. The trade-off is that daemon threads can be killed mid-operation — which is why I also implement graceful shutdown via `_shutdown_event` as a belt-and-suspenders approach.

---

### 13.3 Networking & Protocols

---

**Q10: Why did you choose UDP for the simulator instead of TCP?**

**A:** UDP is a better model for satellite telemetry. Real satellite downlinks are one-way broadcasts — there's no TCP handshake with a satellite in orbit. UDP's connectionless nature means the simulator can start transmitting immediately without waiting for a listener. If a packet is lost, the next one arrives in 100ms — there's no value in retransmitting stale telemetry. TCP's reliability guarantees (ordering, retransmission) would add latency and complexity without benefit for real-time sensor data.

---

**Q11: Explain the telemetry packet framing protocol.**

**A:** Each telemetry packet follows the format: `TELEM:{json}\n`. The `TELEM:` prefix serves as a frame identifier — the parser checks `line.startswith("TELEM:")` before attempting JSON decode, which filters out Arduino boot messages, debug prints, and serial noise. The newline (`\n`) serves as the frame terminator — Python's `serial.readline()` reads until `\n`, guaranteeing a complete, parseable message. This simple framing prevents `json.JSONDecodeError` crashes from partial reads. It's a simplified version of SLIP/COBS framing used in professional embedded protocols.

---

**Q12: How does the system handle COM port access conflicts on Windows?**

**A:** Windows treats COM ports as exclusive resources — only one process can open a port at a time. If the Arduino IDE Serial Monitor is open, `serial.Serial()` raises `SerialException: Access Denied`. The backend handles this with exponential backoff: it retries opening the port at 1s, 2s, 4s, 8s, 16s, 30s intervals (capped at 30s). The error message explicitly warns: "Is the Arduino IDE Serial Monitor open? IT MUST BE CLOSED!" This design means the backend can be started before or after the hardware is connected — it will eventually connect when the port becomes available.

---

### 13.4 Embedded Systems & IoT

---

**Q13: How does the MPU6050 calculate pitch and roll?**

**A:** The MPU6050 accelerometer measures gravitational acceleration along three axes. When the sensor is tilted, gravity projects differently onto X, Y, and Z. The firmware uses trigonometry: `pitch = -atan2(Ax, sqrt(Ay² + Az²)) × 180/π` and `roll = atan2(Ay, Az) × 180/π`. The `atan2` function is used instead of `atan` because it correctly handles all four quadrants and avoids division-by-zero. The `sqrt(Ay² + Az²)` in the pitch formula accounts for roll influence, providing a more accurate pitch measurement.

---

**Q14: Why can't the MPU6050 measure yaw?**

**A:** Yaw is rotation around the vertical axis (Z-axis when the sensor is horizontal). The accelerometer measures gravity, which is a purely vertical force — it has no horizontal component that would change with yaw rotation. You can rotate the sensor 360° around the Z-axis while perfectly level, and the accelerometer readings won't change. Measuring yaw requires either a magnetometer (which detects Earth's magnetic field direction) or integrating gyroscope data over time (which accumulates drift). The roadmap includes adding an HMC5883L magnetometer or upgrading to an MPU9250 (which includes one).

---

**Q15: Explain the hysteresis logic in the solar array control.**

**A:** Hysteresis uses different thresholds for activation and deactivation. The solar array deploys when light exceeds 600 (ADC units) and retracts when it drops below 400. The 200-unit deadband (400–600) prevents flutter — without it, if the threshold were a single value like 500, flickering ambient light would cause rapid deploy/retract cycles, wasting energy and causing mechanical wear. This is the same principle used in thermostats (a 2°F deadband prevents the heater from cycling on/off every second).

---

**Q16: What is the I2C bus-clearing hack, and why is it needed?**

**A:** If the MPU6050 loses power during an I2C data transfer, the SDA line can get stuck LOW — the slave was transmitting a zero bit and never completed the transaction. The I2C master can't send a START condition (which requires SDA to go HIGH→LOW while SCL is HIGH) because SDA is stuck. The fix: manually toggle the SCL line 10 times. Each clock pulse lets the slave advance through its state machine until it eventually releases SDA. This is a well-documented recovery technique in the I2C specification.

---

**Q17: What is the staggered boot sequence and why is it necessary?**

**A:** In `satellite_new.ino`, the I2C bus is initialized first (`Wire.begin()`), then the system waits 2 seconds before configuring GPIO pins. Without this delay, simultaneously initializing I2C and GPIO causes a voltage inrush — the combined current draw from the MPU6050 starting its internal oscillator and the GPIO pin configuration exceeds what the USB power supply can deliver cleanly, causing the MPU6050 to crash. The 2-second gap lets the I2C peripherals stabilize before additional current is drawn.

---

### 13.5 Algorithms & Math

---

**Q18: How does SGP4 predict satellite positions?**

**A:** SGP4 (Simplified General Perturbations Model 4) is an analytical orbit propagation model. It takes six Keplerian orbital elements from a TLE (inclination, RAAN, eccentricity, argument of perigee, mean anomaly, mean motion) plus an epoch time, and computes the satellite's position and velocity at any future time. It accounts for Earth's oblateness (J2 perturbation), atmospheric drag, and solar/lunar gravitational effects. In NGSC, Skyfield wraps SGP4 and converts the output from TEME coordinates to topocentric azimuth/elevation/range relative to the ground station.

---

**Q19: Explain how the 3D rotation matrices work in your visualization.**

**A:** I construct two 3×3 rotation matrices: Rx for pitch (rotation around X-axis) and Ry for roll (rotation around Y-axis). Each vertex of the 3D cube is represented as a 1×3 vector [x, y, z]. Matrix multiplication `vertex @ Ry @ Rx` applies both rotations in sequence. Using NumPy, I can rotate all 8 vertices simultaneously: `rotated = vertices @ Ry @ Rx` where `vertices` is an 8×3 matrix. The `@` operator performs batch matrix multiplication in optimized C code, which is much faster than a Python loop over each vertex.

---

**Q20: What is a voltage divider and how is the LDR circuit designed?**

**A:** A voltage divider uses two resistors in series to produce an output voltage that's a fraction of the input. In NGSC, the LDR (variable resistance, ~1kΩ in bright light to ~100kΩ in darkness) is connected in series with a fixed 10kΩ resistor between 3.3V and GND. The analog pin A0 measures the voltage at the junction: `V_out = 3.3V × 10kΩ / (R_LDR + 10kΩ)`. In bright light, R_LDR is small → V_out is high → ADC reads near 1023. In darkness, R_LDR is large → V_out is low → ADC reads near 0.

---

### 13.6 Python & Frameworks

---

**Q21: Why did you choose FastAPI over Flask?**

**A:** FastAPI provides automatic request/response validation via Pydantic models (e.g., `Command(action: str)` validates the POST body without manual parsing), automatic OpenAPI documentation at `/docs`, and native async support. Flask would require manual JSON validation, separate documentation tooling, and doesn't provide Pydantic integration out of the box. For a system that processes typed telemetry data and validated commands, FastAPI's schema-driven approach reduces boilerplate and prevents type-related bugs.

---

**Q22: What is `@st.cache_resource` and why is it critical?**

**A:** `@st.cache_resource` is Streamlit's caching decorator for objects that should be created once and shared across all re-runs and sessions. In NGSC, the `get_system()` function creates an `OrbitEngine` (which downloads TLE data and initializes Skyfield), `RadioCore`, `TelemetryDecoder`, and `PassPredictor`. Without caching, every user interaction would re-trigger TLE downloads and re-initialize the orbital library. With `@st.cache_resource`, these objects are created once when the first user loads the page and then served from memory for all subsequent interactions.

---

**Q23: What is `@st.fragment` and how does it solve the real-time update problem?**

**A:** `@st.fragment(run_every="0.5s")` creates a partial re-render zone. Without it, updating the live telemetry panel would require re-running the entire Streamlit script (including sidebar, routing, initialization), which would cause visible flickering and waste CPU. With `@st.fragment`, only the decorated function re-executes at 2Hz. The rest of the page — sidebar, static controls, header — remains untouched. This is how the system achieves smooth real-time updates without the performance penalty of full-page re-rendering.

---

**Q24: Why do you return a copy of the telemetry data in `get_latest_data()`?**

**A:** `return current_telemetry.copy()` creates a shallow copy of the dictionary. Without it, the caller would receive a reference to the shared mutable dictionary. If the caller modifies the returned data (e.g., adds a key, changes a value), it would corrupt the shared state that the background listener thread is also writing to. The copy ensures the caller gets a snapshot that's safe to mutate without affecting the producer thread. This is a fundamental pattern for thread-safe data exchange.

---

### 13.7 System Design & Trade-offs

---

**Q25: What trade-offs did you make in the system design?**

**A:**

| Decision | Trade-off | Justification |
|----------|-----------|---------------|
| HTTP polling (2Hz) vs. WebSocket | Higher latency (~250ms avg) but simpler code | Streamlit doesn't natively support WebSockets |
| Latest-value semantics vs. queue | May miss packets under load, but always shows freshest data | For real-time display, freshness > completeness |
| CSV logging vs. database | No query capability, but human-readable and crash-safe | Post-mission analysis can import to Pandas; no DB setup needed |
| Two locks vs. one lock | Slightly more complex locking discipline, but higher concurrency | Prevents telemetry reads from blocking command writes |
| Daemon threads vs. managed threads | Risk of mid-write kill, but clean process exit | Mitigated by flush() on every write and shutdown event handler |
| Exponential backoff vs. fixed retry | More complex, but prevents resource waste during extended outages | COM port conflicts can last minutes (user needs to close IDE) |

---

**Q26: How would you scale this system for production?**

**A:** Several changes would be needed:

1. **Replace HTTP polling with WebSockets** — reduces latency from 250ms to <50ms
2. **Replace CSV with a time-series database** (InfluxDB or TimescaleDB) — enables real-time queries, retention policies, and multi-user access
3. **Add authentication** — the current system has no auth; add JWT tokens for command authorization
4. **Replace Serial with radio** (LoRa or NRF24L01) — simulates real RF constraints including packet loss and range limits
5. **Add message queuing** (RabbitMQ or Redis Pub/Sub) — decouple backend processing from UI serving
6. **Containerize with Docker Compose** — orchestrate backend, frontend, and database as separate services
7. **Add automated testing** — unit tests for decoder, integration tests for the full data pipeline

---

**Q27: Why did you choose to log telemetry to CSV files instead of a database?**

**A:** Three reasons. First, CSV files are directly readable by any tool — Excel, Pandas, MATLAB, even a text editor — with zero infrastructure setup. Second, append-only CSV writing is naturally crash-safe: each `flush()` call guarantees data persistence. Third, the data volume is modest (~2.8 MB/hour at 10Hz), so storage efficiency isn't a concern. The trade-off is the lack of query capability — you can't easily filter "all packets where pitch > 30°" without loading the entire file. For production, I'd migrate to InfluxDB for time-series queries while keeping CSV export as an option.

---

### 13.8 Debugging & Problem Solving

---

**Q28: How did you debug the I2C bus lockup issue?**

**A:** The symptom was that the MPU6050 would occasionally stop responding after a power glitch. I traced it to the I2C protocol: if the slave is mid-transmission when power is lost, the SDA line stays LOW because the slave's output driver was pulling it down. The master can't issue a new START condition because START requires SDA to transition HIGH→LOW while SCL is HIGH. The fix was the SCL bus-clearing hack in `satellite_new.ino setup()`: toggling SCL 10 times forces the stuck slave to clock through its remaining bits and release SDA. I discovered this technique in the NXP I2C specification (UM10204, Section 3.1.16 "Bus clear").

---

**Q29: How did you handle the `JSONDecodeError` crashes in the serial listener?**

**A:** The initial implementation crashed when receiving partial JSON from the serial buffer (e.g., if `readline()` returned before a complete packet). I solved this with three layers of defense: (1) the Arduino firmware uses `TELEM:` prefix + `\n` terminator framing, ensuring Python's `readline()` always gets a complete line; (2) the parser checks `line.startswith("TELEM:")` before attempting JSON decode, filtering out boot messages and debug prints; (3) the JSON parse is wrapped in a try/except that logs the error and continues processing, so one bad packet never crashes the entire listener.

---

**Q30: What was the voltage inrush crash, and how did you solve it?**

**A:** When initializing the MPU6050 (I2C bus) and the LED GPIO pin simultaneously, the combined current draw exceeded the USB power supply's ability to maintain stable voltage. The MPU6050's internal oscillator requires a surge of current during initialization. Combined with GPIO pin configuration (which briefly draws current even when set LOW), the voltage dipped enough to crash the MPU6050. The fix was a staggered boot sequence: initialize I2C first, wait 2 seconds for stabilization, then configure GPIO pins. This is a common pattern in embedded systems called "power sequencing."

---

### 13.9 Behavioral / Project-Based

---

**Q31: Walk me through what happens when I click the "LED ON" button in the browser.**

**A:** The full chain is: (1) User clicks the LED toggle in the Streamlit UI. (2) The `on_led_toggle()` callback fires, calling `send_command("LED_ON")`. (3) `send_command()` sends an HTTP POST to `http://127.0.0.1:8000/command` with JSON body `{"action": "LED_ON"}`. (4) FastAPI validates the request using the `Command(action: str)` Pydantic model. (5) The `send_command()` handler acquires `serial_io_lock`, encodes `"LED_ON\n"` to UTF-8 bytes, writes them to the serial port, and calls `flush()` to ensure immediate transmission. (6) The NodeMCU's `loop()` function reads `Serial.available()`, gets the string `"LED_ON"`, matches it against command strings, and calls `digitalWrite(D5, HIGH)`. (7) Current flows through the 220Ω resistor and the LED, and it lights up. Total latency: under 500 milliseconds.

---

**Q32: What was the hardest technical challenge in this project?**

**A:** The hardest challenge was making the serial communication reliable across the full stack. Serial is inherently fragile — partial reads, buffer overflows, encoding errors, port contention, cable disconnections. I had to implement: (1) Protocol framing (`TELEM:` prefix + newline terminator) to prevent partial-read JSON crashes. (2) Dual locks (`state_lock` + `serial_io_lock`) to prevent the command handler from corrupting a telemetry read. (3) Exponential backoff reconnection with interruptible sleep for port disconnection recovery. (4) Graceful degradation in the firmware (`satellite_new.ino`) where the IMU can fail and recover independently. (5) The I2C bus-clearing hack for hardware-level faults. Each of these required understanding a different layer of the stack — from I2C electrical signals to Python threading semantics.

---

**Q33: What would you do differently if you started this project over?**

**A:** Three things. First, I'd use WebSockets from the start instead of HTTP polling — the `@st.fragment` approach works but adds perceptible latency. I might use a different frontend framework (React + Three.js) for the 3D visualization instead of fighting Streamlit's re-run model. Second, I'd implement proper unit tests from day one — the `tests/` directory has empty placeholder files, which indicates testing was deferred. Third, I'd use a proper message format like Protocol Buffers or CBOR instead of JSON over serial — binary formats are more bandwidth-efficient and handle encoding issues more gracefully than JSON-over-UTF-8-over-serial.

---

**Q34: How does your project demonstrate full-stack engineering ability?**

**A:** NGSC spans five engineering domains: (1) **Frontend:** Streamlit with Plotly for interactive 3D/2D visualizations, CSS theming, state management. (2) **Backend:** FastAPI REST API with threading, graceful lifecycle management, and structured logging. (3) **Embedded systems:** Arduino C++ firmware with I2C sensor communication, ADC analog reads, GPIO control, and fault tolerance. (4) **Scientific computing:** SGP4 orbital propagation, trigonometric attitude determination, rotation matrices, Doppler physics. (5) **Systems engineering:** Protocol design (framing, packet structure), thread safety (dual-lock concurrency), reliability (exponential backoff, graceful degradation, crash-safe logging), and DevOps (devcontainer, environment-based config, cloud deployment).

---

**Q35: Explain the difference between `satellite.ino` and `satellite_new.ino`.**

**A:** `satellite.ino` is the original firmware that accesses the MPU6050 via raw I2C register reads (`Wire.beginTransmission(0x68); Wire.write(0x3B);`). It's lean but has no fault tolerance — if the MPU6050 disconnects, the firmware hangs in an infinite loop. `satellite_new.ino` replaces raw I2C with the Adafruit MPU6050 library (cleaner API), adds degraded mode operation (continues transmitting LDR and status data with zeroed attitude if the IMU fails), implements auto-recovery (retries IMU initialization every 5 seconds), adds the I2C bus-clearing hack (10 SCL pulses on boot), includes temperature telemetry from the MPU6050's built-in sensor, and uses a staggered boot sequence to prevent voltage inrush crashes. It demonstrates engineering maturity — moving from "it works on my desk" to "it recovers from faults in the field."

---

**Q36: What security considerations exist in your system?**

**A:** The current system has minimal security — it's designed for local development and demonstration. Specific gaps include: (1) No authentication on the FastAPI endpoints — anyone on the network can send commands. (2) No encryption on serial or HTTP traffic. (3) No input validation on command strings (though Pydantic validates the JSON structure). For production, I'd add: JWT-based authentication for the command endpoint, HTTPS for all API traffic, rate limiting to prevent command flooding, and command whitelisting to reject invalid/dangerous commands. The `hil_mode.py` file includes an `X-API-Key` header (`NGSC-SECURE-KEY-2026`), which shows awareness of the need for API security, but it's a static key — not suitable for production.

---

**Q37: How does your system handle the case where the backend starts before the hardware is connected?**

**A:** The `serial_listener()` function has a supervised reconnection loop. On startup, it calls `_open_serial_port()`. If the port doesn't exist yet (hardware not plugged in), it catches the `SerialException`, marks the system as disconnected, and enters exponential backoff — waiting 1s, then 2s, then 4s, up to 30s between retries. When the user plugs in the hardware and closes the Arduino Serial Monitor, the next retry succeeds, the backoff resets to 1s, and the system begins ingesting telemetry. The UI, meanwhile, shows "STALE" or "BACKEND OFFLINE" status — never crashes, never hangs. This design allows the three services (backend, frontend, hardware) to start in any order.

---

**Q38: What is the significance of the sync word `\x1A\xCF\xFC\x1D` in the packet decoder?**

**A:** The sync word `0x1ACFFC1D` is a 4-byte magic number that appears at the start of every valid telemetry packet. Its purpose is packet detection and alignment: when the decoder reads a stream of bytes, it looks for this exact sequence to identify where a packet begins. If noise corrupts the stream, the sync word mismatch causes `Const()` to raise an exception, immediately rejecting the bad data. This value is actually the CCSDS (Consultative Committee for Space Data Systems) standard sync marker — the same one used in real satellite missions. Using a standard sync word demonstrates awareness of aerospace communication protocols.

---

**Q39: How does the throttled map refresh work in Mission Control?**

**A:** The ground track calculation (`orbit_engine.get_ground_track()`) is expensive — it computes 180 minutes of satellite positions at 60-second intervals. Running this every 0.5 seconds (at 2Hz fragment rate) would waste CPU and cause UI lag. The solution is a counter-based throttle: `if loop_counter % MAP_REFRESH_INTERVAL == 0` (where interval = 20), the ground track is recalculated and cached in `st.session_state.mc_cached_track`. On other cycles, the cached track data is reused. This means the map updates every 10 seconds (20 cycles × 0.5s) while the radar and metrics update every 0.5s. This is a simple but effective form of **tiered refresh rates** — high-frequency for fast-changing data (position), low-frequency for slow-changing data (ground track).

---

**Q40: What is the `close_tracking_logger()` function, and why is it idempotent?**

**A:** `close_tracking_logger()` is a standalone function that safely closes a `DataManager` instance's file handle. It's idempotent (safe to call multiple times) because it checks `if logger is not None` before calling `logger.close()`, and `close()` itself checks `if self._file` before attempting to close. This matters because Streamlit's re-run model can trigger cleanup code multiple times — when the user switches modules, when they deselect tracking, or when the session expires. Without idempotency, double-close would raise an `OSError`.

---

## Quick Reference: Key Numbers

| Metric | Value | Source |
|--------|-------|--------|
| Hardware telemetry rate | 10 Hz (100ms interval) | `satellite_new.ino` `TELEMETRY_INTERVAL = 100` |
| UI refresh rate | 2 Hz (500ms interval) | `@st.fragment(run_every="0.5s")` |
| Serial baud rate | 115,200 bps | `backend.py` `BAUD_RATE = 115200` |
| HTTP poll timeout | 300 ms | `hil_mode.py` `timeout=0.3` |
| Signal-lost threshold (backend) | 2 seconds | `backend.py` `time.time() - last_packet_time > 2.0` |
| Signal-lost threshold (UDP bridge) | 3 seconds | `udp_bridge.py` `time.time() - last_packet_time > 3.0` |
| HTTP failure tolerance | 3 consecutive failures | `hil_mode.py` `failed_pings > 3` |
| Reconnect backoff range | 1s – 30s | `backend.py` `MIN=1.0, MAX=30.0` |
| TLE cache lifetime | 24 hours | `orbit_engine.py` `file_age > 86400` |
| Map refresh interval | Every 10s (20 cycles) | `app.py` `MAP_REFRESH_INTERVAL = 20` |
| LDR deploy threshold | ADC > 600 | `satellite.ino` / `satellite_new.ino` |
| LDR retract threshold | ADC < 400 | `satellite.ino` / `satellite_new.ino` |
| Hysteresis deadband | 200 ADC units (400–600) | `satellite.ino` / `satellite_new.ino` |
| IMU retry interval | 5 seconds | `satellite_new.ino` `IMU_RETRY_INTERVAL_MS = 5000` |
| Ground track duration | 180 minutes (±90 min) | `orbit_engine.py` `duration_minutes=180` |
| Ground track resolution | 60-second steps | `orbit_engine.py` `step_seconds=60` |
| Min elevation filter | 10° | `stations.conf` `min_elevation = 10.0` |
| Telemetry packet size | 19 bytes (binary decoder) | `decoder.py` sync(4) + volt(2) + curr(2) + temp(1) + msg(10) |
| Total source code | ~2,100 lines (Python + Arduino) | All `.py` + `.ino` files |

---

> **End of Theory.md** — This document covers every concept, technology, pattern, algorithm, and design decision in NGSC V3.0, with 40 interview questions and answers grounded in the actual codebase. For screen-by-screen user journeys and function-level code flow, see `UserJourney.md`.
