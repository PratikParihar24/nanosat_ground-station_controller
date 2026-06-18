# src/backend.py
from fastapi import FastAPI
from pydantic import BaseModel
import serial  # pip install pyserial
import json
import threading
import time
import csv
import os
import math
from datetime import datetime

app = FastAPI()

# --- UMBILICAL CORD (SERIAL) CONFIGURATION ---
SIMULATION_MODE = os.getenv("RENDER") is not None or os.getenv("SIMULATION_MODE") == "True"
COM_PORT = os.environ.get("ARDUINO_COM_PORT", "COM7")
BAUD_RATE = 115200

# --- RECONNECTION POLICY ---
RECONNECT_MIN_DELAY_S = 1.0
RECONNECT_MAX_DELAY_S = 30.0

# --- SYSTEM CONFIGURATION ---
state_lock = threading.Lock()
serial_io_lock = threading.Lock()
serial_port = None
_shutdown_event = threading.Event()

# --- LOGGING SETUP ---
LOG_DIR = os.path.abspath("data/telemetry/hil_side")
os.makedirs(LOG_DIR, exist_ok=True)
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
current_log_file = os.path.join(LOG_DIR, f"hil_session_{timestamp}.csv")

_log_file = None
_log_writer = None

try:
    _log_file = open(current_log_file, "w", newline="")
    _log_writer = csv.writer(_log_file)
    _log_writer.writerow(
        ["timestamp", "pitch", "roll", "yaw", "light", "led_status", "solar_status", "mode"]
    )
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
        "status": {"led": "OFF", "solar": "RETRACTED", "mode": "MANUAL"},
    },
}


def _set_link_disconnected():
    with state_lock:
        ground_state["connected"] = False


def _apply_telemetry_packet(packet: dict):
    with state_lock:
        ground_state["last_packet_time"] = time.time()
        ground_state["connected"] = True
        ground_state["telemetry"]["pitch"] = packet.get("pitch", 0.0)
        ground_state["telemetry"]["roll"] = packet.get("roll", 0.0)
        ground_state["telemetry"]["light"] = packet.get("light", 0)
        if "status" in packet:
            ground_state["telemetry"]["status"] = packet["status"]


def _log_telemetry_packet(packet: dict):
    if not _log_writer:
        return
    s = packet.get("status", {})
    try:
        _log_writer.writerow(
            [
                datetime.now().strftime("%H:%M:%S"),
                packet.get("pitch", 0),
                packet.get("roll", 0),
                packet.get("yaw", 0),
                packet.get("light", 0),
                s.get("led"),
                s.get("solar"),
                s.get("mode"),
            ]
        )
        _log_file.flush()
    except Exception as e:
        print(f"[ERROR] CSV write failed: {e}")


def _close_serial_port():
    """Close the serial handle and clear the global reference."""
    global serial_port
    with serial_io_lock:
        port = serial_port
        serial_port = None
        if port is None:
            return
        try:
            if port.is_open:
                port.close()
        except serial.SerialException as e:
            print(f"[WARN] Error while closing serial port: {e}")


def _open_serial_port() -> bool:
    """Attempt to open the configured COM port. Returns True on success."""
    global serial_port
    with serial_io_lock:
        if serial_port is not None and serial_port.is_open:
            return True
        try:
            serial_port = serial.Serial(COM_PORT, BAUD_RATE, timeout=1)
            print(f"[BACKEND] Hardline Umbilical Connected on {COM_PORT} at {BAUD_RATE} baud.")
            return True
        except (serial.SerialException, OSError) as e:
            serial_port = None
            print(f"[WARN] Could not open {COM_PORT}: {e}")
            print("Is the Arduino IDE Serial Monitor open? IT MUST BE CLOSED!")
            return False


def _wait_for_reconnect(delay_s: float) -> float:
    """Interruptible backoff wait. Returns the next delay (exponential)."""
    if _shutdown_event.wait(delay_s):
        return delay_s
    return min(delay_s * 2, RECONNECT_MAX_DELAY_S)


def _read_serial_line() -> str | None:
    """
    Read one line from the umbilical if data is waiting.
    Must be called with serial_io_lock held by the caller.
    """
    if serial_port is None or not serial_port.is_open:
        return None
    if serial_port.in_waiting <= 0:
        return None
    return serial_port.readline().decode("utf-8").strip()


def _handle_telemetry_line(line: str):
    if not line.startswith("TELEM:"):
        return
    json_str = line.replace("TELEM:", "", 1)
    try:
        packet = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"[WARN] Malformed JSON packet: {e}")
        return
    _apply_telemetry_packet(packet)
    _log_telemetry_packet(packet)


