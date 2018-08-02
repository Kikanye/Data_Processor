import math as m

class GeoHandler:
    """Here a negative latitude value indicates South, and a negative longitude value indicates. """
    SIGNED_LONG_LAT_FORMAT = "SIGNED_NUMBER"
    UNSIGNED_LONG_LAT_FORMAT = "UNSIGNED_NUMBER"
    DEGREES_MIN_SEC_FORMAT = "DEG_MIN_SEC"

    EARTH_RADIUS = 6371*1000 #km
    DEG_TO_RAD = (22.0/7)/180.0

    KILOMETRES_DISTANCE_UNIT = "km"
    METRES_DISTANCE_UNIT = 'm'
    NAUTICAL_MILES_DISTANCE_UNIT = 'n'

    KM_TO_M = 1000
    KM_TO_NM = 0.539957

    DEG_TO_MINS = 60
    DEG_TO_SECS = 3600

    LATITUDE = 'LAT'
    LONGITUDE = 'LONG'

    GEO_SOUTH = 'S'
    GEO_NORTH = 'N'
    GEO_EAST = 'E'
    GEO_WEST = 'W'

    def __init__(self):
        self.longitude_deg_min_sec_dict = None
        self.latitude_deg_min_sec_dict = None
        self.longitude_deg_min_sec = None
        self.latitude_deg_min_sec = None
        #self.longitude_unsigned_decimal = None
        #self.latitude_unsigned_decimal = None
        self.longitude_signed_decimal = None
        self.latitude_signed_decimal = None
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

    def __signed_deg_decimal_to_deg_min_sec(self, degrees_decimal_signed, lat_or_long):
        return_val_dict = {'deg': None, 'min': None, 'sec':None}
        if (degrees_decimal_signed<0):
            if (lat_or_long == GeoHandler.LATITUDE):
                self.lat_ns = GeoHandler.GEO_SOUTH
            elif (lat_or_long == GeoHandler.LONGITUDE):
                self. long_ew = GeoHandler.GEO_WEST
            degrees_decimal_signed = -1 * degrees_decimal_signed
        else:
            if lat_or_long ==GeoHandler.LATITUDE:
                self.lat_ns = GeoHandler.GEO_NORTH
            elif lat_or_long == GeoHandler.LONGITUDE:
                self.long_ew = GeoHandler.GEO_EAST
        degrees = int(degrees_decimal_signed)
        minutes = int((degrees_decimal_signed - degrees) * GeoHandler.DEG_TO_MINS)
        seconds = (degrees_decimal_signed - degrees - (minutes / GeoHandler.DEG_TO_MINS)) * GeoHandler.DEG_TO_SECS

        return_val_dict['deg'] = degrees
        return_val_dict['min'] = minutes
        return_val_dict['sec'] = seconds
        return_val_string = str(degrees)+'°'+str(minutes)+"'"+str(seconds)+'"'

        return (return_val_dict, return_val_string)


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

    def get_longitude(self, str_format=SIGNED_LONG_LAT_FORMAT):
        return_value = None
        if str_format == GeoHandler.SIGNED_LONG_LAT_FORMAT:
            return_value = str(self.longitude_signed_decimal)
        elif str_format == GeoHandler.DEGREES_MIN_SEC_FORMAT:
            return_value = str(self.longitude_deg_min_sec)
        elif str_format == GeoHandler.UNSIGNED_LONG_LAT_FORMAT:
            return_value = str(self.longitude_unsigned_decimal)
        return return_value

    def get_latitude(self, str_format=SIGNED_LONG_LAT_FORMAT):
        return_value=None
        if str_format == GeoHandler.SIGNED_LONG_LAT_FORMAT:
            return_value = str(self.latitude_signed_decimal)
        elif str_format == GeoHandler.DEGREES_MIN_SEC_FORMAT:
            return_value = str(self.latitude_deg_min_sec)
        elif str_format ==GeoHandler.UNSIGNED_LONG_LAT_FORMAT:
            return_value = str(self.latitude_unsigned_decimal)
        return return_value

    def get_given_distance(self, str_format=KILOMETRES_DISTANCE_UNIT):
        return_distance = None
        if str_format == GeoHandler.KILOMETRES_DISTANCE_UNIT:
            return_distance = str(self.given_distance)
        elif str_format == GeoHandler.METRES_DISTANCE_UNIT:
            return_distance = str(self.given_distance * GeoHandler.KM_TO_M)
        elif str_format == GeoHandler.NAUTICAL_MILES_DISTANCE_UNIT:
            return_distance = str(self.given_distance * GeoHandler.KM_TO_NM)
        return return_distance

    def get_calculated_distance(self, str_format=KILOMETRES_DISTANCE_UNIT):
        return_distance = None
        if str_format == GeoHandler.KILOMETRES_DISTANCE_UNIT:
            return_distance = str(self.calculated_distance)
        elif str_format == GeoHandler.METRES_DISTANCE_UNIT:
            return_distance = str(self.calculated_distance * GeoHandler.KM_TO_M)
        elif str_format == GeoHandler.NAUTICAL_MILES_DISTANCE_UNIT:
            return_distance = str(self.calculated_distance * GeoHandler.KM_TO_NM)
        return return_distance

    def get_given_speed(self, str_format):
        """Use necessary code for the given speed"""
        return

    def get_calculated_speed(self, str_format):
        """Apply formula for getting the speed here"""
        return
