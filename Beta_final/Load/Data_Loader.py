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
    :param filename: The path to the .csv file that needs to be processed.
    :param input_specs: The path to the json map file for the file that needs to be processed.
    :return: A list of dictionaries, where each dictionary represents a row from the original data file

    This function will process the contents of 'filename' (which must be a .csv file).
    It will use the json specifications in 'input_specs'.
    It will read in the contents into a dataframe and process them into a list of dictionaries.
    """

    # Open and read the contents of the json file into a variable.
    with open(input_specs) as j_maps:
        map_dict = json.load(j_maps)

    # Get the specification for which row contains the headings in the file
    data_frame = None  # This will be the data_frame containing the data from 'filename'
    file_header_row = int(map_dict['header_row'])
    # Decide how to read in the file based on the header specification.
    if file_header_row <= NO_HEADER_ROW_INDICATOR:
        data_frame = pd.read_csv(filename, header=None)
    elif file_header_row == DEFAULT_HEADER_ROW_NUMBER:
        data_frame = pd.read_csv(filename)
    elif file_header_row > DEFAULT_HEADER_ROW_NUMBER:
        # If the header row is not the first, do this
        data_frame = pd.read_csv(filename, header=file_header_row-1)

    # Get the number of rows and columns and generate a list containing default header names.
    rows, cols = data_frame.shape
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
    data_frame.columns = header_names

    # Check to see if formats are present and generate a boolean value that says so.
    formats = {}
    formats_present = False
    if "formats" in map_dict:
        formats = map_dict["formats"]
        if bool(formats):
            # TODO: This boolean value here may be redundant
            formats_present = True

    # TODO: Consider making this more modular, instead of using the "dates", "time" and "datetime" as the keys.

    # Check to see if the date/time and/or datetime columns are available and process them
    # If the formats for the dates and times are specified use them, if not try to infer the format.
    if "date" in header_names:
        if formats_present and "date" in formats:
            date_format = formats["date"]
            try:
                data_frame["date"] = pd.to_datetime(data_frame["date"], format=date_format)
            except Exception as e:
                print(e)
                print("Failed to read in date using format {}\n Will try to infer the format".format(date_format))
                data_frame["date"] = pd.to_datetime(data_frame["date"])
        else:
            data_frame["date"] = pd.to_datetime(data_frame["date"])

    if "time" in header_names:
        if formats_present and "time" in formats:
            time_format = formats["time"]
            try:
                data_frame["time"] = pd.to_datetime(data_frame["time"], format=time_format)
            except Exception as e:
                print(e)
                print("Failed to read in time using format {}\n Will try to infer the format".format(time_format))
                data_frame["time"] = pd.to_datetime(data_frame["time"])
        else:
            data_frame["time"] = pd.to_datetime(data_frame["time"])

    if "datetime" in header_names:
        if formats_present and "datetime" in formats:
            datetime_format = formats["datetime"]
            try:
                data_frame["datetime"] = pd.to_datetime(data_frame["datetime"], format=datetime_format)
            except Exception as e:
                print(e)
                print("Failed to read in datetime using format {}\n Will try to infer the format"
                      .format(datetime_format))
                data_frame["datetime"] = pd.to_datetime(data_frame["datetime"])
        else:
            data_frame["datetime"] = pd.to_datetime(data_frame["datetime"])
    # Change null values to None and then convert the dataframe to a list of dictionaries and return.
    data_frame = data_frame.where(pd.notnull(data_frame), None)
    data_list = data_frame.to_dict('records')
    return data_list


def handle_xlsx_input(filename, input_specs):
    """

    :param filename: The path to the excel file which needs to be processed.
    :param input_specs: The path to the json map for the input file that needs to be processed.
    :return: A list of dictionaries where each dictionary represents a row from the input file being processed.

    This function will process the contents of 'filename' (which must be an excel file).
    It will use the json specifications in 'input_specs'.
    It will read in the contents into a dataframe and process them into a list of dictionaries.
    """

    # Open and read the contents of the json specification file.
    with open(input_specs) as j_maps:
        test_dict = json.load(j_maps)

    # Get the specification for which row contains the headings in the file.
    d_frame = None  # This will be the dataframe containing the data from 'filename'
    file_header_row = int(test_dict['header_row'])
    # Decide how to read in the file based on which row contains the header.
    if file_header_row <= NO_HEADER_ROW_INDICATOR:
        d_frame = pd.read_excel(filename, sheet_name=None, header=None)
    elif file_header_row == DEFAULT_HEADER_ROW_NUMBER:
        d_frame = pd.read_excel(filename, sheet_name=None)
    elif file_header_row > DEFAULT_HEADER_ROW_NUMBER:
        # If the header row is not the first, do this.
        d_frame = pd.read_excel(filename, sheet_name=None, header=file_header_row-1)

    # Get the number of rows and columns and generate a list containing default header names.
    rows, cols = d_frame.shape
    header_names = [DEFAULT_UNKNOWN]*cols

    # Change the default header names to the actual header names as specified in the json specification data.
    count = 0
    for item in header_names:
        header_names[count] = item+str(count)
        count += 1
    for key, value in test_dict['mappings'].items():
        value = int(value)
        pos_val = value-1
        if pos_val < len(header_names):
            header_names[pos_val] = key
    d_frame.columns = header_names

    # Check to see if formats are present and generate a boolean value that says so.
    formats_present = False
    if "formats" in test_dict:
        formats = test_dict["formats"]
        if bool(formats):
            # TODO: This boolean value here may be redundant
            formats_present = True

        # TODO: Consider making this more modular, instead of using the "dates", "time" and "datetime" as the keys.
        if "date" in header_names:

            # Make a data series containing all the types of the data in the 'date' column
            #  (which is a series in the d_frame) and check to ensure that they are all can all of datetime type.
            type_get = d_frame['date'].apply(type)
            type_test = (type_get == datetime.datetime).all() or (type_get == datetime.date).all()

            # If the data in the field was not of type datetime, do this.
            # Try to convert into datetime using the formats specified, if that fails,
            # Infer the formats of the 'date' field
            # Use the function pd.to_datetime to convert the fields to dates.
            # errors='coerce' will force values that cannot be converted correctly to be NaT.
            if not(type_test):
                if formats_present and "date" in formats:
                    date_format = formats["date"]
                    try:
                        d_frame["date"] = pd.to_datetime(d_frame["date"], format=date_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in date using the format {}\n Will try to infer the format."
                              .format(date_format))
                        d_frame["date"] = pd.to_datetime(d_frame["date"], errors='coerce')
                else:
                    d_frame["date"] = pd.to_datetime(d_frame["date"], errors='coerce')

        if "time" in header_names:
            # Make a data series containing all the types of the data in the 'time' column
            #  (which is a series in the d_frame) and check to ensure that they are all can all of datetime type.
            type_get = d_frame['time'].apply(type)
            type_test = (type_get == datetime.datetime).all() or (type_get == datetime.time).all()

            # If the data in the field was not of type datetime, do this.
            # Try to convert into datetime using the formats specified, if that fails,
            # Infer the formats of the 'time' field
            # Use the function pd.to_datetime to convert the values in the field to times.
            # errors='coerce' will force values that cannot be converted correctly to be NaT.
            if not(type_test):
                if formats_present and "time" in formats:
                    time_format = formats["time"]
                    try:
                        d_frame["time"] = pd.to_datetime(d_frame["time"], format=time_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in the time using the format {}\n Will try to infer the format."
                              .format(time_format))
                        d_frame["time"] = pd.to_datetime(d_frame["time"], errors='coerce')
                else:
                    d_frame["time"] = pd.to_datetime(d_frame["time"], errors='coerce')

        if "datetime" in header_names:
            # Make a data series containing all the types of the data in the 'datetime' column
            #  (which is a series in the d_frame) and check to ensure that they are all can all of datetime type.
            type_get = d_frame["datetime"].apply(type)
            type_test = (type_get == datetime.datetime).all()

            # If the data in the field was not of type datetime, do this.
            # Try to convert into datetime using the formats specified, if that fails,
            # Infer the formats of the 'datetime' field
            # Use the function pd.to_datetime to convert the values in the field to datetime.
            # errors='coerce' will force values that cannot be converted correctly to be NaT.
            if not(type_test):
                if formats_present and "datetime" in formats:
                    datetime_format = formats["datetime"]
                    try:
                        d_frame["datetime"] = pd.to_datetime(d_frame["datetime"], format=datetime_format)
                    except Exception as e:
                        print(e)
                        print("Failed to read in the datetime using the format {}\n Will try to infer the format."
                              .format(datetime_format))
                        d_frame["datetime"] = pd.to_datetime(d_frame["datetime"], errors='coerce')
                else:
                    d_frame["datetime"] = pd.to_datetime(d_frame["datetime"], errors='coerce')

    d_frame = d_frame.where(pd.notnull(d_frame), None)
    data_list = d_frame.to_dict('records')
    return data_list


def get_input(filename, input_map):
    """

    :param filename: The path to the file which will be processed.
    :param input_map: The path to the json map for the input file that needs to be processed.
    :return: A list of dictionaries where each dictionary represents a row from the input file being processed.

    This function will process the contents of 'filename'.
    It will call the functions needed to process '.csv' or '.xlsx' files,
    and return a list of dictionaries made from the data in the file.
    """
    print("\nReading input from {}".format(filename))
    the_path = pathlib2.Path(filename)
    fname = the_path.name
    filename_split = fname.split('.')

    # Check the type of the file and call the required function to process the file.
    input_list = []
    if filename_split[-1] == 'csv':
        input_list = handle_csv_input(filename, input_map)
    elif filename_split[-1] == 'xls' or filename_split[-1] == 'xlsx':
        input_list = handle_xlsx_input(filename, input_map)
    else:
        print("Invalid file type, must be '.csv' or '.xlsx' ")

    return input_list


def format_date_and_time(list_of_rows, output_template):
    """

    :param list_of_rows: A list of dictionaries where each dictionary represents a row of data.
    :param output_template: The path to the template file which the data needs to be loaded into.
    :return: A list of dictionaries with the date/time fields formatted according to the specifications of the user.

    This function will format the date/time fields in the 'list_of_rows' with the formats specified by the user or the
    default formats used by the data processor. It will also remove any fields that are UNKNOWN.
    """
    # TODO: Find someway to not use literals when comparing keys
    print("Reformatting date/time fields gotten from the input file...")
    out_list = []
    with open(output_template) as j_temp_specs:
        template_specs = json.load(j_temp_specs)
    row_template = template_specs["row_template"]
    count = 0

    # For each dictionary in 'list_of_rows' go through all the fields,
    # and if there is a date, datetime or time field, reformat it using the format strings specified.
    for dictionary in list_of_rows:
        count += 1
        curr_row = row_template.copy()
        for key, value in dictionary.items():
            if not(DEFAULT_UNKNOWN in key):
                if "date" == key and (value is not pd.NaT) and (value is not None):
                    value = value.strftime(DEFAULT_DATE_FORMAT)
                elif "time" == key and (value is not pd.NaT) and (value is not None):
                    value = value.strftime(DEFAULT_TIME_FORMAT)
                elif "datetime" == key and (value is not pd.NaT) and (value is not None):
                    value = value.strftime(DEFAULT_DATETIME_FORMAT)
                curr_row[key] = value
            else:
                # If the field is still "UNKNOWN" delete it.
                del dictionary[key]
        # Add the processed dictionary to the list that will be returned from this funciton.
        out_list.append(curr_row)
    return out_list


def handle_xlsx_output(filename, out_list, in_filename, output_specs):
    """

    :param filename: The path to the template file where the data in 'out_list' will be loaded into and saved.
    :param out_list: A list of dictionaries, where each dictionary represents a row of data from 'in_filename'.
    :param in_filename: The name of the file where the data in 'out_list' was gotten from.
    :param output_specs: A json file containing the specifications for the fields in the template file 'filename'.
    :return: A string representation of the location (file path) where the output file was saved.

    This function will load data contained in 'out_list' which was gotten from the file 'in_filename'
    into a template file specified by 'filename'.
    """

    # Open and read the contents of the json specifications for the output template.
    with open(output_specs) as o_specs:
        template_specs = json.load(o_specs)

    # Remove the name extension from the name of the input file, and keep that
    inf_path = pathlib2.Path(in_filename)
    infile_split = (inf_path.name).split('.')
    inf = infile_split[0]

    # Load the data in out_list into the template based on the specifications provided in output_specs.
    out_path = pathlib2.Path(filename)
    workbook = openpyxl.load_workbook(filename)
    wk_sheet = workbook.active
    row = int(template_specs["header_row"])+1
    for dict_item in out_list:
        for key, value in dict_item.items():
            cell = template_specs["fields"][key]["column_letter"] + str(row)
            wk_sheet[cell] = value
        row += 1

    # Get the name of the directory where the template was located
    # Name the file with loaded data in the format *in_filename-output_filename.(*extension_of_the template*)*
    # Save the new file into the directory where the template was located.
    parent_dir = pathlib2.Path(out_path.parent)
    saved_path = str(parent_dir.joinpath(inf+'-'+out_path.name))
    workbook.save(saved_path)
    return saved_path


def handle_csv_output(filename, outlist, in_filename, output_specs):
    # TODO: Use this function to load  the processed input into a .csv formatted output.

    return


def load_output(dictionary_list, filename, in_filename, output_specs):
    """

    :param dictionary_list: A list of dictionaries where each dictionary represents a row of data from 'in_filename'.
    :param filename: The name of the template file where the data in "dictionary_list' will be loaded into.
    :param in_filename: The name of the file which the data in dictionary_list was gotten from.
    :param output_specs: A json file containing the field specification for the template 'filename'.
    :return: A string representation for the location (path) where the file generated was saved.

    This function will decide which function to use when loading the processed data into a copy of the templates
    based on the extensin of the template file.
    """
    print("Loading processed data into {}".format(filename))
    return_val = ''
    the_path = pathlib2.Path(filename)
    fname = the_path.name
    filename_split = fname.split('.')
    if filename_split[-1] == 'xlsx':
        return_val = handle_xlsx_output(filename, dictionary_list, in_filename, output_specs)
    else:
        raise Exception("Error occurred while loading data into template\n"
                        " Unknown file extension for the template file.''".format(filename_split[-1]))

    # TODO: Handle csv file templates here eventually.
    return return_val


def transfer_values(input_file, output_file, mappings_file, template_json):
    """

    :param input_file: The file containing the data to be transferred into the template.
    :param output_file: The template which the data from 'input_file' will be loaded into
    :param mappings_file: A json file specifying the formats, header names and the column locations for the fields
           from the 'input_file'.
    :param template_json: A json file specifying the structure of the 'output_file'.
    :return: The location where the file generated by the function was saved.

    This function uses the above functions to process the data and successfully move data from the input file
    into a copy of the template.
    """

    # Get the rows from the input file specified.
    # Process the dates and times
    # Load the processed output in a copy of the template file and save it
    input_rows = get_input(input_file, mappings_file)
    output_rows = format_date_and_time(input_rows, template_json)
    saved_path = load_output(output_rows, output_file, input_file, template_json)
    return saved_path


# TODO: This main() function is currently not being used for anything, will probably end up having to remove it!
def main():
    print("Getting specifications from config. file")
    Config = configparser.ConfigParser()
    Config.read("DataLoader_Config.ini")

    INPUT_FILE = Config.get('INPUT', 'I_FILE')
    INPUT_SPEC = Config.get('INPUT', 'MAPPINGS_FILE')
    OUTPUT_FILE = Config.get('OUTPUT', 'O_FILE')
    OUT_SPEC = Config.get('OUTPUT', 'FIELDS')
    print("Moving data from {} into {}".format(INPUT_FILE, OUTPUT_FILE))
    transfer_values(INPUT_FILE, OUTPUT_FILE, INPUT_SPEC, OUT_SPEC)
    print("End of Processing")
    return

