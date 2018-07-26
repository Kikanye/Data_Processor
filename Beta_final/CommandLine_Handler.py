import sys
import os
import shutil
import pathlib2
import json
import JSON_Template_Generator, Data_Loader, Normalizer, Generate_Input_map
import configparser


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
    if(input_map_path==None or input_map_path==''):
        input_path = pathlib2.Path(input_file)
        input_fname = input_path.name
        input_fname_split = input_fname.split('.')
        parent_dir = pathlib2.Path(input_path.parent)
        input_map_path = str(parent_dir.joinpath(input_fname_split[0]+'_input_mappings.json'))
        data = Generate_Input_map.generate_sample_input_map(template_map_path)

        with open(input_map_path, "w") as data_file:
            json.dump(data, data_file, indent=2)

    loaded_data_path = Data_Loader.transfer_values(input_file, template_path, input_map_path, template_map_path)
    row_list = Normalizer.normalize(loaded_data_path, template_map_path, formats)
    normalized_path = Normalizer.writerows(loaded_data_path, row_list, template_map_path)

    loaded_data_path_obj = pathlib2.Path(loaded_data_path)
    loaded_data_parent = loaded_data_path_obj.parent
    loaded_data_destination =(loaded_data_parent.joinpath(directories["outputs"])).joinpath(directories['loaded'])
    if((loaded_data_destination.joinpath(loaded_data_path_obj.name)).exists()):
        print("A file with name {} already exists in the destination path provided to move."
              .format(loaded_data_path_obj.name))
        response=raw_input("Would you like to replace the file with the newly processed one? (Y/N)")
        if response.lower() == 'y':
            os.remove(str(loaded_data_destination.joinpath(loaded_data_path_obj.name)))
            shutil.move(loaded_data_path, str(loaded_data_destination))
    else:
        shutil.move(loaded_data_path, str(loaded_data_destination))

    normalized_path_obj = pathlib2.Path(normalized_path)
    normalized_path_parent = normalized_path_obj.parent
    normalized_data_destination = (normalized_path_parent.joinpath(directories["outputs"])).\
        joinpath(directories['normalized'])
    if((normalized_data_destination.joinpath(normalized_path_obj.name)).exists()):
        print("A file with name {} already exists in the destination path provided to move."
              .format(normalized_path_obj.name))
        response=raw_input("Would you like to replace the file with the newly processed one? (Y/N)")
        if response.lower() == 'y':
            os.remove(str(normalized_data_destination.joinpath(normalized_path_obj.name)))
            shutil.move(normalized_path, str(normalized_data_destination))
    else:
        shutil.move(normalized_path, str(normalized_data_destination))

    if move_ip_map:
        ip_map = pathlib2.Path(input_map_path)
        ip_parent = ip_map.parent
        json_templates_path = ip_parent.joinpath(directories['json_maps'])
        if((json_templates_path.joinpath(ip_map.name)).exists()):
            print("A file with name {} already exists in the destination path provided to move, move not possible."
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
    # TODO: Implement algorithm to handle directory as input
    files_list=[]
    dir_path_object = pathlib2.Path(dir_path)
    for item in dir_path_object.iterdir():
        files_list.append(str(item))

    if(same_file_formats):
        if(input_map_path==None or input_map_path==''):
            input_path = pathlib2.Path(files_list[0])
            parent_dir = pathlib2.Path(input_path.parent)
            input_map_path = str(parent_dir.joinpath('_input_mappings.json'))
            data = Generate_Input_map.generate_sample_input_map(template_map_path)

            with open(input_map_path, "w") as data_file:
                json.dump(data, data_file, indent=2)

        for file in files_list:
                handle_file_input(file, template_path, template_map_path, formats, directories=directories,
                                  input_map_path=input_map_path,
                                  move_ip_map=False)
        ip_map = pathlib2.Path(input_map_path)
        ip_parent = ip_map.parent
        json_templates_path = ip_parent.joinpath(directories['json_maps'])
        if (json_templates_path.joinpath(ip_map.name)).exists():
            print("A file with name {} already exists in the destination path provided to move."
                  .format(ip_map.name))
            response = raw_input("Would you like to replace the file with the newly processed one? (Y/N)")
            if response.lower() == 'y':
                os.remove(str(json_templates_path.joinpath(ip_map.name)))
                shutil.move(str(ip_map), str(json_templates_path))
        else:
            shutil.move(str(ip_map), str(json_templates_path))

    else:
        for file in files_list:
            print("Fill in data location information for {}".format(pathlib2.Path(file).name))
            handle_file_input(file, template_path, template_map_path, formats, directories)
    return


def main():
    Config = configparser.ConfigParser()
    Config.read('CommandLine_Config.ini')

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
    template_map_path = None
    template_header_number = '1'

    if(len(arguments)<3):
        print("At least 2 arguments are required for the scripts to run successfully.")
    else:
        print("complete args...")
        args_dictionary = parse_arguments(arguments)
        input_file_or_dir = args_dictionary['input']
        template_file_path = args_dictionary['template']
        template_path = pathlib2.Path(template_file_path)
        template_fname = template_path.name
        template_fname_split = template_fname.split('.')
        template_parent_dir = pathlib2.Path(template_path.parent)

        outputs_dir = template_parent_dir.joinpath(dirs['outputs'])
        normalized_dir = outputs_dir.joinpath(dirs['loaded'])
        loaded_dir = outputs_dir.joinpath(dirs["normalized"])


        if(not(outputs_dir.exists())):
            os.mkdir(str(outputs_dir))
        if(not(normalized_dir.exists())):
            os.mkdir(str(normalized_dir))
        if(not(loaded_dir.exists())):
            os.mkdir(str(loaded_dir))


        template_map_path = str(template_parent_dir.joinpath(template_fname_split[0] + '.json'))

        if(args_dictionary['input_map']!=None):
            input_map_path = args_dictionary['input_map']
        if args_dictionary['template_header']!=None:
            template_header_number = int(args_dictionary['template_header'])

    spec_data = JSON_Template_Generator.get_fields(template_file_path, int(template_header_number))
    JSON_Template_Generator.write_to_file(spec_data, template_map_path, template_header_number)
    input_fpath = pathlib2.Path(input_file_or_dir)


    if(input_fpath.exists()):
        if(input_fpath.is_file()):
            input_dir_obj = input_fpath.parent
            json_maps_dir = input_dir_obj.joinpath(dirs["json_maps"])
            if (not (json_maps_dir.exists())):
                os.mkdir(str(json_maps_dir))
            handle_file_input(input_file_or_dir, template_file_path, template_map_path, formats, input_map_path)
        elif(input_fpath.is_dir()):
            json_maps_dir = input_fpath.joinpath(dirs["json_maps"])
            if (not (json_maps_dir.exists())):
                os.mkdir(str(json_maps_dir))
            same_file_formats = False
            file_fmt_response = None
            while (file_fmt_response is None) or file_fmt_response == '':
                file_fmt_response = raw_input("Do all the files in the directory have the same format (Y/N)?")
                file_fmt_response = file_fmt_response.strip()
            if(file_fmt_response.lower()[0]=='y'):
                print("The same input map will me used to load all the files since they are of the same format.")
                same_file_formats=True
            handle_dir_input(input_file_or_dir, template_file_path, template_map_path, formats, dirs, same_file_formats,
                             input_map_path)
        else:
            print("Invalid argument for input file, it is neither a directory or a file.")
    return


main()
print("End of processing")
