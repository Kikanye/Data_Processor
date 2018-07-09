import configparser
import JSON_Template_Generator, Data_Loader, Normalizer


def main():
    print("Processing new file")
    Config = configparser.ConfigParser()
    Config.read('Loader_Config.ini')
    TEMPLATE_FILE = Config.get('FILES_INFO', 'TEMPLATE_NAME')
    TEMPLATE_HEADER = Config.get('FILES_INFO', 'TEMPLATE_HEADER_ROW')
    INPUT_FILE = Config.get('INPUT', 'I_FILE')
    datetime_format = Config.get('FORMATS', 'datetime')
    date_format = Config.get('FORMATS', 'date')
    time_format = Config.get('FORMATS', 'time')


    # This part generates a JSON template for the Template file.
    #TEMPLATE_FILE = Config.get('FILES_INFO', 'TEMPLATE_NAME')
    print("Generating JSON template file for {}".format(TEMPLATE_FILE))
    #TEMPLATE_HEADER = Config.get('FILES_INFO', 'TEMPLATE_HEADER_ROW')
    template_name_split = TEMPLATE_FILE.split('.')
    template_spec_file = ''.join(template_name_split[0:len(template_name_split)-1])+'.json'#Config.get('FILES_INFO', 'TEMPLATE_SPEC_FILE')
    spec_data = JSON_Template_Generator.get_fields(TEMPLATE_FILE, TEMPLATE_HEADER)
    JSON_Template_Generator.write_to_file(spec_data, template_spec_file, TEMPLATE_HEADER)


    # This part of the script will transfer values from input fule to the template
    #INPUT_FILE = Config.get('INPUT', 'I_FILE')
    input_filename_split = INPUT_FILE.split('.')
    INPUT_SPEC = ''.join(input_filename_split[0:len(input_filename_split)-1])+'_input_mappings.json'#Config.get('INPUT', 'MAPPINGS_FILE')
    OUTPUT_FILE = TEMPLATE_FILE#Config.get('OUTPUT', 'O_FILE')
    OUT_SPEC = template_spec_file#Config.get('OUTPUT', 'FIELDS')
    Data_Loader.transfer_values(INPUT_FILE, OUTPUT_FILE, INPUT_SPEC, OUT_SPEC)


    # This part of the script will normalize the contents of the template.
    input_file_part_name = ''.join(input_filename_split[0:len(input_filename_split)-1])
    DATA_FILE = input_file_part_name+TEMPLATE_FILE#Config.get('SPECS', 'FILENAME')
    DATA_SPEC = template_spec_file#Config.get('SPECS', 'SPECFILE')
    formats = {}
    datetime_format = Config.get('FORMATS', 'datetime')
    date_format = Config.get('FORMATS', 'date')
    time_format = Config.get('FORMATS', 'time')
    formats["datetime_format"] = datetime_format
    formats["date_format"] = date_format
    formats["time_format"] = time_format
    row_list = Normalizer.normalize(DATA_FILE, DATA_SPEC, formats)
    Normalizer.writerows(DATA_FILE, row_list, DATA_SPEC)
    print("ENd of processing")

    return


main()
