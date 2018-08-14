import sys
import os
import shutil
import pathlib2
import json
import JSON_Template_Generator, Data_Loader, Normalizer, Generate_Input_map
import configparser
import traceback


def parse_arguments(arguments):
    """This function will take in one parameter which is a list of values passed in from the command line,
    It returns a dictionary of containing all the arguments with appropriate keys."""
    arg_dict = {'input': None,'template': None, 'input_map': None, 'template_header': None}
    if ('=' in arguments[1] or '=' in arguments[2]):
        raise Exception("Invalid character found in first and/or second argument,\n"
                        "First and/or second arguments must not have '=' signs, must be raw file paths.")
    else:
        arg_dict['input'] = arguments[1].strip()
        arg_dict['template'] = arguments[2].strip()
    for arg in arguments[3:]:
        if('=' not in arg):
            print("Invalid argument supplied, all arguments except the first and the second must be in the form,"
                  " field=value")
            exit(1)
        arg_split = arg.split('=')
        arg_name = arg_split[0].strip()
        arg_variable = arg_split[1].strip()
        arg_dict[arg_name] = arg_variable

    return arg_dict


def handle_file_input(input_file, template_path, template_map_path, formats, directories, input_map_path=None,
                      move_ip_map=True):
    """This function loads a file specified into the specified template. It can use an input_map_path passed in,
     and if not is will generate an input map, by asking u """

    # If the input map file was not provided, then ask questions to generate it.
    if (input_map_path==None or input_map_path==''):
        input_path = pathlib2.Path(input_file)
        input_fname = input_path.name
        input_fname_split = input_fname.split('.')
        parent_dir = pathlib2.Path(input_path.parent)
        input_map_path = str(parent_dir.joinpath(input_fname_split[0]+'_input_mappings.json'))
        data = Generate_Input_map.generate_input_map(template_map_path)

        with open(input_map_path, "w") as data_file:
            json.dump(data, data_file, indent=2)

    # Load the template with the data from the input file and normalize it.
    loaded_data_path = Data_Loader.transfer_values(input_file, template_path, input_map_path, template_map_path)
    row_list = Normalizer.normalize(loaded_data_path, template_map_path, formats)
    normalized_path = Normalizer.writerows(loaded_data_path, row_list, template_map_path)

    # Move the processing files into the right directories
    loaded_data_path_obj = pathlib2.Path(loaded_data_path)
    loaded_data_parent = loaded_data_path_obj.parent
    print("Making directory for Loaded data template. ")
    loaded_data_destination =(loaded_data_parent.joinpath(directories["outputs"])).joinpath(directories['loaded'])
    print("Moving loaded data file into new directory")
    if ((loaded_data_destination.joinpath(loaded_data_path_obj.name)).exists()):
        print("\nA file with name {} already exists in the destination path provided to move."
              .format(loaded_data_path_obj.name))
        response=raw_input("Would you like to replace the file with the newly processed one? (Y/N)")
        if response.lower() == 'y':
            os.remove(str(loaded_data_destination.joinpath(loaded_data_path_obj.name)))

            shutil.move(loaded_data_path, str(loaded_data_destination))
    else:
        shutil.move(loaded_data_path, str(loaded_data_destination))

    normalized_path_obj = pathlib2.Path(normalized_path)
    normalized_path_parent = normalized_path_obj.parent
    print("Making directory for Normalized data template. ")
    normalized_data_destination = (normalized_path_parent.joinpath(directories["outputs"])).\
        joinpath(directories['normalized'])
    print("Moving Normalized data file into new directory.")
    if((normalized_data_destination.joinpath(normalized_path_obj.name)).exists()):
        print("\nA file with name {} already exists in the destination path provided to move."
              .format(normalized_path_obj.name))
        response=raw_input("Would you like to replace the file with the newly processed one? (Y/N)")
        if response.lower() == 'y':
            os.remove(str(normalized_data_destination.joinpath(normalized_path_obj.name)))
            shutil.move(normalized_path, str(normalized_data_destination))
    else:
        shutil.move(normalized_path, str(normalized_data_destination))

    # If the input map file is to be moved (all files are not he same format), then do so.
    if move_ip_map:
        ip_map = pathlib2.Path(input_map_path)
        ip_parent = ip_map.parent
        print("Making directory for json maps. ")
        json_templates_path = ip_parent.joinpath(directories['json_maps'])
        print("Moving json maps data file into new directory.")
        if((json_templates_path.joinpath(ip_map.name)).exists()):
            print("\nA file with name {} already exists in the destination path provided to move, move not possible."
                  .format(ip_map.name))
            response = raw_input("Would you like to replace the file with the newly processed one? (Y/N)")
            if response.lower() == 'y':
                os.remove(str(json_templates_path.joinpath(ip_map.name)))
                shutil.move(str(ip_map), str(json_templates_path))
        else:
            shutil.move(str(ip_map), str(json_templates_path))

    return


