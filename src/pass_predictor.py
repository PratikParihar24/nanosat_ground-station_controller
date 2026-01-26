# src/pass_predictor.py

from skyfield.api import load, wgs84
from datetime import timedelta

class PassPredictor:
    def __init__(self, location_obj):
        """
        :param location_obj: A skyfield Topos object (Your Ground Station)
        """
        self.station = location_obj
        self.ts = load.timescale()

    def get_next_passes(self, satellite, hours=24, min_elevation=10):
        """
        Calculates visible passes for the next 24 hours.
        Returns a list of dictionaries with start/max/end times.
        """
        t0 = self.ts.now()
        t1 = self.ts.now() + timedelta(hours=hours)

        # Skyfield's magic function: find_events
        # 0 = Rise, 1 = Culminate (Max Height), 2 = Set
        t, events = satellite.find_events(self.station, t0, t1, altitude_degrees=min_elevation)

        pass_list = []
        current_pass = {}

        for time_obj, event_type in zip(t, events):
            # event_type 0: AOS (Acquisition of Signal) - Rise
            if event_type == 0:
                current_pass['aos'] = time_obj
                current_pass['aos_iso'] = time_obj.utc_iso()
            
            # event_type 1: TCA (Time of Closest Approach) - Max Elevation
            elif event_type == 1:
                current_pass['tca'] = time_obj
                # Calculate max elevation at this peak time
                diff = satellite - self.station
                alt, _, _ = diff.at(time_obj).altaz()
                current_pass['max_el'] = alt.degrees
            
            # event_type 2: LOS (Loss of Signal) - Set
            elif event_type == 2:
                current_pass['los'] = time_obj
                current_pass['los_iso'] = time_obj.utc_iso()
                
                # Only save if we captured the full cycle (Rise -> Set)
                if 'aos' in current_pass:
                    # Calculate Duration
                    duration_sec = (current_pass['los'] - current_pass['aos']) * 24 * 3600
                    current_pass['duration_str'] = f"{int(duration_sec // 60)}m {int(duration_sec % 60)}s"
                    pass_list.append(current_pass)
                current_pass = {} # Reset for next pass

        return pass_list