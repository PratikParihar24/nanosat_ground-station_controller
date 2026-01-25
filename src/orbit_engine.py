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
            
        # 5. Load TLEs (ROBUST FIX)
        # We load the file, then force it into a dictionary {Name: Object}
        loaded_data = load.tle_file(self.tle_file)
        
        if isinstance(loaded_data, list):
            # If it's a list, convert it to a dict
            self.satellites = {sat.name: sat for sat in loaded_data}
        else:
            # If it's already a dict, keep it
            self.satellites = loaded_data
            
        print(f"[INFO] Loaded {len(self.satellites)} satellites.")

        
    def _update_tles(self):
        """
        Private method to check if TLEs are stale and download new ones.
        """
        should_download = False
        
        # Check if file exists
        if not os.path.exists(self.tle_file):
            print("[WARN] No TLE file found. Downloading fresh...")
            should_download = True
        else:
            # Check age (Stale if older than 24 hours)
            file_age = time.time() - os.path.getmtime(self.tle_file)
            if file_age > 86400: # 86400 seconds = 1 Day
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

    def get_satellite_by_name(self, name):
        """
        Searches for a satellite. 
        Auto-strips whitespace to fix the 'ISS (ZARYA)    ' error.
        """
        # 1. Direct Match (Fastest)
        if name in self.satellites:
            return self.satellites[name]
            
        # 2. Smart Match (Strip whitespace)
        # We loop through all keys and clean them to see if they match
        for key in self.satellites.keys():
            if key.strip() == name.strip():
                return self.satellites[key]
                
        # 3. Fuzzy Match (If you just type 'ISS')
        # This helps if you don't know the full name
        for key in self.satellites.keys():
            if name.upper() in key.strip().upper():
                print(f"[INFO] Exact match not found, but found '{key}'. Using that.")
                return self.satellites[key]

        print(f"[ERR] Satellite '{name}' not found in TLE file.")
        return None

    def get_position(self, satellite):
        """
        Returns Azimuth, Elevation, Distance for a satellite object.
        """
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

# --- TEST BLOCK ---
if __name__ == "__main__":
    engine = OrbitEngine()
    
    # Try finding ISS (It should work now even with spaces!)
    iss = engine.get_satellite_by_name('ISS (ZARYA)')
    
    if iss:
        pos = engine.get_position(iss)
        print(f"\n[SUCCESS] TRACKING LOCK ESTABLISHED")
        print(f"Target:     ISS (ZARYA)")
        print(f"Azimuth:    {pos['azimuth']:.2f} deg")
        print(f"Elevation:  {pos['elevation']:.2f} deg")
        print(f"Distance:   {pos['distance_km']:.2f} km")
    else:
        print("[FAIL] Still couldn't find it.")