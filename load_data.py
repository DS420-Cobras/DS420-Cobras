
#!/usr/bin/python

# PURPOSE: Download air quality (air), meterological observatino (met) and
# meterological grid (grid)
#          data for multipe cities and time frames
#
# ARGUMENTS: load_data.py <city> <type> <start datetime> <end datetime>
#
# WHERE: <city> is one of Beijing, London, or Both
#         <type> is one of air, met, grid, all
#         <start datetime> and <end datetime> are in the form yyyy-mm-dd-h
#
#
# EXAMPLES: python load_data.py Beijing air 2018-04-01-0 2018-04-15-14
#             this will air quality dataload hourl for Beijing between
#             April 1, 2018 midnight and April 15, 2018 2pm.
#           python load_data.py Both all 2018-03-01-0 2018-03-15-14
#             this will load all data for both cities between
#             April 1, 2018 midnight and April 15, 2018 2pm.  for all data
#             types
#
# based on
# https://www.tutorialspoint.com/python/python_command_line_arguments.htm
#
##################################################################################
import sys
import getopt
import requests
import os
import time
import pandas as pd

def doesFileNeedUpdate(filename):
    "This function checks whether this file needs to be downloaded or whether local cache is fine"
    #return True
    if not os.path.exists(filename):
        return True
    ftime = os.path.getmtime(filename)
    ft = time.localtime(ftime)
    ct = time.localtime()
    if ct.tm_year != ft.tm_year:
        return True
    if ct.tm_mon != ft.tm_mon:
        return True
    if ct.tm_mday != ft.tm_mday:
        return True
    if ct.tm_hour != ft.tm_hour:
        return True

    return False

# FUNCTION load_on_url()
# Based on https://biendata.com/forum/view_post_category/9
# Takes city, datatype, from/to date-times and builds urls for gettind data.
# Also builds file paths for saving to csv
# https://biendata.com/competition/airquality/{city}/{start_time}/{end_time}/2k0d1d8
# https://biendata.com/competition/meteorology/{city}/{start_time}/{end_time}/2k0d1d8
# https://biendata.com/competition/meteorology/{city}_grid/{start_time}/{end_time}/2k0d1d8
def load_one_url(city, datatype, from_datetime, to_datetime):

    url_preamble = 'https://biendata.com/competition/'
    url_tail = '/2k0d1d8'
    
    if city == "London":
        url_city = 'ld'
    elif city == "Beijing":
        url_city = 'bj'
    else:
        print("*** ERROR: unknown city " + city)
        exit(9999)

    if datatype == "air":
        url_datatype = 'airquality'
        city_datapath = url_city + '_' + url_datatype
    elif datatype == "met":
        url_datatype = 'meteorology'
        city_datapath = url_city + '_' + url_datatype
    elif datatype == "grid":
        url_datatype = 'meteorology'
        url_city = url_city + '_grid'
        city_datapath = url_city
    else:
        print("*** ERROR: unknown datatype " + datatype)
        exit(9998)

    url = url_preamble + url_datatype + '/' + url_city + '/' + from_datetime + '/' + to_datetime + url_tail
    print(url)

    outpath = 'data/' + city + '/' + datatype + '/' + city_datapath + '_' + from_datetime + '_' + to_datetime + '.csv'
    print(outpath)
    print('')
    if doesFileNeedUpdate(outpath):
        respones = requests.get(url)
        with open(outpath,'w') as f:
            f.write(respones.text)
    return outpath

def load_one_city(city, datatype, from_datetime, to_datetime):
    ret = {}
    if datatype == "all":
        ret[city, 'air'] = load_one_url(city, 'air', from_datetime, to_datetime)
        ret[city, 'met'] = load_one_url(city, 'met', from_datetime, to_datetime)
        ret[city, 'grid'] = load_one_url(city, 'grid', from_datetime, to_datetime)
    else:
        ret[city, datatype] = load_one_url(city, datatype, from_datetime, to_datetime)
    return ret

def getPandasDataframes(argv = ['-c', 'Both', '-d', 'all', '-f', '2017-01-01-0', '-t', '2018-05-31-23']):
    fileDict = main(argv)
    return {key:pd.read_csv(value) for (key, value) in fileDict.items()}

def getBeijingDataframes(argv = ['-c', 'Beijing', '-d', 'all', '-f', '2018-04-23-10', '-t', '2018-05-31-23']):
    fileDict = main(argv)
    return {key:pd.read_csv(value) for (key, value) in fileDict.items()}

def getLondonDataframes(argv = ['-c', 'London', '-d', 'all', '-f', '2018-04-25-21', '-t', '2018-05-31-23']):
    fileDict = main(argv)
    return {key:pd.read_csv(value) for (key, value) in fileDict.items()}

def main(argv):
    city = ''
    datatype = ''
    from_datetime = ''
    to_datetime = ''
    example = 'load_data.py -c <city> -d <datatype> -f <from datetime> -t <to datetime>'
    try:
        opts, args = getopt.getopt(argv,"hc:d:f:t:",["city=","datatype=","from_datetime=","to_datetime="])
    except getopt.GetoptError:
        print(example)
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(example)
            sys.exit()
        elif opt in ("-c", "--city"):
            city = arg
        elif opt in ("-d", "--datatype"):
            datatype = arg
        elif opt in ("-f", "--from_datetime"):
            from_datetime = arg
        elif opt in ("-t", "--to_datetime"):
            to_datetime = arg

    ret = {}
    if city == "Both":
        ret = load_one_city('Beijing', datatype, from_datetime, to_datetime)
        tmp = load_one_city('London', datatype, from_datetime, to_datetime)
        for (key, val) in tmp.items():
            ret[key] = val
    else:
        ret = load_one_city(city, datatype, from_datetime, to_datetime)
    return ret

if __name__ == "__main__":
    main(sys.argv[1:])