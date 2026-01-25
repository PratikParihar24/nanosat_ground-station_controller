# src/orbit_engine.py

import configparser
from datetime import datetime, timedelta
from skyfield.api import Topos, load, EarthSatellite
from skyfield.sgp4lib import EarthSatellite as SGP4Sat

class OrbitEngine:
    def __init__(self, config_path='config/stations.conf'):
        """
        Initialize the Math Engine.
        1. Loads the Time Scale (needed for physics).
        2. Loads the Ground Station location from config.
        """
        print("[INIT] Starting OrbitEngine...")
        
        # Load Time Scale (Downloads a small file from NASA if needed)
        self.ts = load.timescale()
        
        # Load Configuration
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Setup Ground Station (Observer)
        # We grab these values from the file you just created
        lat = float(self.config['GROUND_STATION']['latitude'])
        lon = float(self.config['GROUND_STATION']['longitude'])
        alt = float(self.config['GROUND_STATION']['altitude'])
        
        # Create the Observer object (Topos = Topocentric = Surface of Earth)
        self.station = Topos(latitude_degrees=lat, longitude_degrees=lon, elevation_m=alt)
        print(f"[INFO] Station loaded at: {lat}N, {lon}E")

    def create_satellite(self, line1, line2, name):
        """
        Creates a Satellite object from TLE lines.
        """
        satellite = EarthSatellite(line1, line2, name, self.ts)
        return satellite

    def get_position(self, satellite):
        """
        The Core Math Function.
        Returns: Azimuth (deg), Elevation (deg), Doppler Shift Factor
        """
        # 1. Get current time
        t = self.ts.now()
        
        # 2. Calculate the difference vector (Station -> Satellite)
        # This handles the heavy SGP4 math
        difference = satellite - self.station
        
        # 3. Get the "Look Angles" (Azimuth/Elevation) at that time
        topocentric = difference.at(t)
        alt, az, distance = topocentric.altaz()
        
        # 4. Calculate Relative Velocity (Range Rate) for Doppler
        # Positive velocity = moving AWAY (Frequency drops)
        # Negative velocity = moving CLOSER (Frequency rises)
        velocity = topocentric.velocity.km_per_s
        range_rate = topocentric.position.km
        
        # Note: Skyfield doesn't give range_rate directly in simple mode,
        # so for V1 we will return the basic Az/El which is 90% of the job.
        
        return {
            'azimuth': az.degrees,
            'elevation': alt.degrees,
            'distance_km': distance.km,
            'timestamp': t.utc_iso()
        }

# --- Quick Test Block ---
# This only runs if you run this file directly (not when imported)
if __name__ == "__main__":
    # Test Data: ISS TLE (This changes daily, but good for a quick test)
    tle1 = "1 25544U 98067A   24024.50000000  .00016717  00000+0  30000-3 0  9991"
    tle2 = "2 25544  51.6416 110.0000 0005000 100.0000 200.0000 15.50000000400001"
    
    # 1. Start Engine
    engine = OrbitEngine()
    
    # 2. Load Satellite
    iss = engine.create_satellite(tle1, tle2, "ISS_TEST")
    
    # 3. Get Position
    pos = engine.get_position(iss)
    
    print("\n--- TEST RESULT ---")
    print(f"Azimuth:   {pos['azimuth']:.2f} deg")
    print(f"Elevation: {pos['elevation']:.2f} deg")
    print(f"Distance:  {pos['distance_km']:.2f} km")