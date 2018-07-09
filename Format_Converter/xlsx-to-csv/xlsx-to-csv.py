"""Specify the fields form the input file which you want to move into the csv file."""
import openpyxl
import pandas as pd

def main(filename, header_row, header_names, ):
    d_frames = pd.read_excel(filename)
    d_frames.to_csv()


    return