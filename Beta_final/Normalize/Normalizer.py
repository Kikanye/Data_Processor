# -*- coding: utf-8 -*-
"""
This script contains the functions needed to perform the normalizing functionality of the data processor.
"""
# TODO: Could probably use seperate scripts for handling datetime normalizing and longitude and latitude normalizing.
import configparser, pandas as pd
import datetime, json
import DatetimeHandler, GeoHandler, pathlib2

Config = configparser.ConfigParser()
Config.read("Formats_Settings.ini")

DEFAULT_DATE_FORMAT = Config.get('NORMALIZE_FORMATS', 'date')
DEFAULT_DATETIME_FORMAT = Config.get('NORMALIZE_FORMATS', 'datetime')
DEFAULT_TIME_FORMAT = Config.get('NORMALIZE_FORMATS', 'time')


def datetime_work(row, formats):
    """
    :param row: A dictionary representing a row of data from the file which is being processed.
    :param formats: A dictionary containing the formats for the different date/time fields.
    :return A processed version of 'row' with all the fields that could possibly be generated added.

    This function will do the work needed to generate the different fields for representing date/time values.
    """

    # Use an instance of the DatetimeHandler() class
    curr_dt_handler = DatetimeHandler.DatetimeHandler()
    # Check for the date/time fields
    # Give datetime priority
    # if there is a datetime field no other fields are needed because all other fields can be generated from it.
    if "datetime" in row:
        # If the datetime field isn't empty, add it to the datetime variable in the DatetimeHandler() instance.
        if (row["datetime"] != '') and (row["datetime"] is not None):
            dt_time = row["datetime"]
            try:
                curr_dt_handler.date_time = datetime.datetime.strptime(dt_time, formats["datetime_format"])
            except Exception as e:
                print(e)
                print("Provided format for reading datetime failed in normalizer, will use default format {}"
                      .format(DEFAULT_DATETIME_FORMAT))
                formats["datetime_format"] = DEFAULT_DATETIME_FORMAT
                curr_dt_handler.date_time = datetime.datetime.strptime(dt_time, DEFAULT_DATETIME_FORMAT)
        # If the datetime field is empty look for the date and time field and give them priority.
        else:
            if "date" in row:
                if (row["date"] != '') and (row["date"] is not None):
                    dt = row["date"]
                    try:
                        curr_dt_handler.date = (datetime.datetime.strptime(dt, formats["date_format"])).date()
                    except Exception as e:
                        print(e)
                        print("Provided format for reading date failed in normalizer, will use default format {}".
                              format(DEFAULT_DATE_FORMAT))
                        formats["datetime_format"] = DEFAULT_DATE_FORMAT
                        curr_dt_handler.date = (datetime.datetime.strptime(dt, formats["date_format"])).date()
                # If there is no date field look for day month and year
                else:
                    if "day" in row:
                        if (row["day"] != '') and (row["day"] is not None):
                            day = int(row["day"])
                            curr_dt_handler.day = day
                    if "month" in row:
                        if (row["month"] != '') and (row["day"] is not None):
                            month = int(row["month"])
                            curr_dt_handler.month = month
                    if "year" in row:
                        if (row["year"] != '') and (row["year"] is not None):
                            yr = int(row["year"])
                            curr_dt_handler.year = yr

            if "time" in row:
                curr_time = None
                if (row["time"] != '') and (row["time"] is not None):
                    t = row["time"]
                    try:
                        curr_time = datetime.datetime.strptime(t, formats["time_format"])
                    except Exception as e:
                        print(e)
                        print("Provided format for reading time in normalizer, will use default format {}".
                              format(DEFAULT_TIME_FORMAT))
                        formats["datetime_format"] = DEFAULT_TIME_FORMAT
                        curr_time = datetime.datetime.strptime(t, formats["time_format"])

                    do_ampm = False
                    # Also look for ap/pm fields and process them.
                    if ('am/pm' in row) and (row['am/pm'] is not None) and (row['am/pm'] != ''):
                        do_ampm = True
                    if do_ampm and (curr_time is not None):
                        val = row['am/pm']
                        cleaned_val = ''
                        for letter in val:
                            if letter.isalpha():
                                cleaned_val += letter
                        cleaned_val = cleaned_val.lower()
                        if cleaned_val == 'pm':
                            curr_time = curr_time + datetime.timedelta(hours=12)

                    curr_dt_handler.time = curr_time.time()

                # If there is no date field look for hour, minutes and seconds
                else:
                    if "hour" in row:
                        if (row["hour"] != '') and (row["hour"] is not None):
                            hr = int(row["hour"])
                            if "am/pm" in row:
                                if (row["am/pm"] != '') and (row["am/pm"] is not None):
                                    val = row['am/pm']
                                    cleaned_val = ''
                                    for letter in val:
                                        if letter.isalpha():
                                            cleaned_val += letter
                                    cleaned_val = cleaned_val.lower()
                                    if (hr < 12) and (cleaned_val == 'pm'):
                                        hr = hr+12
                                    if (hr == 12) and (cleaned_val == 'am'):
                                        hr = 0
                            curr_dt_handler.hour = hr
                    if "minute" in row:
                        if (row["minute"] != '') and (row["minute"] is not None):
                            minute_val = float(row["minute"])
                            minute_val = int(minute_val)
                            curr_dt_handler.minute = minute_val
                    if "seconds" in row:
                        if (row["seconds"] != '') and (row["seconds"] is not None):
                            secs = int(row["seconds"])
                            curr_dt_handler.seconds = secs
    # Call the process method which will generate all relevant fields within the DatetimeHandler class.
    curr_dt_handler.process()

    # Add all fields into the row and return.
    row["datetime"] = curr_dt_handler.get_datetime()
    row["date"] = curr_dt_handler.get_date()
    row["time"] = curr_dt_handler.get_time()
    row["day"] = curr_dt_handler.get_day()
    row["month"] = curr_dt_handler.get_month()
    row["year"] = curr_dt_handler.get_year()
    row["hour"] = curr_dt_handler.get_hour()
    row["minute"] = curr_dt_handler.get_minute()
    row["seconds"] = curr_dt_handler.get_seconds()
    row["am/pm"] = curr_dt_handler.get_am_pm()
    row["julian_day"] = curr_dt_handler.get_julian_day()
    row["part_day"] = curr_dt_handler.get_part_day()
    row["unix_timestamp"] = curr_dt_handler.get_timestamp()

    return row


