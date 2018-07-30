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
    if row["datetime"] != '':
        dt_time = row["datetime"]
        try:
            curr_dt_handler.date_time = datetime.datetime.strptime(dt_time, formats["datetime_format"])
        except Exception as e:
            print("Provided format for reading datetime failed in normalizer, will use default format {}"
                  .format(DEFAULT_DATETIME_FORMAT))
            formats["datetime_format"]=DEFAULT_DATETIME_FORMAT
            curr_dt_handler.date_time = datetime.datetime.strptime(dt_time, DEFAULT_DATETIME_FORMAT)

    else:
        if row["date"] != '':
            dt = row["date"]
            try:
                curr_dt_handler.date = (datetime.datetime.strptime(dt, formats["date_format"])).date()
            except Exception as e:
                print("Provided format for reading date failed in normalizer, will use default format {}".
                      format(DEFAULT_DATE_FORMAT))
                formats["datetime_format"] = DEFAULT_DATE_FORMAT
                curr_dt_handler.date = (datetime.datetime.strptime(dt, formats["date_format"])).date()

        else:
            if row["day"] != '':
                day = int(row["day"])
                curr_dt_handler.day = day
            if row["month"] != '':
                month = int(row["month"])
                curr_dt_handler.month = month
            if row["year"] != '':
                yr = int(row["year"])
                curr_dt_handler.year = yr
        if row["time"] != '':
            t = row["time"]
            try:
                curr_dt_handler.time = (datetime.datetime.strptime(t, formats["time_format"])).time()
            except Exception as e:
                print("Provided format for reading time in normalizer, will use default format {}".
                      format(DEFAULT_TIME_FORMAT))
                formats["datetime_format"] = DEFAULT_TIME_FORMAT
                curr_dt_handler.time = (datetime.datetime.strptime(t, formats["time_format"])).time()

        else:
            if row["hour"] != '':
                hr = int(row["hour"])
                curr_dt_handler.hour = hr
            if row["minute"] != '':
                minute_val = float(row["minute"])
                minute_val = int(minute_val)
                curr_dt_handler.minute = minute_val
            if row["seconds"] != '':
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

    return row


def geo_data_work(row):
    curr_geo_handler = GeoHandler.GeoHandler()
    curr_geo_handler.process()
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
