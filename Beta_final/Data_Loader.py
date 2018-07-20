"""This script will get data from a specified spreadsheet and load it into a specified output sheet.
   This script will use a .ini file which will have """
import csv
import openpyxl, configparser, datetime
import json
import datetime
import pandas as pd, numpy as np
import pathlib2, shutil

def handle_csv_input(filename, input_specs):
    with open(input_specs) as j_maps:
        test_dict = json.load(j_maps)
    header_names = test_dict["header_list"]
    data = pd.read_csv(filename, header=None, names=header_names, skiprows=int(test_dict['header_row']))
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
            data["date"] = pd.to_datetime(data["date"], format=date_format)
        else:
            data["date"] = pd.to_datetime(data["date"])
    if ("time" in header_names):
        if ((formats_present)and formats.has_key("time")):
            time_format = formats["time"]
            data["time"] = pd.to_datetime(data["time"], format=time_format)
        else:
            data["time"] = pd.to_datetime(data["time"])
    if ("datetime" in header_names):
        if ((formats_present)and formats.has_key("datetime")):
            datetime_format = formats["datetime"]
            data["datetime"] = pd.to_datetime(data["datetime"], format=datetime_format)
        else:
            data["datetime"] = pd.to_datetime(data["datetime"])
    data=data.where(pd.notnull(data), None)
    data_list = data.to_dict('records')
    return data_list


def handle_xlsx_input(filename, input_specs):
    with open(input_specs) as j_maps:
        test_dict = json.load(j_maps)
    header_names = test_dict["header_list"]
    d_frames = pd.read_excel(filename, header=None, names=header_names, sheet_name=None,
                             skiprows=int(test_dict['header_row']))
    formats = {}
    formats_present = False
    if (test_dict.has_key("formats")):
        formats = test_dict["formats"]
        if (bool(formats)):
            formats_present = True

        if ("date" in header_names):
            if ((formats_present) and formats.has_key("date")):
                if (not ((d_frames["date"].dtype == datetime.date) or (d_frames["date"].dtype == datetime.datetime))):
                    date_format = formats["date"]
                    d_frames["date"] = pd.to_datetime(d_frames["date"], format=date_format)
            else:
                if (not ((d_frames["date"].dtype == datetime.date) or (d_frames["date"].dtype == datetime.datetime))):
                    d_frames["date"] = pd.to_datetime(d_frames["date"])

        if ("time" in header_names):
            if ((formats_present) and formats.has_key("time")):
                if (not ((d_frames["time"].dtype == datetime.time) or (d_frames["time"].dtype == datetime.datetime))):
                    time_format = formats["time"]
                    d_frames["time"] = pd.to_datetime(d_frames["time"], format=time_format)
            else:
                if (not ((d_frames["time"].dtype == datetime.time) or (d_frames["time"].dtype == datetime.datetime))):
                    d_frames["time"] = pd.to_datetime(d_frames["time"])

        if ("datetime" in header_names):
            if ((formats_present) and formats.has_key("datetime")):
                if (not (d_frames["datetime"].dtype == datetime.datetime)):
                    datetime_format = formats["datetime"]
                    d_frames["datetime"] = pd.to_datetime(d_frames["datetime"], format=datetime_format)
            else:
                if (not (d_frames["datetime"].dtype == datetime.datetime)):
                    d_frames["datetime"] = pd.to_datetime(d_frames["datetime"])
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
        raise Exception("Invalid file type, must be '.csv' or '.xlsx' ")
    return input_list


def process_input(list_of_rows, output_template):
    out_list=[]
    with open(output_template) as j_temp_specs:
        template_specs = json.load(j_temp_specs)
    row_template = template_specs["row_template"]
    count=0
    for dictionary in list_of_rows:
        count+=1
        curr_row = row_template.copy()
        for key, value in dictionary.items():
            if "date" == key and (value is not pd.NaT) and (value is not None):
                value=value.strftime("%d-%m-%Y")
            elif "time" == key and (value is not pd.NaT) and (value is not None):
                value=value.strftime("%I:%M:%S%p")
            elif "datetime" == key and (value is not pd.NaT) and (value is not None):
                value=value.strftime("%d-%m-%Y %I:%M:%S%p")
            curr_row[key] = value
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
    #filename_split = filename.split('.')
    if(filename_split[-1]=='xlsx'):
        return_val=handle_xlsx_output(filename, dictionary_list, in_filename, output_specs)
    return return_val


def transfer_values(inputfile, outputfile, mappings_file, template_json, output_directory):
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


#print("Loading data into template.")
#main()
#print("Data loading into template complete.")

