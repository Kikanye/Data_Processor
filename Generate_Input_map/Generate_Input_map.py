"""This script will use a .ini file which will have one section NAMED [FILES_INFO] with three (3) fields:
    TEMPLATE_NAME: The filename of the template
    SPEC_FILE: The name of the file which the generated JSON template will be written to
    HEADER_ROW: The row in the file which contains the column headers (this will default to 1 if not specified)
    NOTE: The template file must be a valid '.csv' or '.xlsx' file"""

# TODO: Need to do more extensive testing on this script to make sure that it can handle edge cases.
import json
import openpyxl
import csv
import configparser

def get_csv(filename):
    """This function takes in the name of a '.csv' file and generates a Json dictionary,
       which specifies the fields and columns for the template
       as well as a template dictionary for all the fields in the template.
       [see info.txt for info on the json that is generated.]"""
    data_dict = {}
    with open(filename) as csvfile:
        content_reader = csv.DictReader(csvfile)
        header_names = content_reader.fieldnames
        fields_dict = {}
        row_template = {}
        header_list = []
        for item in header_names:
            # Get the contents of each cell in the header row
            column_dict = {}
            # Determine the column number and letter using the index of the item from the list
            h_val=((item.lower()).strip()).replace(" ", "_")
            header_list.append(h_val)
            col_number = header_names.index(item)+1
            col_letter = openpyxl.utils.get_column_letter(col_number)
            column_dict["column_letter"] = col_letter
            column_dict["column_number"] = col_number
            column_dict["type"] = None
            header_key = h_val
            fields_dict[header_key] = column_dict
            row_template[header_key] = None
        data_dict["fields"] = fields_dict
        data_dict["row_template"] = row_template
        data_dict["header_list"] = header_list
    return data_dict


def get_excel(filename, header_row=1):
    """This function takes in the name of a '.xlsx' file,
     and the number of the row which has the column headers.
     It generates a Json dictionary,
     which specifies the fields and columns for the template
     as well as a template dictionary for all the fields in the template.
     [see info.txt for info on the json that is generated.]"""
    return_dict = {}
    wk_bk=openpyxl.load_workbook(filename)
    wk_sht=wk_bk.active
    try:
        header_loc = int(header_row)
    except Exception as e:
        print(e)
        print("Header row should be a number")
        header_loc=1
    header_row=wk_sht[header_loc]
    fields_dict={}
    row_template={}
    header_list=[]
    for column in header_row:
        column_dict={}
        curr_header=column.value
        h_val=((curr_header.lower()).strip()).replace(" ", "_")
        header_list.append(h_val)
        column_letter=column.column
        column_number=column.col_idx
        column_dict["column_letter"]=column_letter
        column_dict["column_number"]=column_number
        column_dict["type"]=None
        header_key=h_val
        fields_dict[header_key]=column_dict
        row_template[header_key]=None
    return_dict["fields"]=fields_dict
    return_dict["row_template"]=row_template
    return_dict["header_list"]=header_list
    return return_dict


def get_fields(filename, header_row=None):
    """This function will take in the filename and the header_row of the file and return the Json template for the file
        The file must either be a '.xlsx' or '.csv' file"""

    data={}
    filename_split=filename.split('.')
    ext=filename_split[-1]
    if ext == 'csv':
        print("Generating input-map for '.csv' file.")
        data=get_csv(filename)
    elif ext == 'xlsx':
        print("Generating template for '.xlsx' file.")
        data=get_excel(filename, header_row)
    else:
        print("Filename provided was of an invalid format need .csv or .xlsx")
        exit(1)
    return data

def main():
    """This function opens the .ini file with the specifications and then generates the json template for the file."""
    spec_data={}
    print("Reading configurations from config. file..")
    Config=configparser.ConfigParser()
    Config.read('Input-map_Generate_Settings.ini')

    input_file=Config.get('FILES_INFO', 'TEMPLATE_NAME')
    input_file_header = Config.get('FILES_INFO', 'HEADER_ROW')
    spec_file=Config.get('FILES_INFO', 'SPEC_FILE')
    print("Grabbing info from the input {}, and loading into {}...".format(input_file, spec_file))
    spec_data=get_fields(input_file, input_file_header)
    spec_data["header_row"]=input_file_header

    with open(spec_file, 'w') as write_file:
        json.dump(spec_data, write_file, indent=4)
    return


print("Starting to generate json template.")
main()
print("JSON Template Generated.")

