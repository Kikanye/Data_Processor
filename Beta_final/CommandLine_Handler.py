import Main
import sys
import os
import pathlib2

def handle_dir_input():
    # TODO: Implement algorithm to handle directory as input
    return

def handle_file_input():
    # TODO: Implement algorithm to handle file as input
    return

tst=os.listdir('C:\Users\CEOS\PycharmProjects\Data_Processor')
testdir=tst[-1]
the_path=testdir
the_curr_path=pathlib2.Path(the_path)
ttst=the_curr_path.is_dir()

xxt = pathlib2.Path('Loader_Config.ini')
ttt=xxt.exists()
lts=xxt.is_file()

arguments=sys.argv
input_file=''
template_file=''
input_map_file=''
input_header_number=''
template_header_number=''

if(len(arguments)<3):
    print("At least 2 arguments are required for the scripts to run successfully.")
else:
    print("complete args...")
    input_file_or_dir = arguments[1]
    template_file = arguments[2]
    if(len(arguments)==4):
        input_map_file=arguments[3]
    if(len(arguments)==5):
        input_header_number = arguments[4]
    if len(arguments) == 6:
        template_header_number = arguments[5]

input_path = pathlib2.Path(input_file_or_dir)
if(input_path.exists()):
    if(input_path.is_file()):
        handle_file_input()
    elif(input_path.is_dir()):
        handle_dir_input()
    else:
        print("Invalid argument for input file, it is neither a directory or a file.")



def handle_dir_input():

    return

def handle_file_input():
    return

print("End of processing")