def geo_data_work(row):
    """
    :param row: A dictionary representing a row of data from the file which is being processed.
    :return A processed version of 'row' with all the fields that could possibly be generated added.

    This function will do the work needed to generate the different fields for representing longitude, latitude
    and some other 'Geospace' data values.
    """

    # Use an instance of the GeoHandler() class.
    curr_geo_handler = GeoHandler.GeoHandler()

    # if the latitude in degrees_decimal format is present, process it this way.
    # Add it to the relevant variables in the GeoHandler() class instance.
    if "latitude_decdeg" in row:
        if (row["latitude_decdeg"] != '') and (row["latitude_decdeg"] is not None):
            latitude_degrees_decimal = row['latitude_decdeg']
            lat_string = str(latitude_degrees_decimal)
            lat_string = lat_string.replace(',', '.')
            cardinal_point = None
            # Split and check the contents of the fields.
            for char in lat_string:
                if not(char.isdigit()) and not(char == '.'):
                    if char.isalpha():
                        cardinal_point = (char.strip()).lower()
                        lat_string = lat_string.replace(char, '')
                        break

            curr_geo_handler.latitude_signed_decimal = float(lat_string)
            if cardinal_point == 'n':
                curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_NORTH
            elif cardinal_point == 's':
                curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_SOUTH

    # if the latitude in degrees, minutes, seconds format is present, process it this way.
    # Add it to the relevant variables in the GeoHandler() class instance.
    if "latitude_minsec" in row:
        # Break it up into a dictionary representation., and determine the cardinal points for the value.
        deg_min_sec_dict = {'deg': None, 'min': None, 'sec': None}
        if (row["latitude_minsec"] != '') and (row["latitude_minsec"] is not None):
            latitude_minsec = row['latitude_minsec']
            latitude_minsec_split = latitude_minsec.split(u'°')
            deg_min_sec_dict['deg'] = float(latitude_minsec_split[0])

            latitude_minsec_part = latitude_minsec_split[-1]
            latitude_minsec_part = (latitude_minsec_part.strip())
            for char in latitude_minsec_part:
                if char.isalpha():
                    latitude_minsec_part = latitude_minsec_part.replace(char, '')
                    if char.lower() == 'n':
                        curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_NORTH
                    elif char.lower() == 's':
                        curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_SOUTH

            latitude_minsec_part = latitude_minsec_part.replace('"', '')
            latitude_minsec_part_split = latitude_minsec_part.split("'")
            deg_min_sec_dict['min'] = float(latitude_minsec_part_split[0])
            if len(latitude_minsec_part_split) == 2:
                deg_min_sec_dict['sec'] = float(latitude_minsec_part_split[1])
            curr_geo_handler.latitude_deg_min_sec_dict = deg_min_sec_dict

    # If there is a cardinal point fields for latitudes, process it.
    if "n/s" in row:
        if (row["n/s"] != '') and (row["n/s"] is not None):
            lat_cardinal = row['n/s']
            lat_cardinal = (str(lat_cardinal).lower()).strip()
            if lat_cardinal == 'n':
                curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_NORTH
            elif lat_cardinal == 's':
                curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_SOUTH

    # if the longitude in degrees_decimal format is present, process it this way.
    # Add it to the relevant variables in the GeoHandler() class instance.
    if "longitude_decdeg" in row:
        if row["longitude_decdeg"] != '':
            longitude_degrees_decimal = row["longitude_decdeg"]
            long_string = str(longitude_degrees_decimal)
            long_string = long_string.replace(',', '.')
            cardinal_point = None
            # Split and check the contents of the fields.
            for char in long_string:
                if not (char.isdigit()) and not (char == '.'):
                    if char.isalpha():
                        cardinal_point = (char.strip()).lower()
                        long_string = long_string.replace(char, '')
                        break

            curr_geo_handler.longitude_signed_decimal = float(long_string)
            if cardinal_point == 'e':
                curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_EAST
            elif cardinal_point == 'w':
                curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_WEST

    # if the latitude in degrees, minutes, seconds format is present, process it this way.
    # Add it to the relevant variables in the GeoHandler() class instance.
    if "longitude_minsec" in row:
        # Break it up into a dictionary, and add it to the relevant variables in the GeoHandler instance.
        deg_min_sec_dict = {'deg': None, 'min': None, 'sec': None}
        if (row["longitude_minsec"] != '') and (row["longitude_minsec"] is not None):
            longitude_minsec = row["longitude_minsec"]
            longitude_minsec_split = longitude_minsec.split(u'°')
            deg_min_sec_dict['deg'] = float(longitude_minsec_split[0])

            longitude_minsec_part = longitude_minsec_split[-1]
            longitude_minsec_part = (longitude_minsec_part.strip())
            for char in longitude_minsec_part:
                if char.isalpha():
                    longitude_minsec_part = longitude_minsec_part.replace(char, '')
                    if char.lower() == 'e':
                        curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_EAST
                    elif char.lower() == 'w':
                        curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_WEST

            longitude_minsec_part = longitude_minsec_part.replace('"', '')
            longitude_minsec_part_split = longitude_minsec_part.split("'")
            deg_min_sec_dict['min'] = float(longitude_minsec_part_split[0])
            if len(longitude_minsec_part_split) == 2:
                deg_min_sec_dict['sec'] = float(longitude_minsec_part_split[1])
            curr_geo_handler.longitude_deg_min_sec_dict = deg_min_sec_dict

    # Handle cardinal point fields.
    if "e/w" in row:
        if (row["e/w"] != '') and (row["e/w"] is not None):
            lat_cardinal = row['e/w']
            lat_cardinal = (str(lat_cardinal).lower()).strip()
            if lat_cardinal == 'e':
                curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_EAST
            elif lat_cardinal == 'w':
                curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_WEST

    # Process the fields using the .process() function. Also add the generated values into the row.
    curr_geo_handler.process()
    row["latitude_decdeg"] = curr_geo_handler.get_latitude(GeoHandler.GeoHandler.DEGREES_DECIMAL_FORMAT)
    row["latitude_minsec"] = curr_geo_handler.get_latitude(GeoHandler.GeoHandler.DEGREES_MIN_SEC_FORMAT)
    row["longitude_decdeg"] = curr_geo_handler.get_longitude(GeoHandler.GeoHandler.DEGREES_DECIMAL_FORMAT)
    row["longitude_minsec"] = curr_geo_handler.get_longitude(GeoHandler.GeoHandler.DEGREES_MIN_SEC_FORMAT)
    row["n/s"] = curr_geo_handler.lat_ns
    row["e/w"] = curr_geo_handler.long_ew
    return row


