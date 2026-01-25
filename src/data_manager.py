# src/data_manager.py

import os
import csv
from datetime import datetime

class DataManager:
    def __init__(self, satellite_name):
        """
        Initialize the Flight Recorder.
        Creates a unique CSV file for this specific pass.
        """
        # 1. Setup paths
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.log_dir = os.path.join(self.base_dir, 'data', 'telemetry')
        
        # Ensure folder exists
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 2. Generate Filename (e.g., "ISS_20260125_143005.csv")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = satellite_name.replace(" ", "_").replace("(", "").replace(")", "")
        self.filename = f"{safe_name}_{timestamp}.csv"
        self.filepath = os.path.join(self.log_dir, self.filename)
        
        # 3. Create the file and write headers
        self._init_csv()
        print(f"[LOG] Recording started: {self.filename}")

    def _init_csv(self):
        """Writes the column headers."""
        headers = [
            'timestamp', 
            'azimuth', 
            'elevation', 
            'doppler_shift', 
            'battery_voltage', 
            'internal_temp', 
            'status_msg'
        ]
        with open(self.filepath, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def log_packet(self, telemetry, orbital_data, doppler):
        """
        Saves one frame of data to the disk.
        """
        # Prepare the row
        row = [
            datetime.now().isoformat(),
            f"{orbital_data['azimuth']:.2f}",
            f"{orbital_data['elevation']:.2f}",
            doppler,
            telemetry.get('voltage', 0),  # Safe get (defaults to 0 if missing)
            telemetry.get('temp', 0),
            telemetry.get('msg', 'N/A')
        ]
        
        # Append to file
        with open(self.filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(row)