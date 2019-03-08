import configparser
import pathlib2
import json
from map_Generators import JSON_Template_Generator, Generate_Input_map
from Load import Data_Loader
from Normalize import Normalizer


def main():
    print("Processing new file")
    Config = configparser.ConfigParser()
    Config.read('Loader_Config.ini')

    TEMPLATE_FILE = Config.get('TEMPLATE_INFO', 'TEMPLATE_PATH')
    TEMPLATE_SPEC = ''
    TEMPLATE_HEADER = ''
    if (TEMPLATE_FILE is None) or TEMPLATE_FILE == '':
        print("Template to load the data into must be specified.")
        exit(-1)
    else:
        template_path_obj = pathlib2.Path(TEMPLATE_FILE)
        if(template_path_obj.exists()):
            if(template_path_obj.is_file()):
                template_name = template_path_obj.name
                template_name_split = template_name.split('.')
                extension = template_name_split[-1].lower()
                if(extension == 'xlsx') or (extension == 'csv') or (extension == 'xls'):
                    template_spec_name = ''.join(template_name_split[0:len(template_name_split)-1])+'.json'
                    template_path_parent = template_path_obj.parent
                    TEMPLATE_SPEC = str(template_path_parent.joinpath(template_spec_name))
                    TEMPLATE_HEADER = Config.get('TEMPLATE_INFO', 'TEMPLATE_HEADER_ROW')
                else:
                    print("The template must have one of the following extensions (.csv, .xlsx, .xls)")
                    exit(-1)
            else:
                print("Template path must be a file, not a directory")
                exit(-1)
        else:
            print("The path specified for the template file does not exist")
            exit(-1)

    INPUT_FILE = Config.get('INPUT_INFO', 'INPUT_FILE_PATH')
    input_path_obj=''
    input_filename_split = ''
    if (INPUT_FILE is None) or INPUT_FILE == '':
        print("Input file to load data from.")
        exit(-1)
    else:
        input_path_obj=pathlib2.Path(INPUT_FILE)
        if (input_path_obj.exists()):
            if(input_path_obj.is_file()):
                input_filename=input_path_obj.name
                input_filename_split = input_filename.split('.')
                extension = input_filename_split[-1].lower()

                if (not((extension == 'xlsx') or (extension == 'csv') or (extension == 'xls'))):
                    print("Input file must be of type xlsx, csv or xls")
                    exit(-1)
            else:
                print("Input must be a file, not a directory")
                exit(-1)

    INPUT_SPEC = Config.get('INPUT_INFO', 'INPUT_FILE_MAP')

    if(INPUT_SPEC==''):
        print("Input map file path not specified, will generate this map by asking questions.")
        input_spec_name = ''.join(input_filename_split[0:len(input_filename_split) - 1]) + '_input_mappings.json'
        INPUT_SPEC_Parent = input_path_obj.parent
        INPUT_SPEC=str(INPUT_SPEC_Parent.joinpath(input_spec_name))

    else:
        input_spec_path_obj = pathlib2.Path(INPUT_SPEC)
        if (input_spec_path_obj.exists()):
            if(input_spec_path_obj.is_file()):
                input_spec_name = input_spec_path_obj.name
                input_spec_name_split = input_spec_name.split('.')
                extension = input_spec_name_split[-1].lower()

                if(not(extension == 'json')):
                    print("Input map file must be a json file.")
                    exit(-1)
            else:
                print("Input file map path must be a file, not a directory")
                exit(-1)



    input_file_part_name = ''.join(input_filename_split[0:len(input_filename_split)-1])
    template_path_obj=pathlib2.Path(TEMPLATE_FILE)
    DATA_FILE = input_file_part_name+'-'+template_path_obj.name
    DATA_FILE = str((template_path_obj.parent).joinpath(DATA_FILE))
    datetime_format = Config.get('INPUT_FORMATS', 'datetime')
    date_format = Config.get('INPUT_FORMATS', 'date')
    time_format = Config.get('INPUT_FORMATS', 'time')

    # This part generates a JSON template for the Template file.
    print("Generating JSON template file for {}".format(TEMPLATE_FILE))
    spec_data = JSON_Template_Generator.get_fields(TEMPLATE_FILE, TEMPLATE_HEADER)
    JSON_Template_Generator.write_to_file(spec_data, TEMPLATE_SPEC, TEMPLATE_HEADER)

    # This part of the script will transfer values from input file to the template.
    print ("Loading data from {} into template {}".format(INPUT_FILE, TEMPLATE_FILE))
    input_map = Generate_Input_map.generate_input_map(TEMPLATE_SPEC)
    with open(INPUT_SPEC, 'w') as data_file:
        json.dump(input_map, data_file, indent=2)

    Data_Loader.transfer_values(INPUT_FILE, TEMPLATE_FILE, INPUT_SPEC, TEMPLATE_SPEC)

    # This part of the script will normalize the contents of the template.
    print ("Normalizing the data which has been loaded into the Template {}".format(DATA_FILE))
    formats = {}
    formats["datetime_format"] = datetime_format
    formats["date_format"] = date_format
    formats["time_format"] = time_format
    row_list = Normalizer.normalize(DATA_FILE, TEMPLATE_SPEC, formats)
    Normalizer.writerows(DATA_FILE, row_list, TEMPLATE_SPEC)

    print("End of processing")

    return


main()
