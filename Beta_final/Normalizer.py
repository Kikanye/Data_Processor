# -*- coding: utf-8 -*-
import configparser, pandas as pd
import datetime, json, openpyxl
import DatetimeHandler, GeoHandler, pathlib2

Config = configparser.ConfigParser()
Config.read("Formats_Settings.ini")

DEFAULT_DATE_FORMAT = Config.get('DATALOADER_FORMATS', 'date')
DEFAULT_DATETIME_FORMAT = Config.get('DATALOADER_FORMATS', 'datetime')
DEFAULT_TIME_FORMAT = Config.get('DATALOADER_FORMATS', 'time')

def datetime_work(row, formats):
    curr_dt_handler = DatetimeHandler.DatetimeHandler()
    if "datetime" in row:
        if (row["datetime"] != '') and (row["datetime"] is not None):
            dt_time = row["datetime"]
            try:
                curr_dt_handler.date_time = datetime.datetime.strptime(dt_time, formats["datetime_format"])
            except Exception as e:
                print("Provided format for reading datetime failed in normalizer, will use default format {}"
                      .format(DEFAULT_DATETIME_FORMAT))
                formats["datetime_format"]=DEFAULT_DATETIME_FORMAT
                curr_dt_handler.date_time = datetime.datetime.strptime(dt_time, DEFAULT_DATETIME_FORMAT)

        else:
            if "date" in row:
                if (row["date"] != '') and (row["date"] is not None):
                    dt = row["date"]
                    try:
                        curr_dt_handler.date = (datetime.datetime.strptime(dt, formats["date_format"])).date()
                    except Exception as e:
                        print("Provided format for reading date failed in normalizer, will use default format {}".
                              format(DEFAULT_DATE_FORMAT))
                        formats["datetime_format"] = DEFAULT_DATE_FORMAT
                        curr_dt_handler.date = (datetime.datetime.strptime(dt, formats["date_format"])).date()

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
                if (row["time"] != '') and (row["time"] is not None):
                    t = row["time"]
                    try:
                        curr_dt_handler.time = (datetime.datetime.strptime(t, formats["time_format"])).time()
                    except Exception as e:
                        print("Provided format for reading time in normalizer, will use default format {}".
                              format(DEFAULT_TIME_FORMAT))
                        formats["datetime_format"] = DEFAULT_TIME_FORMAT
                        curr_dt_handler.time = (datetime.datetime.strptime(t, formats["time_format"])).time()

                else:
                    if "hour" in row:
                        if (row["hour"] != '') and (row["hour"] is not None):
                            hr = int(row["hour"])
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
    curr_dt_handler.process()

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
    curr_geo_handler = GeoHandler.GeoHandler()

    if "latitude_deg_dec" in row:
        if (row["latitude_deg_dec"] != '') and (row["latitude_deg_dec"] is not None):
            latitude_degrees_decimal = row['latitude_deg_dec']
            lat_string = str(latitude_degrees_decimal)
            lat_string = lat_string.replace(',', '.')
            cardinal_point = None
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

    if "latitude_min_sec" in row:
        deg_min_sec_dict = {'deg': None, 'min': None, 'sec': None}
        if (row["latitude_min_sec"] != '') and (row["latitude_min_sec"] is not None):
            latitude_min_sec = row['latitude_min_sec']
            latitude_min_sec_split = latitude_min_sec.split('°')
            deg_min_sec_dict['deg'] = float(latitude_min_sec_split[0])

            latitude_min_sec_part = latitude_min_sec_split[-1]
            latitude_min_sec_part = (latitude_min_sec_part.strip())
            for char in latitude_min_sec_part:
                if char.isalpha():
                    latitude_min_sec_part = latitude_min_sec_part.replace(char, '')
                    if char.lower() == 'n':
                        curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_NORTH
                    elif char.lower() == 's':
                        curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_SOUTH

            latitude_min_sec_part = latitude_min_sec_part.replace('"', '')
            latitude_min_sec_part_split = latitude_min_sec_part.split("'")
            deg_min_sec_dict['min'] = float(latitude_min_sec_part_split[0])
            if len(latitude_min_sec_part_split) == 2:
                deg_min_sec_dict['sec'] = float(latitude_min_sec_part_split[1])
            curr_geo_handler.latitude_deg_min_sec_dict = deg_min_sec_dict

    if "n/s" in row:
        if (row["n/s"] != '') and (row["n/s"] is not None):
            lat_cardinal = row['n/s']
            lat_cardinal = (str(lat_cardinal).lower()).strip()
            if lat_cardinal == 'n':
                curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_NORTH
            elif lat_cardinal == 's':
                curr_geo_handler.lat_ns = GeoHandler.GeoHandler.GEO_SOUTH

    if "longitude_deg_dec" in row:
        if row["longitude_deg_dec"] != '':
            longitude_degrees_decimal = row["longitude_deg_dec"]
            long_string = str(longitude_degrees_decimal)
            long_string = long_string.replace(',', '.')
            cardinal_point = None
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

    if "longitude_min_sec" in row:
        deg_min_sec_dict = {'deg': None, 'min': None, 'sec': None}
        if (row["longitude_min_sec"] != '') and (row["longitude_min_sec"] is not None):
            longitude_min_sec = row["longitude_min_sec"]
            longitude_min_sec_split = longitude_min_sec.split('°')
            deg_min_sec_dict['deg'] = float(longitude_min_sec_split[0])

            longitude_min_sec_part = longitude_min_sec_split[-1]
            longitude_min_sec_part = (longitude_min_sec_part.strip())
            for char in longitude_min_sec_part:
                if char.isalpha():
                    longitude_min_sec_part = longitude_min_sec_part.replace(char, '')
                    if char.lower() == 'e':
                        curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_EAST
                    elif char.lower() == 'w':
                        curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_WEST

            longitude_min_sec_part = longitude_min_sec_part.replace('"', '')
            longitude_min_sec_part_split = longitude_min_sec_part.split("'")
            deg_min_sec_dict['min'] = float(longitude_min_sec_part_split[0])
            if len(longitude_min_sec_part_split) == 2:
                deg_min_sec_dict['sec'] = float(longitude_min_sec_part_split[1])
            curr_geo_handler.longitude_deg_min_sec_dict = deg_min_sec_dict

    if "e/w" in row:
        if (row["e/w"] != '') and (row["e/w"] is None):
            lat_cardinal = row['e/w']
            lat_cardinal = (str(lat_cardinal).lower()).strip()
            if lat_cardinal == 'e':
                curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_NORTH
            elif lat_cardinal == 'w':
                curr_geo_handler.long_ew = GeoHandler.GeoHandler.GEO_SOUTH

    curr_geo_handler.process()
    row["latitude_deg_dec"] = curr_geo_handler.get_latitude(GeoHandler.GeoHandler.DEGREES_DECIMAL_FORMAT)
    row["latitude_min_sec"] = curr_geo_handler.get_latitude(GeoHandler.GeoHandler.DEGREES_MIN_SEC_FORMAT)
    row["longitude_deg_dec"] = curr_geo_handler.get_longitude(GeoHandler.GeoHandler.DEGREES_DECIMAL_FORMAT)
    row["longitude_min_sec"] = curr_geo_handler.get_longitude(GeoHandler.GeoHandler.DEGREES_MIN_SEC_FORMAT)
    row["n/s"] = curr_geo_handler.lat_ns
    row["e/w"] = curr_geo_handler.long_ew
    return row


def normalize(file_name, specs, formats):
    normalized_rows = []
    with open(specs) as the_specs:
        template_specs = json.load(the_specs)
    header_names = template_specs["header_list"]
    type_dict = {}
    for num in range(len(header_names)):
        type_dict[num] = str
    dt_frames = pd.read_excel(file_name, names=header_names, converters=type_dict)
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

    workbook = openpyxl.load_workbook(filename)
    wk_sheet = workbook.active
    with open(specs) as the_specs:
        template_specs = json.load(the_specs)
    row = int(template_specs["header_row"])+1
    for dict_item in row_list:
        for key, value in dict_item.items():
            cell = template_specs["fields"][key]["column_letter"] + str(row)
            wk_sheet[cell] = value
        row += 1
    parent_dir = pathlib2.Path(f_path.parent)
    save_path = str(parent_dir.joinpath('_normalized'+'-'+fname))
    workbook.save(save_path)
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
