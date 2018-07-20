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


def generate_sample_input_map(json_template):
    """This function takes in the json template for the template file,
    and generates a JSON input map for the input file by asking the user questions."""
    return_dict = {"mappings":{}, "header_row":1, "header_list":[], "formats":{}}
    with open(json_template, 'r') as template_json:
        json_template_contents = json.load(template_json)
    header_name_list = json_template_contents["header_list"]
    for item in header_name_list:
        seek_format = False
        if(item=='date' or item=='datetime' or item=='time'):
            seek_format = True
        correct_input = False
        while (not(correct_input)):
            col = raw_input("\nWhich column contains the "+item+"? (Use number or excel column letter)")
            col = col.strip()
            if(col.isdigit()):
                print("Column number entered.")
                correct_input = True
                return_dict["mappings"][item] = int(col)
                #return_dict["header_list"].append(item)
                if(seek_format):
                    valid_format = False
                    while(not(valid_format)):
                        fmt = raw_input("Enter the format for "+item+" (using Python datetime style.)")
                        fmt.strip()
                        if('%' in fmt) and (fmt != ''):
                            valid_format=True
                            return_dict['formats'][item] = fmt.strip()
                        else:
                            print("Invalid format entered.")
            elif(col.isalpha()):
                print("Column letter entered.")
                correct_input = True
                col_num = openpyxl.utils.column_index_from_string(col)
                return_dict["mappings"][item] = col_num
                #return_dict["header_list"].append(item)
                if seek_format :
                    fmt = raw_input("Enter the format for "+item+" (using Python datetime style.)")
                    if('%' in fmt) and (fmt != ''):
                        return_dict['formats'][item] = fmt.strip()
            elif col == '':
                print("No column entered, meaning field is not present")
                correct_input = True
            else:
                print("Invalid entry please enter either a valid number for the column of the excel style column")
    header_row=raw_input("What row in the file contains the column headings?")
    if (header_row.strip() != '1') and (header_row != '') and (header_row.isdigit()):
        header_row=int(header_row)
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
    data = generate_sample_input_map(TEMPLATE_FILE)

    with open(SPEC_FILE, "w") as data_file:
        json.dump(data, data_file, indent=2)
    return


#main()






