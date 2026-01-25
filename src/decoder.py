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

class TelemetryDecoder:
    def __init__(self):
        self.packet_count = 0

    def parse_frame(self, raw_bytes):
        """
        Tries to fit raw bytes into our structure.
        """
        try:
            # Parse the bytes using the definition above
            data = TelemetryPacket.parse(raw_bytes)
            
            # Apply Physics Conversions (y = mx + c)
            parsed = {
                "voltage": data.battery_voltage * 0.01,  # Convert 800 -> 8.00V
                "current": data.panel_current * 0.001,   # Convert 500 -> 0.5A
                "temp": data.internal_temp - 20,         # Offset
                "msg": data.status_msg
            }
            self.packet_count += 1
            return parsed
        except Exception as e:
            # If noise corrupts the packet, parsing fails
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