def _serial_read_loop():
    """Inner loop: ingest telemetry while the port remains healthy."""
    while not _shutdown_event.is_set():
        try:
            with serial_io_lock:
                line = _read_serial_line()
        except UnicodeDecodeError as e:
            print(f"[WARN] Invalid bytes in serial buffer: {e}")
            continue
        except serial.SerialException as e:
            print(f"[ERROR] Serial connection lost: {e}")
            _set_link_disconnected()
            _close_serial_port()
            return

        if line is None:
            time.sleep(0.01)
            continue

        try:
            _handle_telemetry_line(line)
        except Exception as e:
            print(f"[ERROR] Telemetry processing failed: {e}")


def simulated_telemetry_loop():
    """Inner loop: generate synthetic telemetry for cloud/testing."""
    print("[INFO] Starting Simulated Telemetry Loop (10Hz).")
    while not _shutdown_event.is_set():
        t = time.time()
        pitch = math.sin(t * 0.5) * 45.0
        roll = math.cos(t * 0.3) * 45.0
        yaw = (t * 10) % 360.0
        light = int(abs(math.sin(t * 0.1)) * 1023)
        
        with state_lock:
            ground_state["last_packet_time"] = time.time()
            ground_state["connected"] = True
            ground_state["telemetry"]["pitch"] = pitch
            ground_state["telemetry"]["roll"] = roll
            ground_state["telemetry"]["yaw"] = yaw
            ground_state["telemetry"]["light"] = light
            
        time.sleep(0.1)


def serial_listener():
    """
    Supervised background worker: open the umbilical, ingest 10Hz telemetry,
    and automatically reconnect with exponential backoff after any fault.
    """
    if SIMULATION_MODE:
        simulated_telemetry_loop()
        return

    global _log_file, _log_writer
    reconnect_delay = RECONNECT_MIN_DELAY_S

    while not _shutdown_event.is_set():
        _set_link_disconnected()

        if not _open_serial_port():
            reconnect_delay = _wait_for_reconnect(reconnect_delay)
            continue

        reconnect_delay = RECONNECT_MIN_DELAY_S
        _serial_read_loop()

        if not _shutdown_event.is_set():
            print(f"[INFO] Reconnecting to {COM_PORT} in {reconnect_delay:.1f}s...")
            reconnect_delay = _wait_for_reconnect(reconnect_delay)

    if _log_file:
        _log_file.close()
        _log_file = None
        _log_writer = None
    print("Serial listener stopped.")


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
    if SIMULATION_MODE:
        action = cmd.action.upper().strip()
        with state_lock:
            status = ground_state["telemetry"]["status"]
            if action == "LED_ON":
                status["led"] = "ON"
            elif action == "LED_OFF":
                status["led"] = "OFF"
            elif action == "SOLAR_DEPLOY":
                status["solar"] = "DEPLOYED"
            elif action == "SOLAR_RETRACT":
                status["solar"] = "RETRACTED"
            elif action == "MODE_AUTO":
                status["mode"] = "AUTO"
            elif action == "MODE_MANUAL":
                status["mode"] = "MANUAL"
        print(f"[SIM FIRED] {cmd.action}")
        return {"status": "success"}

    command_str = f"{cmd.action}\n"
    encoded = command_str.encode("utf-8")

    try:
        with serial_io_lock:
            if serial_port is None or not serial_port.is_open:
                return {"status": "error", "message": "Umbilical disconnected."}

            bytes_written = serial_port.write(encoded)
            serial_port.flush()

        if bytes_written != len(encoded):
            print(f"[WARN] Incomplete write: {bytes_written}/{len(encoded)} bytes")
            return {"status": "error", "message": "Incomplete write"}

        print(f"[HARDLINE FIRED] {cmd.action} over {COM_PORT}")
        return {"status": "success"}

    except serial.SerialException as e:
        print(f"[COMMAND ERROR] Serial exception: {e}")
        _set_link_disconnected()
        _close_serial_port()
        return {"status": "error", "message": f"Serial error: {str(e)}"}
    except Exception as e:
        print(f"[COMMAND ERROR] {e}")
        return {"status": "error", "message": str(e)}


@app.on_event("shutdown")
def shutdown_event():
    """Graceful shutdown handler."""
    print("[INFO] Shutting down...")
    _shutdown_event.set()
    _close_serial_port()

    if _log_file:
        _log_file.close()
        print("[INFO] Log file closed.")
