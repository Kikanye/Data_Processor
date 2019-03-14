"""This script has functions which are used to generate a json file which contains specifications for where the fields
   in a template can be found in an input file.

   NOTE: The template file must be a valid '.csv' or '.xlsx' file"""

# TODO: Need to do more extensive testing on this script to make sure that it can handle edge cases.
import json
import openpyxl
import configparser

RESET_VALUE = 'reset'  # If this is typed in by the user that means they want to restart the process.
NO_HEADER_ROW_INDICATOR = 0


def get_input(item):
    """

    :param item: The name of the field which which needs its column to be specified.
    :return: A dictionary with two keys:
             'column' which specifies the column number where the field 'item' is located in the input file
             'format' which is used to specify the format for the field 'item' if needed

    This function will request input from the user to determine where a field from the template file is located in the
    input file.
    It will process the input to ensure that it is valid.
    If the field is a date/time field, it will also request  that the user input the format of the field.
    """

    return_dict = {"column": -1, "format": ''}  # The dictionary to be returned
    seek_format = False  # Should I ask the user for a format or not?

    # TODO: Should make this more modular, fields must not be named date, datetime or time.

    # If 'item' is a date/time field then ask the user for a format string.
    if (item == 'date') or (item == 'datetime') or (item == 'time'):
        seek_format = True
    correct_input = False
    column_specified = False

    # Keep asking the user for input until you get something valid.
    while (not (correct_input)):
        col = raw_input("\nWhich column contains the '" + item + "'? (Use number or excel column letter)\n Enter " +
                        "{} to restart your entry, (maybe due to errors)".format(RESET_VALUE.upper()))
        # Remove trailing spaces
        col = col.strip()
        # If it is a number, process it and add it to the return dictionary.
        if col.isdigit():
            print("Column number entered.")
            correct_input = True
            return_dict["column"] = int(col)
            column_specified = True
        # If it is a letter, process it and convert it to the equivalent number.
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

            return_dict["column"] = int(col_num)
            column_specified = True

        # If the column was not entered, or something invalid was entered, do these.
        elif col == '':
            print("No column entered, meaning field is not present")
            correct_input = True
        else:
            print("Invalid entry please enter either a valid number for the column of the excel style column")

        # If the column exists in the file and, and the format is needed question the user and get it.
        if column_specified and correct_input and seek_format:
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
    """

    :param header_name_list: A list of all the header names in the template that need to be mapped to a column in
                            another file.
    :return: A dictionary containing the following fields:
            'mappings' which is a dictionary in which every key represents a field from a template and the value
                       represents the column number of where that field is located.
            'header_row' which represents the row which contains the column headers
            'header_list' which is a list containing all the field names which are relevant.
            'formats' which is a dictionary in which every key represents a field from a template and the values
                      represents the format for that field (usually only for date/time fields)

    This function uses the 'get_input()' function to get input for the location of each field in the 'header_name_list'.
    It processes each one and returns a dictionary that fully describes how to map an input file to a template file.
    """
    check_list = [] # Use this list to check if column numbers have previously been used for another field.
    std_dict = {"mappings": {}, "header_row": 1, "header_list": [], "formats": {}}

    # For every field name in the 'header_name_list' get the details for the field.
    for item in header_name_list:
        column = None
        fmt = None
        repeated_entry = True

        # If the user repeats a column which has been assigned to another field then keep asking.
        while repeated_entry:
            # Get input for the current field, if they say reset. End the process.
            item_info = get_input(item)
            if item_info == RESET_VALUE:
                return item_info
            column = item_info["column"]
            fmt = item_info["format"]

            # Check if the column has been assigned to another field and
            # Check that the column was actually specified.
            # (if the column == -1 then that field does not exist in the input file.)
            # If both conditions are satisfied, then add the column number to the list of valid column numbers,
            # else print a message to the user informing them.
            if (column not in check_list) and (column != -1):
                repeated_entry = False
                check_list.append(column)
            elif column == -1:
                # If the column does not exist then don't ask again.
                repeated_entry = False
            else:
                print('Column entered has already been assigned to another field! Please Input a valid Entry'.upper())

        # Add the field specification to the return dictionary.
        if column != -1:
            std_dict["mappings"][item] = column
        if fmt != '':
            std_dict['formats'][item] = fmt

    return std_dict


def generate_input_map(json_template):
    """

    :param json_template: The json file containing the specifications for the fields in the template file
                          (The template file is the file which will have data loaded into it)
    :return: A dictionary containing the following fields:
             'mappings' which is a dictionary in which every key represents a field name in the template,
              and the values represent the column number where that field is located in the input file.
              'header_row': which represents the row number containing the headers in the input file
              'header_list': which is a list containing all the field names in the template file
              'formats': which is a dictionary where each key represents a field from the template
               (the field must also exists in the input file), and the values represent the formats used for those
                fields.

    This function will use the functions above it to get input from the user to generate a json specification
    file that describes where to find each field in the template in the input file.

    It will als question the user to determine what row in the input file contains the headers.
    """
    # the dictionary to be returned.
    return_dict = {"mappings": {}, "header_row": 1, "header_list": [], "formats": {}}

    # Read in the contents of the 'json_template'
    with open(json_template, 'r') as template_json:
        json_template_contents = json.load(template_json)
    header_name_list = json_template_contents["header_list"]
    re_processing = True

    # Call handle_headerlist to get the details for all the fields.
    while re_processing:
        info = handle_headerlist(header_name_list)
        if info != RESET_VALUE:
            re_processing = False
            return_dict = info

    invalid_header_input = True
    header_row = None
    header_row_is_number = False

    # Get the info for the header row and ensure it is valid.
    while invalid_header_input:
        header_row = raw_input("\nWhat row in the file contains the column headings?"
                               " (Enter 0 if the input file has no header row)")
        header_row = header_row.strip()
        try:
            int_test = int(header_row)
            header_row_is_number = True
            invalid_header_input = False
        except Exception as e:
            print e
            print('Invalid entry, input needs to be a number.')

    if (header_row != '1') and (header_row != '') and header_row_is_number:
        header_row = int(header_row)
        if header_row <= 0:
            return_dict["header_row"] = NO_HEADER_ROW_INDICATOR
        else:
            return_dict["header_row"] = header_row
    # sort the contents of the mappings field.
    sorted_headers = sorted(return_dict['mappings'].items(), key=lambda x: (x[1]))
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






