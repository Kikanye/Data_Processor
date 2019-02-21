"""
This script contains functions that will help with the process of getting data from an input source file and loading
it into a specified template file.

Functions from this script are called by the scripts which setup the variables needed for this to work.
"""

import openpyxl, configparser
import json
import datetime
import pandas as pd
import pathlib2

# Open file which contains the formats for the date/time and load them into variables.
Config = configparser.ConfigParser()
Config.read("Formats_Settings.ini")

DEFAULT_DATE_FORMAT = Config.get('DATALOADER_FORMATS', 'date')
DEFAULT_DATETIME_FORMAT = Config.get('DATALOADER_FORMATS', 'datetime')
DEFAULT_TIME_FORMAT = Config.get('DATALOADER_FORMATS', 'time')
DEFAULT_UNKNOWN = 'UNKNOWN-'  # This string will be used as the default header for columns.

NO_HEADER_ROW_INDICATOR = 0  # Use this if there is no header row in the file.
DEFAULT_HEADER_ROW_NUMBER = 1  # The default row to use as the header row.


def handle_csv_input(filename, input_specs):
    """
    ->'filename': The path to the file that needs to be processed.
    ->'input_specs': The path to the json map file for the file that needs to be processed.
    This function will process the contents of 'filename' using the json specification in 'input_specs'.
     It will read in the contents into a dataframe and return a list of dictionaries,
    where each dictionary represents a row from the original data file.
    """

    # Open and read the contents of the json file into a variable.
    with open(input_specs) as j_maps:
        map_dict = json.load(j_maps)

    # Get the specification for which row contains the headings in the file
    data = None
    file_header_column = int(map_dict['header_row'])
    # Decide how to read in the file based on the header specification.
    if file_header_column <= NO_HEADER_ROW_INDICATOR:
        data = pd.read_csv(filename, header=None)
    elif file_header_column == 1:
        data = pd.read_csv(filename)
    elif file_header_column > 1:
        # If the header row is not the first, do this
        data = pd.read_csv(filename, header=file_header_column-1)

    # Get the number of rows and columns and generate a list containing default header names.
    rows, cols = data.shape
    header_names = [DEFAULT_UNKNOWN]*cols

    # Change the default header names to the actual header names as specified in the json specification data.
    count = 0
    for item in header_names:
        header_names[count] = item+str(count)
        count += 1
    for key, value in map_dict['mappings'].items():
        if value > cols:
            print(" \nThe field {} was specified to be at {}, but this is out of the range in the input file.".
                  format(key, value))
        else:
            header_names[int(value)-1] = key
    data.columns = header_names

    # Check to see if formats are present and generate a boolean value that says so.
    formats = {}
    formats_present = False
    if "formats" in map_dict:
        formats = map_dict["formats"]
        if bool(formats):
            # TODO: This boolean value here may be redundant
            formats_present = True

    # TODO: Consider making this more modular, instead of using the "dates", "time" and "datetime" as the keys.

    # Check to see if the data/time and/or datetime columns are available and process them
    # If the formats for the dates and times are specified, use that else try to infer the format.
    if "date" in header_names:
        if formats_present and "date" in formats:
            date_format = formats["date"]
            try:
                data["date"] = pd.to_datetime(data["date"], format=date_format)
            except Exception as e:
                print(e)
                print("Failed to read in date using format {}\n Will try to infer the format".format(date_format))
                data["date"] = pd.to_datetime(data["date"])
        else:
            data["date"] = pd.to_datetime(data["date"])

    if "time" in header_names:
        if formats_present and "time" in formats:
            time_format = formats["time"]
            try:
                data["time"] = pd.to_datetime(data["time"], format=time_format)
            except Exception as e:
                print(e)
                print("Failed to read in time using format {}\n Will try to infer the format".format(time_format))
                data["time"] = pd.to_datetime(data["time"])
        else:
            data["time"] = pd.to_datetime(data["time"])

    if "datetime" in header_names:
        if formats_present and "datetime" in formats:
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
    # Change null values to None and then convert the dataframe to a list of dictionaries and return.
    data = data.where(pd.notnull(data), None)
    data_list = data.to_dict('records')
    return data_list


