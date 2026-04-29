# src/decoder.py

from construct import Struct, Int16ub, Int8ub, Float32b, Const, PaddedString
import random
import time

# --- Define the Packet Structure ---
# This matches the "Byte Map" of the satellite
# Example: First 4 bytes are Sync Word, next 2 are Voltage, etc.
TelemetryPacket = Struct(
    "sync_word" / Const(b"\x1A\xCF\xFC\x1D"),  # Unique ID (4 bytes)
    "battery_voltage" / Int16ub,              # 2 bytes (Raw integer)
    "panel_current" / Int16ub,                # 2 bytes
    "internal_temp" / Int8ub,                 # 1 byte
    "status_msg" / PaddedString(10, "utf-8")  # 10 bytes text
)

# --- Validation Constants ---
VOLTAGE_MIN = 0.0
VOLTAGE_MAX = 15.0   # Safe max for LiPo batteries
CURRENT_MIN = 0.0
CURRENT_MAX = 5.0    # 5A max expected
TEMP_MIN = -50.0     # Celsius - extreme cold
TEMP_MAX = 100.0     # Celsius - extreme heat

class TelemetryDecoder:
    def __init__(self):
        self.packet_count = 0
        self.error_count = 0

    def parse_frame(self, raw_bytes):
        """
        Tries to fit raw bytes into our structure.
        Returns None if parsing fails or values are out of range.
        """
        try:
            # Parse the bytes using the definition above
            data = TelemetryPacket.parse(raw_bytes)
            
            # Apply Physics Conversions (y = mx + c)
            raw_voltage = data.battery_voltage * 0.01
            raw_current = data.panel_current * 0.001
            raw_temp = data.internal_temp - 20
            
            # Validate and clamp values to safe ranges
            voltage = max(VOLTAGE_MIN, min(VOLTAGE_MAX, raw_voltage))
            current = max(CURRENT_MIN, min(CURRENT_MAX, raw_current))
            temp = max(TEMP_MIN, min(TEMP_MAX, raw_temp))
            
            # Check if values were clamped (indicates bad data)
            was_clamped = (raw_voltage != voltage or raw_current != current or raw_temp != temp)
            if was_clamped:
                self.error_count += 1
                print(f"[WARN] Telemetry values out of range, clamped: V={raw_voltage:.2f}->{voltage:.2f}, I={raw_current:.3f}->{current:.3f}, T={raw_temp:.1f}->{temp:.1f}")
            
            parsed = {
                "voltage": voltage,
                "current": current,
                "temp": temp,
                "msg": data.status_msg,
                "raw_voltage": raw_voltage,  # Keep raw for diagnostics
                "raw_temp": raw_temp
            }
            self.packet_count += 1
            return parsed
        except Exception as e:
            # If noise corrupts the packet, parsing fails
            self.error_count += 1
            print(f"[WARN] Frame parse failed: {e}")
            return None

    def get_mock_packet(self):
        """
        Generates a fake valid packet for testing.
        """
        # Create fake raw values
        fake_volts = int(random.uniform(700, 840))  # 7.00V - 8.40V
        fake_amps = int(random.uniform(100, 500))
        fake_temp = int(random.uniform(40, 60))     # 20C - 40C
        
        # Pack them into binary (Reverse Engineering!)
        raw = TelemetryPacket.build(dict(
            sync_word=b"\x1A\xCF\xFC\x1D",
            battery_voltage=fake_volts,
            panel_current=fake_amps,
            internal_temp=fake_temp,
            status_msg=u"ALL_OK"
        ))
        return raw
    
    def get_stats(self):
        """Return decoder statistics."""
        return {
            "packets_processed": self.packet_count,
            "errors": self.error_count,
            "error_rate": self.error_count / max(1, self.packet_count)
        }