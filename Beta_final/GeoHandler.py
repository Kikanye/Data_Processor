import math as m

class GeoHandler:
    """Here a negative latitude value indicates South, and a negative longitude value indicates. """
    DEFAULT_LONG_LAT_FORMAT="number"
    EARTH_RADIUS=6371*1000 #km
    DEG_TO_RAD=(22.0/7)/180.0
    DEFAULT_DISTANCE_FORMAT="Km"

    def __init__(self):
        self.longitude_deg_min_sec_dict = None
        self.latitude_deg_min_sec_dict = None
        self.longitude_deg_min_sec = None
        self.latitude_deg_min_sec = None
        self.longitude_number = None
        self.latitude_number = None
        self.lat_ns = None
        self.long_ew = None
        self.given_speed = None
        self.calculated_speed = None
        self.northing = None
        self.easting = None
        self.altitude = None
        self.calculated_altitude = None
        self.given_distance = None
        self.calculated_distance = None
        self.heading = None
        self.calculated_heading = None
        self.time_in_seconds = None

    def process(self):

        return

    def __calculate_dictance(self, geo1, geo2):
        """This function will return the kilometer value of the distance between (lat1, lon1), (lat2, lon2)."""
        return_distance = None
        if (geo1 is not None) and (geo2 is not None):
            lat1, lon1 = geo1
            lat2, lon2 = geo2
            lat1_rad = m.radians(lat1)
            lon1_rad = m.radians(lon1)
            lat2_rad = m.radians(lat2)
            lon2_rad = m.radians(lon2)

            delta_theta = lat2_rad - lat1_rad
            delta_lambda = lon2_rad - lon1_rad
            a = m.sin(delta_theta / 2) * m.sin(delta_theta / 2) + m.cos(lat1_rad) * m.cos(lat2_rad) * \
                m.sin(delta_lambda / 2) * m.sin(delta_lambda / 2)

            c = 2 * m.atan2(m.sqrt(a), m.sqrt(1 - a))
            dist = GeoHandler.EARTH_RADIUS * c
            return_distance = dist
        return return_distance

    def get_longitude(self, str_format=DEFAULT_LONG_LAT_FORMAT):
        return_value = None
        if str_format == "number":
            return_value = str(self.longitude_number)
        elif str_format == "degrees":
            return_value = str(self.longitude_deg_min_sec)
        return return_value

    def get_latitude(self, str_format=DEFAULT_LONG_LAT_FORMAT):
        return_value=None
        if str_format == "number":
            return_value = str(self.longitude_number)
        elif str_format == "degrees":
            return_value = str(self.latitude_deg_min_sec)
        return return_value

    def get_given_distance(self, str_format=DEFAULT_DISTANCE_FORMAT):
        return_distance = None
        if str_format == "km":
            return_distance = str(self.given_distance)
        elif str_format == "m":
            return_distance = str(self.given_distance * 1000)
        elif str_format == "n":
            return_distance = str(self.given_distance * 0.539957)
        return return_distance

    def get_calculated_distance(self, str_format=DEFAULT_DISTANCE_FORMAT):
        return_distance = None
        if str_format == "km":
            return_distance = str(self.calculated_distance)
        elif str_format == "m":
            return_distance = str(self.calculated_distance * 1000)
        elif str_format == "n":
            return_distance = str(self.calculated_distance * 0.539957)
        return return_distance

    def get_given_speed(self, str_format):
        """Use necessary code for the given speed"""
        return

    def get_calculated_speed(self, str_format):
        """Apply formula for getting the speed here"""
        return