def handle_dir_input(dir_path, template_path, template_map_path, formats, directories, same_file_formats,
                     input_map_path=None):
    """This function takes in a directory and loads all the files in that directory into the specified template."""

    # Get all the names of the files to be loaded and put them into a list.
    files_list = []
    dir_path_object = pathlib2.Path(dir_path)
    for item in dir_path_object.iterdir():
        item = str(item)
        item_split = item.split('.')
        extension = item_split[-1]
        if extension == 'csv' or extension == 'xlsx' or extension == 'xls':
            files_list.append(str(item))

    # Do this if all the files in the directory have the same format.
    if (same_file_formats):
        # Check to see if the input file map was provided, if not ask questions to generate it.
        print("Processing files with all same formats")
        if(input_map_path==None or input_map_path==''):
            input_path = pathlib2.Path(files_list[0])
            parent_dir = pathlib2.Path(input_path.parent)
            input_map_path = str(parent_dir.joinpath('_input_mappings.json'))
            data = Generate_Input_map.generate_input_map(template_map_path)

            with open(input_map_path, "w") as data_file:
                json.dump(data, data_file, indent=2)

        # Process each file in the list
        for file in files_list:
            try:
                handle_file_input(file, template_path, template_map_path, formats, directories=directories,
                                  input_map_path=input_map_path,
                                  move_ip_map=False)
            except Exception as e:
                traceback.print_exc()
                print("Processing {} failed".format(file))
                print(e)

        # Move the files into the right directories after processing.
        ip_map = pathlib2.Path(input_map_path)
        ip_parent = ip_map.parent
        print("Making directory for json maps. ")
        json_templates_path = ip_parent.joinpath(directories['json_maps'])
        print("Moving json maps data file into new directory.")
        if (json_templates_path.joinpath(ip_map.name)).exists():
            print("\nA file with name {} already exists in the destination path provided to move."
                  .format(ip_map.name))
            response = raw_input("Would you like to replace the file with the newly processed one? (Y/N)")
            if response.lower() == 'y':
                os.remove(str(json_templates_path.joinpath(ip_map.name)))
                shutil.move(str(ip_map), str(json_templates_path))
        else:
            shutil.move(str(ip_map), str(json_templates_path))

    else:
        print("Processing files with same formats")
        # If the files to be loaded are not all in the same format, load them this way
        for file in files_list:
            print("\nFill in data location information for {}".format(pathlib2.Path(file).name))
            try:
                handle_file_input(file, template_path, template_map_path, formats, directories)
            except Exception as e:
                print(e)
                traceback.print_exc()
    return