def handle_xlsx_input(filename, input_specs):
    with open(input_specs) as j_maps:
        test_dict = json.load(j_maps)
    d_frames=None
    file_header_column = int(test_dict['header_row'])
    if file_header_column <= NO_HEADER_ROW_INDICATOR:
        d_frames = pd.read_excel(filename, sheet_name=None, header=None)
    elif file_header_column == DEFAULT_HEADER_ROW_NUMBER:
        d_frames = pd.read_excel(filename, sheet_name=None)
    elif file_header_column > DEFAULT_HEADER_ROW_NUMBER:
        d_frames = pd.read_excel(filename, sheet_name=None, header=file_header_column-1)
    rows, cols = d_frames.shape
    header_names = [DEFAULT_UNKNOWN]*cols

    count = 0
    for item in header_names:
        header_names[count] = item+str(count)
        count += 1
    for key, value in test_dict['mappings'].items():
        value = int(value)
        pos_val=value-1
        if pos_val < len(header_names):
            header_names[pos_val] = key
    d_frames.columns = header_names

    formats_present = False
    if (test_dict.has_key("formats")):
        formats = test_dict["formats"]
        if (bool(formats)):
            formats_present = True

        if ("date" in header_names):
            type_get = d_frames['date'].apply(type)
            type_test = (type_get == datetime.datetime).all() or (type_get == datetime.date).all()

            if not(type_test):
                if ((formats_present) and formats.has_key("date")):
                    date_format = formats["date"]
                    try:
                        d_frames["date"] = pd.to_datetime(d_frames["date"], format=date_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in date using the format {}\n Will try to infer the format."
                              .format(date_format))
                        d_frames["date"] = pd.to_datetime(d_frames["date"], errors='coerce')
                else:
                    d_frames["date"] = pd.to_datetime(d_frames["date"], errors='coerce')

        if ("time" in header_names):
            type_get = d_frames['time'].apply(type)
            type_test = (type_get == datetime.datetime).all() or (type_get == datetime.time).all()

            if not(type_test):
                if ((formats_present) and formats.has_key("time")):
                    time_format = formats["time"]
                    try:
                        d_frames["time"] = pd.to_datetime(d_frames["time"], format=time_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in the time using the format {}\n Will try to infer the format."
                              .format(time_format))
                        d_frames["time"] = pd.to_datetime(d_frames["time"], errors='coerce')
                else:
                    d_frames["time"] = pd.to_datetime(d_frames["time"], errors='coerce')

        if ("datetime" in header_names):
            type_get = d_frames["datetime"].apply(type)
            type_test = (type_get == datetime.datetime).all()

            if not(type_test):
                if ((formats_present) and formats.has_key("datetime")):
                    datetime_format = formats["datetime"]
                    try:
                        d_frames["datetime"] = pd.to_datetime(d_frames["datetime"], format=datetime_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in the datetime using the format {}\n Will try to infer the format."
                              .format(datetime_format))
                        d_frames["datetime"] = pd.to_datetime(d_frames["datetime"], errors='coerce')
                else:
                    d_frames["datetime"] = pd.to_datetime(d_frames["datetime"], errors='coerce')

    d_frames = d_frames.where(pd.notnull(d_frames), None)
    data_list = d_frames.to_dict('records')
    return data_list


def get_input(filename, input_map):
    print("\nReading input from {}".format(filename))
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
    print("Processing input gotten from the file...")
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


def handle_csv_output(filename, outlist, in_filename, output_specs):
    # TODO: Use this function to load  the processed input into a .csv formatted output.


    return


def load_output(dictionary_list, filename, in_filename, output_specs):
    print("Loading processed data into {}".format(filename))
    return_val=''
    the_path = pathlib2.Path(filename)
    fname = the_path.name
    filename_split = fname.split('.')
    if(filename_split[-1]=='xlsx'):
        return_val=handle_xlsx_output(filename, dictionary_list, in_filename, output_specs)
    #TODO: Haldle csv files here.
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

