"""This script will use a .ini file which will have one section NAMED [FILES_INFO] with three (3) fields:
    TEMPLATE_NAME: The filename of the template
    SPEC_FILE: The name of the file which the generated JSON template will be written to
    HEADER_ROW: The row in the file which contains the column headers (this will default to 1 if not specified)
    NOTE: The template file must be a valid '.csv' or '.xlsx' file"""

# TODO: Need to do more extensive testing on this script to make sure that it can handle edge cases.
import json
import openpyxl
#import csv
import configparser

RESET_VALUE='reset'

def get_input(item):
    return_dict = {"column": -1, "format": ''}
    seek_format = False
    if (item == 'date' or item == 'datetime' or item == 'time'):
        seek_format = True
    correct_input = False
    column_specified = False
    while (not (correct_input)):
        col = raw_input("\nWhich column contains the '" + item + "'? (Use number or excel column letter)\n Enter " +
                        "{} to restart your entry, (maybe due to errors)".format(RESET_VALUE.upper()))
        col = col.strip()
        if (col.isdigit()):
            print("Column number entered.")
            correct_input = True
            return_dict["column"] = int(col)
            column_specified = True
        elif col.isalpha():
            col = col.lower()
            if col == RESET_VALUE:
                return col

            print("Column letter entered.")
            col_num = -1
            try:
                col_num = openpyxl.utils.column_index_from_string(col)
                correct_input = True
            except ValueError as ve:
                print(ve)

            return_dict["column"] = col_num
            column_specified = True

        elif col == '':
            print("No column entered, meaning field is not present")
            correct_input = True
        else:
            print("Invalid entry please enter either a valid number for the column of the excel style column")

        if (column_specified and correct_input and seek_format):
            valid_format = False
            while (not (valid_format)):
                fmt = raw_input("Enter the format for " + item + " (using Python datetime style.)")
                fmt.strip()
                if (fmt == ''):
                    valid_format = True
                    print("No format supplied, will try to infer format.")
                elif ('%' in fmt):
                    valid_format = True
                    return_dict["format"] = fmt.strip()
                else:
                    print("Invalid format entered.")

    return return_dict

def handle_headerlist(header_name_list):
    std_dict = {"mappings":{}, "header_row":1, "header_list":[], "formats":{}}
    for item in header_name_list:
        item_info=get_input(item)
        if(item_info==RESET_VALUE):
            return item_info
        column = item_info["column"]
        fmt = item_info["format"]

        if column != -1:
            std_dict["mappings"][item] = column
        if fmt != '':
            std_dict['formats'][item] = fmt

    return std_dict


def generate_input_map(json_template):
    """This function takes in the json template for the template file,
    and generates a JSON input map for the input file by asking the user questions."""
    return_dict = {"mappings":{}, "header_row":1, "header_list":[], "formats":{}}
    with open(json_template, 'r') as template_json:
        json_template_contents = json.load(template_json)
    header_name_list = json_template_contents["header_list"]
    re_processing = True
    while re_processing:
        info = handle_headerlist(header_name_list)
        if info != RESET_VALUE:
            re_processing = False
            return_dict = info

    header_row = raw_input("What row in the file contains the column headings?")
    if (header_row.strip() != '1') and (header_row != '') and (header_row.isdigit()):
        header_row = int(header_row)
        return_dict["header_row"] = header_row
    sorted_headers=sorted(return_dict['mappings'].items(), key=lambda x:(x[1]))
    for item in sorted_headers:
        return_dict["header_list"].append(item[0])
    return return_dict


def main():
    Config = configparser.ConfigParser()
    Config.read('Loader_Config.ini')
    TEMPLATE_FILE = Config.get('TEMPLATE_INFO', 'TEMPLATE_PATH')
    SPEC_FILE = Config.get('TEMPLATE_INFO', 'TEMPLATE_MAP_PATH')
    data = generate_input_map(TEMPLATE_FILE)

    with open(SPEC_FILE, "w") as data_file:
        json.dump(data, data_file, indent=2)
    return


#main()