def main():
    Config = configparser.ConfigParser()
    Config.read('Formats_Settings.ini')

    dirs = {'outputs': 'Outputs', 'loaded': 'Loaded', 'normalized': 'Normalized', 'json_maps': 'Json_Maps'}

    datetime_format = Config.get('NORMALIZE_FORMATS', 'datetime')
    date_format = Config.get('NORMALIZE_FORMATS', 'date')
    time_format = Config.get('NORMALIZE_FORMATS', 'time')

    formats = {}
    formats["datetime_format"] = datetime_format
    formats["date_format"] = date_format
    formats["time_format"] = time_format

    arguments=sys.argv
    input_file_or_dir = None
    template_file_path = None
    input_map_path = None
    template_json_map_path = None
    template_header_number = '1'

    # Get and parse arguments, exit if the number of arguments are incomplete
    if(len(arguments)<3):
        print("At least 2 arguments are required for the scripts to run successfully.")
        exit(-1)
    else:
        print("Complete args... ")
        print("Parsing arguments... ")
        args_dictionary = parse_arguments(arguments)
        input_file_or_dir = args_dictionary['input']
        template_file_path = args_dictionary['template']
        template_path = pathlib2.Path(template_file_path)
        template_fname = template_path.name
        template_fname_split = template_fname.split('.')
        template_parent_dir = pathlib2.Path(template_path.parent)

        # Get the names of the directories to put the output files into.
        outputs_dir = template_parent_dir.joinpath(dirs['outputs'])
        normalized_dir = outputs_dir.joinpath(dirs['loaded'])
        loaded_dir = outputs_dir.joinpath(dirs["normalized"])

        # Check to see if the directories that will contain the auto generated files exist already, if not create them.
        if (not(outputs_dir.exists())):
            os.mkdir(str(outputs_dir))
        if (not(normalized_dir.exists())):
            os.mkdir(str(normalized_dir))
        if (not(loaded_dir.exists())):
            os.mkdir(str(loaded_dir))

        # Create the filename string for the Json map that will be used for the template file
        template_json_map_path = str(template_parent_dir.joinpath(template_fname_split[0] + '.json'))

        if (args_dictionary['input_map']!=None):
            input_map_path = args_dictionary['input_map']
        if (args_dictionary['template_header']!=None):
            template_header_number = int(args_dictionary['template_header'])

    # Call functions from the JSON Template Generator to create the JSON_Template map
    spec_data = JSON_Template_Generator.get_fields(template_file_path, template_header_number)
    JSON_Template_Generator.write_to_file(spec_data, template_json_map_path, template_header_number)

    # Create path object for the input data,call methods to process and load the data into the templates
    input_data_path = pathlib2.Path(input_file_or_dir)
    if (input_data_path.exists()):
        # If the input path is a file, process it like this.
        if (input_data_path.is_file()):
            print('Processing single file.')
            input_fname=input_data_path.name
            input_fname_split=input_fname.split('.')
            extension=input_fname_split[-1]

            if not((extension == 'csv') or (extension == 'xlsx') or (extension == 'xls')):
                print("Input file must be a csv, xlsx or xls file.")
                exit(-1)
            input_dir_obj = input_data_path.parent
            json_maps_dir = input_dir_obj.joinpath(dirs["json_maps"])
            if (not (json_maps_dir.exists())):
                os.mkdir(str(json_maps_dir))
            try:
                handle_file_input(input_file_or_dir, template_file_path, template_json_map_path, formats, dirs,
                              input_map_path=input_map_path)
            except Exception as e:
                print("Failed to process {}".format(input_file_or_dir))
                print(e)
                traceback.print_exc()

        # If the input path is a directory, process it like this.
        elif(input_data_path.is_dir()):
            print("Processing a directory of files.")
            json_maps_dir = input_data_path.joinpath(dirs["json_maps"])
            if (not (json_maps_dir.exists())):
                os.mkdir(str(json_maps_dir))
            same_file_formats = False
            file_fmt_response = None
            while (file_fmt_response is None) or file_fmt_response == '':
                file_fmt_response = raw_input("Do all the files in the directory have the same format (Y/N)?")
                file_fmt_response = file_fmt_response.strip()
            if(file_fmt_response.lower()[0]=='y'):
                print("The same input map will be used to load all the files since they are of the same format.")
                same_file_formats = True
            try:
                handle_dir_input(input_file_or_dir, template_file_path, template_json_map_path, formats, dirs,
                             same_file_formats, input_map_path)
            except Exception as e:
                print("Failed to process {}".format(input_file_or_dir))
                print(e)
                traceback.print_exc()
        else:
            print("Invalid argument for input file, it is neither a directory or a file.")
    return


main()
print("End of processing")
