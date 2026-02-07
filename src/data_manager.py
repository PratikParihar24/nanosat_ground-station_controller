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
        
        # Initialize File
        self._init_log()

    def _init_log(self):
        """Creates the file with headers."""
        try:
            with open(self.filepath, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "azimuth", "elevation", "range", "doppler", "voltage", "temp"])
        except Exception as e:
            print(f"[ERROR] Could not create log: {e}")

    def log_packet(self, telemetry, position, doppler):
        """Appends a row of data."""
        try:
            with open(self.filepath, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().strftime("%H:%M:%S"),
                    f"{position['azimuth']:.2f}",
                    f"{position['elevation']:.2f}",
                    f"{position['distance_km']:.2f}",
                    doppler,
                    telemetry.get('voltage', 0),
                    telemetry.get('temp', 0)
                ])
        except Exception as e:
            
            print(f"[ERROR] Write failed: {e}")