"""This script is used to handle date/time conversions. Each instance variable represents a date or time fields.
    It works using a DatetimeHandler class which will """

import datetime
import configparser
import time


class DatetimeHandler:
    """This class will handle the conversion of date and/or time fields.
       It uses the formats specified in 'Formats_Settings.ini'."""

    # Read the settings file into a variable
    Config = configparser.ConfigParser()
    Config.read("Formats_Settings.ini")

    # Get the formats for date, time and datetime.
    process_date_format = Config.get('NORMALIZE_FORMATS', 'date')
    process_datetime_format = Config.get('NORMALIZE_FORMATS', 'datetime')
    process_time_format = Config.get('NORMALIZE_FORMATS', 'time')

    # Set constants needed for conversions.
    SECONDS_IN_DAY = 24.0*60.0*60.0
    HOURS_TO_MIN = 60.0
    MINS_TO_SECS = 60.0
    HOURS_TO_SECONDS = HOURS_TO_MIN*MINS_TO_SECS

    def __init__(self):
        """Constructor for setting instance variables to None. """
        self.date_time = None
        self.date = None
        self.time = None
        self.day = None
        self.month = None
        self.year = None
        self.hour = None
        self.minute = None
        self.seconds = None
        self.am_pm = None
        self.julian_day = None
        self.part_day = None
        self.time_stamp = None

    def __calculate_part_day(self, hours, minutes=0.0, seconds=0.0):
        """

        :param hours: Hours in the time (24 hour representation)
        :param minutes: Minutes in the time
        :param seconds: The seconds in the time
        :return: The part day representation of the of time.

        Part day is calculated by dividing the the number of seconds that have gone by at the specified time by the number of seconds in the day.
        That is part_day represents what fraction of the day has gone by at the specified time.
        The formula used is part_day=(1/(24*60*60))*((hours*60*60)+(minutes*60)+(seconds))
        """
        part_day = None
        if hours is not None:
            coeff = 1.0/DatetimeHandler.SECONDS_IN_DAY
            hr_secs = hours*DatetimeHandler.HOURS_TO_SECONDS
            min_secs = minutes*DatetimeHandler.MINS_TO_SECS
            part_day = coeff*(hr_secs+min_secs+seconds)
        return part_day

    def __process_datetime(self, dt_time):
        """

        :param dt_time: The datetime variable to be processed
        :return: None

        This function processes the datetime 'dt_time' and loads the fields for the instance variables as needed.
        """

        self.date = dt_time.date()
        self.time = dt_time.time()
        self.day = dt_time.day
        self.month = dt_time.month
        self.year = dt_time.year
        self.hour = dt_time.hour
        self.minute = dt_time.minute
        self.seconds = dt_time.second
        self.am_pm = dt_time.strftime("%p")
        self.julian_day = int(dt_time.strftime("%j"))
        self.part_day = self.__calculate_part_day(dt_time.hour, dt_time.minute, dt_time.second)
        self.time_stamp = int(time.mktime(dt_time.timetuple()))

        return

    def process(self):
        """

        :return: None

        This function will process the date/time values provided.
        It will set the instance variables that can be generated from the date/time fields which it gets.
        It will check which date/time fields it has been provided and set the values for the other fields if possible.
        This function will call __process_datetime function will get all the values for the variables from the datetime
        if it is available.
        """

        # Give unix timestamp priority over all all other time fields when generating the values.
        # If there is a unix timestamp, get the datetime from that and use that to get the other fields.
        if (self.time_stamp is not None) and (self.date_time is None):
            self.date_time = datetime.datetime.utcfromtimestamp(self.time_stamp)
        if self.date_time is not None:
            self.__process_datetime(self.date_time)
        # If the date and the time are available, make the datetime from them and process
        elif (self.date is not None) and (self.time is not None):
            self.date_time = datetime.datetime(day=self.date.day, month=self.date.month, year=self.date.year,
                                               hour=self.time.hour, minute=self.time.minute, second=self.time.second)
            self.__process_datetime(self.date_time)
        # If the date is available get all the possible fields from that
        elif self.date is not None:
            self.day = self.date.day
            self.month = self.date.month
            self.year = self.date.year
        # This is used to get the julian_day from the date
            self.julian_day = int(self.date.strftime("%j"))
        # If the time is available, get all the possible fields from that.
        elif self.time is not None:
            self.hour = self.time.hour
            self.minute = self.time.minute
            self.seconds = self.time.second
            self.am_pm = self.time.strftime("%p")
        # Calculate the part day is the time is provided.
            self.part_day = self.__calculate_part_day(self.time.hour, self.time.minute, self.time.second)
        # If day, month and year are available and there is no date. Generate the date and julian day using them.
        if (self.day is not None) and (self.month is not None) and (self.year is not None) and(self.date is None):
            self.date = datetime.date(day=int(self.day), month=int(self.month), year=int(self.year))
            self.julian_day = int(self.date.strftime("%j"))
        # If hour, minute and seconds are available and there is no time. Generate the time from that and
        # calculate the part day.
        if (self.hour is not None) and (self.minute is not None) and (self.seconds is not None) and (self.time is None):
            self.time = datetime.time(hour=int(self.hour), minute=int(self.minute), second=int(self.seconds))
            self.am_pm = self.time.strftime("%p")
            self.part_day = self.__calculate_part_day(self.time.hour, self.time.minute, self.time.second)
        # If hour, minute are available, but no seconds, generate the time with them without the seconds.
        if (self.hour is not None) and (self.minute is not None) and (self.seconds is None):
            self.time = datetime.time(hour=int(self.hour), minute=int(self.minute))
            self.am_pm = self.time.strftime("%p")
            self.part_day = self.__calculate_part_day(self.time.hour, self.time.minute, self.time.second)
        # If the date and time are available generate the datetime and process it.
        # This is done again after all other processing is done.
        if (self.date is not None) and (self.time is not None):
            self.date_time = datetime.datetime(day=self.date.day, month=self.date.month,
                                               year=self.date.year, hour=self.time.hour,
                                               minute=self.time.minute, second=self.time.second)
            self.__process_datetime(self.date_time)

        return

    def input_time(self, datetime_time=None, time_string=None, str_format=None, hour=None, minute=None, seconds=None):
        """
        Function currently not being used.
        """
        if (datetime_time is not None) and (type(datetime_time) == datetime.time):
            self.time = datetime_time
        elif (time_string is not None) and (type(time_string) == str):
            if str_format is None:
                print("Format not specified, will attempt to use default format {}".
                      format(DatetimeHandler.process_time_format))
                str_format = DatetimeHandler.process_time_format
                try:
                    the_time = datetime.datetime.strptime(time_string, str_format)
                    self.time = the_time.time()
                    print("Success in attempt to use default format.")
                except Exception as e:
                    print (e)
                    print("Attempt to use default format failed")

            elif (str_format is not None) and (type(str_format) == str):
                the_time = datetime.datetime.strptime(time_string, str_format)
                self.time = the_time.time()
        elif (hour is not None) and (minute is not None) and (seconds is not None):
            the_time = datetime.time(hour=int(hour), minute=int(minute), second=int(seconds))
            self.time = the_time
        return

    def input_date(self, datetime_date=None, date_string=None, str_format=None, day=None, month=None, year=None):
        """
        Function currently not being used.
        """
        if (datetime_date is not None) and (type(datetime_date) == datetime.date):
            self.date = datetime_date
        elif (date_string is not None) and (type(date_string) == str):
            if str_format is None:
                print("Format not specified, will attempt to use default format {}".
                      format(DatetimeHandler.process_date_format))
                str_format = DatetimeHandler.process_date_format
                try:
                    the_date = datetime.datetime.strptime(date_string, str_format)
                    self.date = the_date.date()
                    print("Success in attempt to use default format.")
                except Exception as e:
                    print (e)
                    print("Attempt to use default format failed")
            elif (str_format is not None) and (type(str_format) == str):
                the_date = datetime.datetime.strptime(date_string, str_format)
                self.date = the_date.date()
        elif (day is not None) and (month is not None) and (year is not None):
            the_date = datetime.date(year=year, month=month, day=day)
            self.date = the_date
        return

    def get_datetime(self, str_format=None):
        """

        :param str_format: The format string for the datetime module to use to generate the string for the datetime.
        :return: A string representation of the datetime.

        Check if the datetime exists, if it does format it using 'str_format', if not return 'None'.
        """
        datetime_string = None
        if self.date_time is not None:
            if str_format is None:
                datetime_string = self.date_time.strftime(DatetimeHandler.process_datetime_format)
            else:
                datetime_string = self.date_time.strftime(str_format)
        return datetime_string

    def get_date(self, str_format=None):
        """

        :param str_format: The format string for the datetime module to use to generate the string for the date.
        :return: A string representation of the date.

        Check if the date exists, if it does format it using 'str_format', if not return 'None'.
        """
        date_string = None
        if self.date is not None:
            if str_format is None:
                date_string = self.date.strftime(DatetimeHandler.process_date_format)
            else:
                date_string = self.date.strftime(str_format)
        return date_string

    def get_time(self, str_format=None):
        """

        :param str_format: The format string for the datetime module to use to generate the string for the time.
        :return: A string representation of the time.

        Check if the time exists, if it does format it using 'str_format', if not return 'None'.
        """
        time_string = None
        if self.time is not None:
            if str_format is None:
                time_string = self.time.strftime(DatetimeHandler.process_time_format)
            else:
                time_string = self.time.strftime(str_format)
        return time_string

    """The functions below here check and return the variable if it exists, else it returns 'None'"""
    def get_year(self):
        year = None
        if self.year is not None:
            year = self.year
        return year

    def get_day(self):
        day = None
        if self.year is not None:
            day = self.day
        return day

    def get_month(self):
        month = None
        if self.month is not None:
            month = self.month
        return month

    def get_am_pm(self):
        am_pm = None
        if self.am_pm is not None:
            am_pm = self.am_pm
        return am_pm

    def get_hour(self):
        hour = None
        if self.hour is not None:
            hour = self.hour
        return hour

    def get_minute(self):
        minute = None
        if self.minute is not None:
            minute = self.minute
        return minute

    def get_seconds(self):
        seconds = None
        if self.seconds is not None:
            seconds = self.seconds
        return seconds

    def get_julian_day(self):
        julian_day_str = None
        if self.julian_day is not None:
            julian_day_str = str(self.julian_day)
        return julian_day_str

    def get_part_day(self):
        part_day_str = None
        if self.part_day is not None:
            part_day_str = str(self.part_day)
        return part_day_str

    def get_timestamp(self):
        timestamp_str = None
        if self.time_stamp is not None:
            timestamp_str = str(self.time_stamp)
        return timestamp_str
