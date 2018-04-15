
#!/usr/bin/python

# PURPOSE: Download air quality (air), meterological observatino (met) and meterological grid (grid) 
#          data for multipe cities and time frames
#
# ARGUMENTS: load_data.py <city> <type> <start datetime> <end datetime>
#
# WHERE:  <city> is one of Beijing, London, or Both
#         <type> is one of air, met, grid, all
#         <start datetime> and <end datetime> are in the form yyyy-mm-dd-h
#
#
# EXAMPLES: python load_data.py Beijing air 2018-04-01-0 2018-04-15-14 
#             this will air quality dataload hourl for Beijing between 
#             April 1, 2018 midnight and April 15, 2018 2pm.
#           python load_data.py Both all 2018-03-01-0 2018-03-15-14 
#             this will load all data for both cities between 
#             April 1, 2018 midnight and April 15, 2018 2pm. for all data types
#
# based on https://www.tutorialspoint.com/python/python_command_line_arguments.htm
#
##################################################################################

import sys, getopt
import requests

# FUNCTION load_on_url()
# Based on https://biendata.com/forum/view_post_category/9
# Takes city, datatype, from/to date-times and builds urls for gettind data.
# Also builds file paths for saving to csv
# https://biendata.com/competition/airquality/{city}/{start_time}/{end_time}/2k0d1d8
# https://biendata.com/competition/meteorology/{city}/{start_time}/{end_time}/2k0d1d8
# https://biendata.com/competition/meteorology/{city}_grid/{start_time}/{end_time}/2k0d1d8
def load_one_url (city, datatype, from_datetime, to_datetime):

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
    print (url)

    outpath = 'data/' + city + '/' + datatype + '/' + city_datapath + '_' + from_datetime + \
               '_' + to_datetime + '.csv'
    print (outpath)
    print ('')

    respones= requests.get(url)
    with open (outpath,'w') as f:
      f.write(respones.text)

def load_one_city(city, datatype, from_datetime, to_datetime):
   if datatype == "all":
       load_one_url(city, 'air', from_datetime, to_datetime)
       load_one_url(city, 'met', from_datetime, to_datetime)
       load_one_url(city, 'grid', from_datetime, to_datetime)
   else:
       load_one_url(city, datatype, from_datetime, to_datetime)

def main(argv):
   city = ''
   datatype = ''
   from_datetime = ''
   to_datetime = ''
   example = 'load_data.py -c <city> -d <datatype> -f <from datetime> -t <to datetime>'
   try:
      opts, args = getopt.getopt(argv,"hc:d:f:t:",["city=","datatype=","from_datetime=","to_datetime="])
   except getopt.GetoptError:
      print (example)
      sys.exit(2)
   for opt, arg in opts:
      if opt == '-h':
         print (example)
         sys.exit()
      elif opt in ("-c", "--city"):
         city = arg
      elif opt in ("-d", "--datatype"):
         datatype = arg
      elif opt in ("-f", "--from_datetime"):
         from_datetime = arg
      elif opt in ("-t", "--to_datetime"):
         to_datetime = arg

   if city == "Both":
       load_one_city('Beijing', datatype, from_datetime, to_datetime)
       load_one_city('London', datatype, from_datetime, to_datetime)
   else:
       load_one_city(city, datatype, from_datetime, to_datetime)

if __name__ == "__main__":
   main(sys.argv[1:])