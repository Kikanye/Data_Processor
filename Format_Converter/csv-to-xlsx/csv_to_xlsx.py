"""This script will convert csv files into excel file formats."""
"""There is probably going to be no need for this."""
import csv
import openpyxl


def convert_shet(filename):
    filename_split=filename.split('.')
    workbook=openpyxl.load_workbook(filename_split[0]+".xlsx")
    w_sheet=workbook.active
    w_sheet.title=filename[0]
    return