def normalize(file_name, specs, formats):
    """

    :param file_name: The path to the file which is being normalized.
    :param specs: The path to the json file containing the specifications for the structure of 'file_name'
    :param formats: A dictionary specifying the formats for date/time fields.
    :return: A list of dictionaries, where each dictionary represents a row of data from 'file_name'
            after it has been normalized.

    This function will use the functions above it to normalize 'file_name' and return a list of dictionaries
    which is the contents of 'file_name' after it has been normalized.

    'file_name' MUST BE AN EXCEL FILE!!!
    """
    print ("Normalizing {}".format(file_name))
    normalized_rows = []
    with open(specs) as the_specs:
        template_specs = json.load(the_specs)
    header_names = template_specs["header_list"]
    type_dict = {}
    for num in range(len(header_names)):
        type_dict[num] = str
    dt_frames = pd.read_excel(file_name, names=header_names, encoding='utf-8-sig')
    dt_frames = dt_frames.fillna('')
    rows = dt_frames.to_dict('records')
    for row in rows:
        row = datetime_work(row, formats)
        row = geo_data_work(row)
        normalized_rows.append(row)
    return normalized_rows


def writerows(filename, row_list, specs):
    f_path = pathlib2.Path(filename)
    fname = f_path.name
    with open(specs) as the_specs:
        template_specs = json.load(the_specs)
    parent_dir = pathlib2.Path(f_path.parent)
    save_path = str(parent_dir.joinpath('_normalized'+'-'+fname))
    data=pd.DataFrame(row_list)
    columns_order = template_specs["header_list"]
    save_path_split = save_path.split('.')
    extension = save_path_split[-1]
    if (extension.lower()).strip()!='csv':
        save_path_split[-1]='csv'
    save_path = '.'.join(save_path_split)
    data.to_csv(save_path, columns=columns_order, index=False, encoding='utf-8-sig')
    return save_path


def main():
    print("Starting")
    Config = configparser.ConfigParser()
    Config.read("Normalizer_Config.ini")

    INPUT_FILE = Config.get('SPECS', 'FILENAME')
    INPUT_SPEC = Config.get('SPECS', 'SPECFILE')
    formats = {}
    datetime_format = Config.get('FORMATS', 'datetime')
    date_format = Config.get('FORMATS', 'date')
    time_format = Config.get('FORMATS', 'time')
    formats["datetime_format"] = datetime_format
    formats["date_format"] = date_format
    formats["time_format"] = time_format
    row_list = normalize(INPUT_FILE, INPUT_SPEC, formats)
    writerows(INPUT_FILE, row_list, INPUT_SPEC)

    print("End of Processing")
    return


# main()
