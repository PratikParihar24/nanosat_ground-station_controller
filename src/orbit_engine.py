# src/orbit_engine.py

import configparser
import os
import time
import requests
from skyfield.api import Topos, load, EarthSatellite

class OrbitEngine:
    def __init__(self, config_path='config/stations.conf', tle_update=True):
        print("[INIT] Starting OrbitEngine...")
        
        # 1. Load Time Scale
        self.ts = load.timescale()
        
        # 2. Load Configuration
        self.config = configparser.ConfigParser()
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        full_config_path = os.path.join(base_dir, config_path)
        self.config.read(full_config_path)
        
        # 3. Setup Ground Station
        lat = float(self.config['GROUND_STATION']['latitude'])
        lon = float(self.config['GROUND_STATION']['longitude'])
        alt = float(self.config['GROUND_STATION']['altitude'])
        self.station = Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=alt)
        print(f"[INFO] Station loaded at: {lat}N, {lon}E")

        # 4. TLE Management
        self.tle_file = os.path.join(base_dir, 'config', 'active_tles.txt')
        self.tle_url = "https://celestrak.org/NORAD/elements/stations.txt"
        
        if tle_update:
            self._update_tles()
            
        # 5. Load TLEs
        loaded_data = load.tle_file(self.tle_file)
        if isinstance(loaded_data, list):
            self.satellites = {sat.name: sat for sat in loaded_data}
        else:
            self.satellites = loaded_data
            
        print(f"[INFO] Loaded {len(self.satellites)} satellites.")

    def _update_tles(self):
        should_download = False
        if not os.path.exists(self.tle_file):
            print("[WARN] No TLE file found. Downloading fresh...")
            should_download = True
        else:
            file_age = time.time() - os.path.getmtime(self.tle_file)
            if file_age > 86400: 
                print(f"[INFO] TLE file is {file_age/3600:.1f} hours old. Updating...")
                should_download = True
            else:
                print("[INFO] TLE file is fresh. Using local cache.")
        
        if should_download:
            try:
                response = requests.get(self.tle_url, timeout=10)
                if response.status_code == 200:
                    with open(self.tle_file, 'wb') as f:
                        f.write(response.content)
                    print("[SUCCESS] TLEs updated from CelesTrak.")
                else:
                    print(f"[ERR] Failed to download TLEs. HTTP {response.status_code}")
            except Exception as e:
                print(f"[ERR] Internet Error: {e}. Using cached file if available.")

    def get_satellite_by_name(self, name, custom_tle_lines=None):
        """
        Searches for a satellite.
        Priority 1: Custom TLE provided in config (JSON)
        Priority 2: Public TLE from CelesTrak file
        """
        # 1. Check for Manual Override (Custom TLE)
        if custom_tle_lines and len(custom_tle_lines) == 2:
            print(f"[INFO] Using Custom TLE for {name}")
            return EarthSatellite(custom_tle_lines[0], custom_tle_lines[1], name, self.ts)

        # 2. Direct Match
        if name in self.satellites:
            return self.satellites[name]
            
        # 3. Smart Match (Strip whitespace)
        for key in self.satellites.keys():
            if key.strip() == name.strip():
                return self.satellites[key]
                
        # 4. Fuzzy Match
        for key in self.satellites.keys():
            if name.upper() in key.strip().upper():
                print(f"[INFO] Exact match not found, but found '{key}'. Using that.")
                return self.satellites[key]

        print(f"[ERR] Satellite '{name}' not found anywhere.")
        return None

    def get_position(self, satellite):
        t = self.ts.now()
        difference = satellite - self.station
        topocentric = difference.at(t)
        alt, az, distance = topocentric.altaz()
        
        return {
            'azimuth': az.degrees,
            'elevation': alt.degrees,
            'distance_km': distance.km,
            'timestamp': t.utc_iso()
        }

if __name__ == "__main__":
    engine = OrbitEngine()
    iss = engine.get_satellite_by_name('ISS (ZARYA)')
    if iss:
        pos = engine.get_position(iss)
        print(f"[SUCCESS] Tracking ISS at El: {pos['elevation']:.2f}")