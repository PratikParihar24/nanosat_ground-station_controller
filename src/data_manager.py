# src/data_manager.py
import os
import csv
from datetime import datetime

class DataManager:
    def __init__(self, satellite_name):
        self.sat_name = satellite_name
        
        # --- PATH LOGIC (Hardened) ---
        # 1. Get the directory where THIS file (data_manager.py) lives (i.e., src/)
        src_dir = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Go up one level to the Project Root
        project_root = os.path.dirname(src_dir)
        
        # 3. Define the specific subfolder
        self.log_dir = os.path.join(project_root, 'data', 'telemetry', 'mission_control')
        
        # 4. Force create the directory
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 5. Create Filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(self.log_dir, f"{satellite_name}_{timestamp}.csv")
        
        # --- DEBUG PRINT ---
        # Look at your terminal when you start tracking!
        print(f"[DATA MANAGER] Saving log to: {self.filepath}")
        
        # Initialize File - keep handle open for session
        self._file = None
        self._writer = None
        self._init_log()

    def _init_log(self):
        """Creates the file with headers and keeps file open."""
        try:
            self._file = open(self.filepath, 'w', newline='')
            self._writer = csv.writer(self._file)
            self._writer.writerow(["timestamp", "azimuth", "elevation", "range", "doppler", "voltage", "temp"])
            self._file.flush()
        except Exception as e:
            print(f"[ERROR] Could not create log: {e}")

    def log_packet(self, telemetry, position, doppler):
        """Appends a row of data using persistent file handle."""
        if not self._writer:
            print("[WARN] DataManager file not open, skipping log")
            return
            
        try:
            self._writer.writerow([
                datetime.now().strftime("%H:%M:%S"),
                f"{position['azimuth']:.2f}",
                f"{position['elevation']:.2f}",
                f"{position['distance_km']:.2f}",
                doppler,
                telemetry.get('voltage', 0),
                telemetry.get('temp', 0)
            ])
            self._file.flush()  # Ensure data is written immediately
        except Exception as e:
            print(f"[ERROR] Write failed: {e}")

    def close(self):
        """Safely close the file handle."""
        if self._file:
            try:
                self._file.close()
                self._file = None
                self._writer = None
                print(f"[DATA MANAGER] Log file closed: {self.filepath}")
            except Exception as e:
                print(f"[ERROR] Failed to close log file: {e}")

    def __del__(self):
        """Ensure file is closed on object destruction."""
        self.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
        return False