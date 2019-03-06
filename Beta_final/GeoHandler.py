# -*- coding: utf-8 -*-

"""This script contains a class and functions which are used to generate the different values for the variables used to
   represent geographical data.

   -> When longitude and latitude values in degrees, minutes, seconds format are represented in dictionaries,
      they look like this: {'deg':X, 'min':Y, 'sec':Z} where X,Y,Z are float numbers which may be different.
   -> When longitude and latitude values in degrees, minutes, seconds format are represented as a string,
      they look like this: X°Y'Z" where X,Y,Z are float numbers which may be different.
   """
import math as m


class GeoHandler:
    """This class will handle the conversion of longitude and/or latitude fields as well as other geographical data."""

    # These constants are used to specify what formats to present longitude and latitude values in.
    DEGREES_DECIMAL_FORMAT = "DEGREES_DECIMAL_FORMAT"
    DEGREES_MIN_SEC_FORMAT = "DEG_MIN_SEC"

    # Conversion constants.
    EARTH_RADIUS = 6371*1000  # km
    DEG_TO_RAD = (22.0/7)/180.0
    KM_TO_M = 1000
    KM_TO_NM = 0.539957
    DEG_TO_MINS = 60.0
    DEG_TO_SECS = 3600.0

    # Units constants'
    KILOMETRES_DISTANCE_UNIT = "km"
    METRES_DISTANCE_UNIT = 'm'
    NAUTICAL_MILES_DISTANCE_UNIT = 'n'

    LATITUDE = 'LATITUDE'
    LONGITUDE = 'LONGITUDE'

    GEO_SOUTH = 'S'
    GEO_NORTH = 'N'
    GEO_EAST = 'E'
    GEO_WEST = 'W'

    # Number of decimal places required in values
    DECIMAL_PLACES = 4

    def __init__(self):
        # Constructor for setting instance variables to None.

        # Contain dictionary representation of longitude and latitude values.
        # deg, min, sec are keys in the variable which represent degrees, minutes and seconds respectively.
        self.longitude_deg_min_sec_dict = None
        self.latitude_deg_min_sec_dict = None

        # A string representation of the longitude and latitude values in degrees minutes seconds format.
        self.longitude_deg_min_sec = None
        self.latitude_deg_min_sec = None

        # A signed degrees decimal representation of the longitude and latitude values,
        #  where the signs indicate the cardinal direction
        self.longitude_signed_decimal = None
        self.latitude_signed_decimal = None

        # Represent the cardinal points of the longitude and latitude values.
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
        """

        :param degrees_decimal_signed: The signed decimal degrees representation of either a latitude or a longitude.
        :param lat_or_long: Is the degrees decimal value provided a longitude or a latitude.
        :return: A tuple with two values:
            -> 1. return_val_dict: A dictionary representation of the degrees_decimal_signed value
                                 in degrees, minutes, seconds
                                 eg. {'deg':X, 'min':Y, 'sec':Z} where X,Y,Z are float numbers which may be different.
           -> 2. return_val_string: A string representation of the degrees_decimal_signed value
                                    in degrees, minuted, seconds
                                 eg. X°Y'Z" where X,Y,Z are float numbers which may be different.

        This function will process a degrees decimal representation of either a longitude or a latitude
        and return two representation of it.

        """

        return_val_dict = {'deg': None, 'min': None, 'sec': None}

        # if it is a negative value do this
        if degrees_decimal_signed < 0:
            # if it is negative and it is a latitude then the cardinal point is South.
            if lat_or_long == GeoHandler.LATITUDE:
                if self.lat_ns is None:
                    self.lat_ns = GeoHandler.GEO_SOUTH
            # if it is negative and it is a longitude then the cardinal point is West.
            elif lat_or_long == GeoHandler.LONGITUDE:
                if self.long_ew is None:
                    self. long_ew = GeoHandler.GEO_WEST
            degrees_decimal_signed = -1 * degrees_decimal_signed # Make it positive so that it can be converted.
        # if it is a positive value do this
        else:
            # if it is positive and it is a latitude then the cardinal point is North.
            if lat_or_long == GeoHandler.LATITUDE:
                if self.lat_ns is None:
                    self.lat_ns = GeoHandler.GEO_NORTH
            # If it is positive and it is a longitude then the cardinal point is East
            elif lat_or_long == GeoHandler.LONGITUDE:
                if self.long_ew is None:
                    self.long_ew = GeoHandler.GEO_EAST

        # Calculate  and store the value sof the degrees, minutes and seconds and return
        degrees = int(degrees_decimal_signed)
        minutes = int((degrees_decimal_signed - degrees) * GeoHandler.DEG_TO_MINS)
        seconds = (degrees_decimal_signed - degrees - (minutes / GeoHandler.DEG_TO_MINS)) * GeoHandler.DEG_TO_SECS
        seconds = round(seconds, GeoHandler.DECIMAL_PLACES)
        return_val_dict['deg'] = degrees
        return_val_dict['min'] = minutes
        return_val_dict['sec'] = seconds
        return_val_string = str(degrees)+'°'+str(minutes)+"'"+str(seconds)+'"'

        return (return_val_dict, return_val_string)

    def __deg_min_sec_dict_to_signed_deg_decimal(self, degrees_minutes_seconds, cardinal_point):
        """

        :param degrees_minutes_seconds: A longitude or latitude value represented as a dictionary
        :param cardinal_point: The cardinal direction of the degrees_minutes_seconds value
        :return: A tuple with two values:

        """
        degrees = degrees_minutes_seconds['deg']
        minutes = degrees_minutes_seconds['min']
        seconds = degrees_minutes_seconds['sec']
        decimal_return_val = None
        degrees_minutes_seconds_return_val = None
        cardinal = ((str(cardinal_point)).lower()).strip()

        if (degrees is None) or (minutes is None):
            return (decimal_return_val, degrees_minutes_seconds_return_val)
        else:
            if seconds is None:
                decimal_return_val = degrees+(minutes/60)
                decimal_return_val = round(decimal_return_val, GeoHandler.DECIMAL_PLACES)
                if (cardinal == 's') or (cardinal == 'w'):
                    decimal_return_val = -1*decimal_return_val
                temp = str(minutes)
                temp_split = temp.split('.')
                decimal_part = float('0.'+temp_split[-1])
                seconds = decimal_part*60
                seconds = round(seconds, GeoHandler.DECIMAL_PLACES)
                degrees_minutes_seconds_return_val = str(int(degrees)) + "°" + str(int(minutes)) + "'" +\
                                                     str(seconds)+'"'
            else:
                decimal_return_val = degrees+(minutes/60)+(seconds/3600)
                decimal_return_val = round(decimal_return_val, GeoHandler.DECIMAL_PLACES)
                degrees_minutes_seconds_return_val = str(int(degrees)) + "°" + str(int(minutes)) + "'" \
                                                     + str(seconds) + '"'

        return (decimal_return_val, degrees_minutes_seconds_return_val)

    def __deg_min_sec_dict_to_deg_min_sec_string(self, degrees_minutes_seconds):
        degrees = degrees_minutes_seconds['deg']
        minutes = degrees_minutes_seconds['min']
        seconds = degrees_minutes_seconds['sec']

        degrees_minutes_seconds_string = None

        if (degrees is None) or (minutes is None):
            return degrees_minutes_seconds_string
        else:
            if seconds is None:
                temp = str(minutes)
                temp_split = temp.split('.')
                decimal_part = float('0.' + temp_split[-1])
                seconds = decimal_part * 60
                seconds = round(seconds, GeoHandler.DECIMAL_PLACES)
                degrees_minutes_seconds_string = str(int(degrees)) + "°" + str(int(minutes)) + "'" + \
                                                     str(seconds) + '"'
            else:
                degrees_minutes_seconds_string = str(int(degrees)) + "°" + str(int(minutes)) + "'" \
                                                     + str(seconds) + '"'

        return degrees_minutes_seconds_string

    def process(self):
        if (self.longitude_signed_decimal is not None) and (self.longitude_deg_min_sec_dict is None):
            return_val = self.__signed_deg_decimal_to_deg_min_sec(self.longitude_signed_decimal, GeoHandler.LONGITUDE)
            self.longitude_deg_min_sec_dict, self.longitude_deg_min_sec = return_val
        if (self.latitude_signed_decimal is not None) and (self.latitude_deg_min_sec_dict is None):
            return_val = self.__signed_deg_decimal_to_deg_min_sec(self.latitude_signed_decimal, GeoHandler.LATITUDE)
            self.latitude_deg_min_sec_dict, self.latitude_deg_min_sec = return_val
        if (self.latitude_deg_min_sec_dict is not None) and (self.latitude_signed_decimal is None):
            return_val = self.__deg_min_sec_dict_to_signed_deg_decimal(self.latitude_deg_min_sec_dict, self.lat_ns)
            self.latitude_signed_decimal, self.latitude_deg_min_sec = return_val
        if (self.longitude_deg_min_sec_dict is not None) and (self.longitude_signed_decimal is None):
            return_val = self.__deg_min_sec_dict_to_signed_deg_decimal(self.longitude_deg_min_sec_dict, self.long_ew)
            self.longitude_signed_decimal, self.longitude_deg_min_sec = return_val
        if (self.longitude_deg_min_sec_dict is not None) and (self.longitude_deg_min_sec is None):
            self.longitude_deg_min_sec = self.__deg_min_sec_dict_to_deg_min_sec_string(self.longitude_deg_min_sec_dict)
        if (self.latitude_deg_min_sec_dict is not None) and (self.latitude_deg_min_sec is None):
            self.latitude_deg_min_sec = self.__deg_min_sec_dict_to_deg_min_sec_string(self.latitude_deg_min_sec_dict)

        if self.long_ew is not None:
            self.long_ew = (self.long_ew).upper()
        if self.lat_ns is not None:
            self.lat_ns = (self.lat_ns).upper()
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

    def get_longitude(self, str_format=DEGREES_DECIMAL_FORMAT):
        return_value = None
        if str_format == GeoHandler.DEGREES_DECIMAL_FORMAT:
            if self.longitude_signed_decimal is not None:
                return_value = str(round(self.longitude_signed_decimal, GeoHandler.DECIMAL_PLACES))
        elif str_format == GeoHandler.DEGREES_MIN_SEC_FORMAT:
            return_value = str(self.longitude_deg_min_sec)
        return return_value

    def get_latitude(self, str_format=DEGREES_DECIMAL_FORMAT):
        return_value=None
        if str_format == GeoHandler.DEGREES_DECIMAL_FORMAT:
            if self.latitude_signed_decimal is not None:
                return_value = str(round(self.latitude_signed_decimal, GeoHandler.DECIMAL_PLACES))
        elif str_format == GeoHandler.DEGREES_MIN_SEC_FORMAT:
            return_value = str(self.latitude_deg_min_sec)
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

    def get_cardinal_point(self, long_or_lat):
        return_cardinal = None
        if long_or_lat == GeoHandler.LATITUDE:
            return_cardinal = str(self.lat_ns)
        elif long_or_lat == GeoHandler.LONGITUDE:
            return_cardinal = str(self.long_ew)
        return return_cardinal

    def get_given_speed(self, str_format):
        """Use necessary code for the given speed"""
        return

    def get_calculated_speed(self, str_format):
        """Apply formula for getting the speed here"""
        return

