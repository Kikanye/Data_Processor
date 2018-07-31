"""This script will get data from a specified spreadsheet and load it into a specified output sheet.
   This script will use a .ini file which will have """
import csv
import openpyxl, configparser
import json
import datetime
import pandas as pd
import pathlib2

Config = configparser.ConfigParser()
Config.read("Formats_Settings.ini")

DEFAULT_DATE_FORMAT = Config.get('DATALOADER_FORMATS', 'date')
DEFAULT_DATETIME_FORMAT = Config.get('DATALOADER_FORMATS', 'datetime')
DEFAULT_TIME_FORMAT = Config.get('DATALOADER_FORMATS', 'time')
DEFAULT_UNKNOWN = 'UNKNOWN-'

def handle_csv_input(filename, input_specs):
    with open(input_specs) as j_maps:
        test_dict = json.load(j_maps)

    data = pd.read_csv(filename)
    rows, cols = data.shape
    header_names = [DEFAULT_UNKNOWN]*cols

    count = 0
    for item in header_names:
        header_names[count] = item+str(count)
        count += 1
    for key, value in test_dict['mappings'].items():
        if(value>cols):
            print(" The field {} was specified to be at {}, but this is out of the range in the input file.".
                  format(key, value))
        else:
            header_names[int(value)-1] = key
    data.columns = header_names

    formats={}
    formats_present=False
    if(test_dict.has_key("formats")):
        formats = test_dict["formats"]
        if(bool(formats)):
            formats_present = True

    # TODO: Consider making this more modular, instead of using the "dates", "time" and "datetime" as the keys.
    if ("date" in header_names):
        if ((formats_present)and formats.has_key("date")):
            date_format=formats["date"]
            try:
                data["date"] = pd.to_datetime(data["date"], format=date_format)
            except Exception as e:
                print(e)
                print("Failed to read in date using format {}\n Will try to infer the format".format(date_format))
                data["date"] = pd.to_datetime(data["date"])
        else:
            data["date"] = pd.to_datetime(data["date"])
    if ("time" in header_names):
        do_ampm = False
        if 'am/pm' in header_names:
            do_ampm = True
        if ((formats_present)and formats.has_key("time")):
            time_format = formats["time"]
            try:
                data["time"] = pd.to_datetime(data["time"], format=time_format)
            except Exception as e:
                print(e)
                print("Failed to read in time using format {}\n Will try to infer the format".format(time_format))
                data["time"] = pd.to_datetime(data["time"])
        else:
            data["time"] = pd.to_datetime(data["time"])
        if do_ampm:
            time_list = data['time'].tolist()
            ampm_list = data['am/pm'].tolist()
            curr_index = 0
            for item in time_list:
                pos = curr_index
                if (str(ampm_list[pos]).lower()).strip() == 'pm':
                    print("Time {} at position {} is pm".format(item, pos))
                    time_list[pos] = time_list[pos] + datetime.timedelta(hours=12)
                curr_index += 1
            time_series = pd.Series(time_list)
            data['time'] = time_series
    if ("datetime" in header_names):
        if ((formats_present)and formats.has_key("datetime")):
            datetime_format = formats["datetime"]
            try:
                data["datetime"] = pd.to_datetime(data["datetime"], format=datetime_format)
            except Exception as e:
                print(e)
                print("Failed to read in datetime using format {}\n Will try to infer the format"
                      .format(datetime_format))
                data["datetime"] = pd.to_datetime(data["datetime"])
        else:
            data["datetime"] = pd.to_datetime(data["datetime"])
    data=data.where(pd.notnull(data), None)
    data_list = data.to_dict('records')
    return data_list


def handle_xlsx_input(filename, input_specs):
    with open(input_specs) as j_maps:
        test_dict = json.load(j_maps)

    d_frames = pd.read_excel(filename, sheet_name=None)
    rows, cols = d_frames.shape
    header_names = [DEFAULT_UNKNOWN]*cols

    count = 0
    for item in header_names:
        header_names[count] = item+str(count)
        count += 1
    for key, value in test_dict['mappings'].items():
        header_names[int(value)-1] = key
    d_frames.columns = header_names

    formats_present = False
    if (test_dict.has_key("formats")):
        formats = test_dict["formats"]
        if (bool(formats)):
            formats_present = True

        if ("date" in header_names):
            if (not ((d_frames["date"].dtype == datetime.date) or (d_frames["date"].dtype == datetime.datetime))):
                if ((formats_present) and formats.has_key("date")):
                    date_format = formats["date"]
                    try:
                        d_frames["date"] = pd.to_datetime(d_frames["date"], format=date_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in date using the format {}\n Will try to infer the format."
                              .format(date_format))
                        d_frames["date"] = pd.to_datetime(d_frames["date"])
                else:
                        d_frames["date"] = pd.to_datetime(d_frames["date"])

        if ("time" in header_names):
            if (not ((d_frames["time"].dtype == datetime.time) or (d_frames["time"].dtype == datetime.datetime))):
                if ((formats_present) and formats.has_key("time")):
                    time_format = formats["time"]
                    try:
                        d_frames["time"] = pd.to_datetime(d_frames["time"], format=time_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in the time using the format {}\n Will try to infer the format."
                              .format(time_format))
                        d_frames["time"] = pd.to_datetime(d_frames["time"])
                else:
                        d_frames["time"] = pd.to_datetime(d_frames["time"])

        if ("datetime" in header_names):
            if (not (d_frames["datetime"].dtype == datetime.datetime)):
                if ((formats_present) and formats.has_key("datetime")):
                    datetime_format = formats["datetime"]
                    try:
                        d_frames["datetime"] = pd.to_datetime(d_frames["datetime"], format=datetime_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in the datetime using the format {}\n Will try to infer the format."
                              .format(datetime_format))
                        d_frames["datetime"] = pd.to_datetime(d_frames["datetime"])
                else:
                        d_frames["datetime"] = pd.to_datetime(d_frames["datetime"])

    d_frames = d_frames.where(pd.notnull(d_frames), None)
    data_list = d_frames.to_dict('records')
    return data_list


