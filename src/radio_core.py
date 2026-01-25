# src/radio_core.py

import sys

# We wrap the import in a try-block so the app doesn't crash 
# if the SDR driver isn't installed on your OS.
try:
    from rtlsdr import RtlSdr
    HAS_SDR = True
except ImportError:
    HAS_SDR = False
    print("[WARN] pyrtlsdr library not found. Running in MOCK mode.")
except Exception as e:
    HAS_SDR = False
    print(f"[WARN] SDR Error: {e}. Running in MOCK mode.")

class RadioCore:
    def __init__(self, frequency=145.8e6, gain='auto', mock_mode=False):
        """
        Initialize the Radio Interface.
        :param frequency: Center frequency in Hz (e.g., 145800000)
        :param gain: Gain in dB or 'auto'
        :param mock_mode: Force the system to use the Fake Radio
        """
        self.mock_mode = mock_mode or (not HAS_SDR)
        self.center_freq = frequency
        self.gain = gain
        self.sdr = None
        
        if not self.mock_mode:
            try:
                self.sdr = RtlSdr()
                self.sdr.sample_rate = 2.048e6  # Standard sample rate (2.048 MHz)
                self.sdr.center_freq = self.center_freq
                self.sdr.freq_correction = 60   # PPM correction (varies by dongle)
                self.sdr.gain = self.gain
                print(f"[INFO] Real SDR Device Connected on {frequency/1e6} MHz")
            except Exception as e:
                print(f"[ERR] Could not open SDR: {e}")
                print("[INFO] Falling back to MOCK SDR.")
                self.mock_mode = True
        
        if self.mock_mode:
            print(f"[INFO] Mock SDR initialized on {frequency/1e6} MHz")

    def set_doppler_freq(self, target_freq, doppler_shift):
        """
        Updates the radio frequency to account for Doppler Shift.
        Equation: New_Freq = Target_Freq + Doppler_Shift
        """
        corrected_freq = target_freq + doppler_shift
        
        if not self.mock_mode:
            self.sdr.center_freq = corrected_freq
        else:
            # In Mock Mode, we just print the update so you can verify the logic works
            # We use carriage return '\r' to overwrite the line instead of spamming
            sys.stdout.write(f"\r[RADIO] Tuning to: {corrected_freq/1e6:.6f} MHz (Shift: {doppler_shift:.2f} Hz)   ")
            sys.stdout.flush()

    def get_samples(self, num_samples=256*1024):
        """
        Reads raw I/Q data from the radio.
        """
        if not self.mock_mode:
            return self.sdr.read_samples(num_samples)
        else:
            # Return fake static (0s) just to keep the pipeline moving
            return [0] * num_samples

    def stop(self):
        """
        Safely closes the connection.
        """
        if not self.mock_mode and self.sdr:
            self.sdr.close()
        print("\n[INFO] Radio Closed.")

# --- Quick Test Block ---
if __name__ == "__main__":
    import time
    
    # 1. Initialize Radio (Will likely default to Mock Mode if no USB stick)
    radio = RadioCore(frequency=437.500e6)
    
    # 2. Simulate a Satellite Pass (Doppler shifting)
    # We will pretend the satellite is approaching, so frequency goes UP
    print("\n--- STARTING DOPPLER SIMULATION ---")
    base_freq = 437.500e6
    
    for i in range(10):
        # Fake shift: Starts high (+5000Hz), drops to 0, goes low (-5000Hz)
        fake_doppler = 5000 - (i * 1000) 
        
        radio.set_doppler_freq(base_freq, fake_doppler)
        time.sleep(0.5)
        
    radio.stop()