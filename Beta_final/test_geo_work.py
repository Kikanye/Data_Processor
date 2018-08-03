# -*- coding: utf-8 -*-
import Normalizer, time

def main():
    degree_sign = u'\N{DEGREE SIGN}'
    row_list=[]
    row1 = {'latitude_min_sec': '''71°25'16"''', 'longitude_min_sec': '''136°25.25''', 'n/s': 'N', 'e/w': 'W'}
    row2 = {'latitude_deg_dec': 71.2580, 'n/s':'N', 'longitude_deg_dec': -136.2564}
    row3 = {'latitude_min_sec': '''71°35.20N''', 'longitude_min_sec': '''130°25.64W'''}
    row4 = {'latitude_min_sec': '''''', 'longitude_min_sec':''''''}
    row5 = {'latitude_min_sec': None, 'longitude_min_sec': None}
    row6 = {'latitude_deg_dec':'71.2580N', 'longitude_deg_dec': '130.25W'}


    row_list.append(row1)
    row_list.append(row2)
    row_list.append(row3)
    row_list.append(row4)
    row_list.append(row5)
    row_list.append(row6)
    count = 1
    for row in row_list:
        print "row"+str(count)+"-"*20
        row = Normalizer.geo_data_work(row)
        for key, value in row.items():
            print ("{}->{}".format(key, value))
        print
        count+=1
        time.sleep(2.0)
    return

main()