def get_input(filename, input_map):
    print("Reading input from {}".format(filename))
    the_path=pathlib2.Path(filename)
    fname = the_path.name
    filename_split = fname.split('.')

    input_list=[]
    if filename_split[-1] == 'csv':
        input_list=handle_csv_input(filename, input_map)
    elif filename_split[-1] == 'xls' or filename_split[-1] == 'xlsx':
        input_list=handle_xlsx_input(filename, input_map)
    else:
        print("Invalid file type, must be '.csv' or '.xlsx' ")

    return input_list


def process_input(list_of_rows, output_template):
    # TODO: Find someway to not use literals when comparing keys
    out_list=[]
    with open(output_template) as j_temp_specs:
        template_specs = json.load(j_temp_specs)
    row_template = template_specs["row_template"]
    count=0
    for dictionary in list_of_rows:
        count += 1
        curr_row = row_template.copy()
        for key, value in dictionary.items():
            if(not(DEFAULT_UNKNOWN in key)):
                if "date" == key and (value is not pd.NaT) and (value is not None):
                    value=value.strftime(DEFAULT_DATE_FORMAT)
                elif "time" == key and (value is not pd.NaT) and (value is not None):
                    value=value.strftime(DEFAULT_TIME_FORMAT)
                elif "datetime" == key and (value is not pd.NaT) and (value is not None):
                    value=value.strftime(DEFAULT_DATETIME_FORMAT)
                curr_row[key] = value
            else:
                del dictionary[key]
        out_list.append(curr_row)
    return out_list


def handle_xlsx_output(filename, out_list, in_filename, output_specs):
    with open(output_specs) as o_specs:
        template_specs = json.load(o_specs)

    inf_path = pathlib2.Path(in_filename)
    infile_split = (inf_path.name).split('.')
    inf=infile_split[0]

    out_path = pathlib2.Path(filename)

    workbook = openpyxl.load_workbook(filename)
    wk_sheet = workbook.active
    row = int(template_specs["header_row"])+1
    for dict_item in out_list:
        for key, value in dict_item.items():
            cell = template_specs["fields"][key]["column_letter"] + str(row)
            wk_sheet[cell] = value
        row += 1
    parent_dir = pathlib2.Path(out_path.parent)
    saved_path = str(parent_dir.joinpath(inf+'-'+out_path.name))
    workbook.save(saved_path)
    return saved_path


def handle_csv_output():
    # TODO: Use this function to load  the processed input into a .csv formatted output.
    return


def load_output(dictionary_list, filename, in_filename, output_specs):
    return_val=''
    the_path = pathlib2.Path(filename)
    fname = the_path.name
    filename_split = fname.split('.')
    if(filename_split[-1]=='xlsx'):
        return_val=handle_xlsx_output(filename, dictionary_list, in_filename, output_specs)
    return return_val


def transfer_values(inputfile, outputfile, mappings_file, template_json):
    """This function will move the values in inputfile to outputfile accurately, based on the mappings_file and
       template_json specifications."""

    input_rows = get_input(inputfile, mappings_file)
    output_rows = process_input(input_rows, template_json)
    saved_path = load_output(output_rows, outputfile, inputfile, template_json)
    return saved_path


def main():
    print("Getting specifications from config. file")
    Config=configparser.ConfigParser()
    Config.read("DataLoader_Config.ini")

    INPUT_FILE = Config.get('INPUT', 'I_FILE')
    INPUT_SPEC = Config.get('INPUT', 'MAPPINGS_FILE')
    OUTPUT_FILE = Config.get('OUTPUT', 'O_FILE')
    OUT_SPEC=Config.get('OUTPUT', 'FIELDS')
    print("Moving data from {} into {}".format(INPUT_FILE, OUTPUT_FILE))
    transfer_values(INPUT_FILE, OUTPUT_FILE, INPUT_SPEC, OUT_SPEC)
    print("End of Processing")
    return

