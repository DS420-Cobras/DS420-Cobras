
# PURPOSE: Download air quality (air), meterological observatino (met) and meterological grid (grid) 
#          data for multipe cities and time frames
#!/usr/bin/python
#
# ARGUMENTS: load_data.py <city> <type> <start datetime> <end datetime>
#
# WHERE:  <city> is one of Beijing, London, or Both
#         <type> is one of air, met, grid, all
#         <start datetime> and <end datetime> yyyy-mm-dd-h
#
#
# EXAMPLES: python load_data.py Beijing air 2018-03-01-0 2018-03-15-14 
#             this will air quality dataload hourl for Beijing between 
#             March 1, 2018 midnight and March 15, 2018 2pm.
#           python load_data.py Both all 2018-03-01-0 2018-03-15-14 
#             this will load all data for both cities between 
#             March 1, 2018 midnight and March 15, 2018 2pm.
#
# based on https://www.tutorialspoint.com/python/python_command_line_arguments.htm
#
##################################################################################

import sys, getopt

def load_one_datatype(city, datatype, from_datetime, to_datetime):
    from_year  = from_datetime[:4] #equiv. to left(from_datetime, 4)
    from_month = from_datetime[5:7]
    from_day   = from_datetime[8:10]
    from_hour  = from_datetime[11:len(from_datetime)]

    to_year  = to_datetime[:4] #equiv. to left(to_datetime, 4)
    to_month = to_datetime[5:7]
    to_day   = to_datetime[8:10]
    to_hour  = to_datetime[11:len(to_datetime)]

    #print ("----< in load_one_datatype() >----")
    #print ('city is ' + city)
    #print ('datatype is ' + datatype)
    #print ('from year: '  + from_year)
    #print ('from month: ' + from_month)
    #print ('from day: '   + from_day)
    #print ('from hour: '  + from_hour)

    #print ('to year: '  + to_year)
    #print ('to month: ' + to_month)
    #print ('to day: '   + to_day)
    #print ('to hour: '  + to_hour)

    #print (' ')

    url = 'https://biendata.com/competition/meteorology/bj/2018-04-01-0/2018-04-01-23/2k0d1d8'
    url = 'https://biendata.com/competition/airquality/bj/2018-04-01-0/2018-04-01-23/2k0d1d8'
    url = 'https://biendata.com/competition/meteorology/bj_grid/2018-04-01-0/2018-04-01-23/2k0d1d8'
    url = 'https://biendata.com/competition/meteorology/ld/2018-04-01-0/2018-04-01-23/2k0d1d8'
    url = 'https://biendata.com/competition/airquality/ld/2018-04-01-0/2018-04-01-23/2k0d1d8'
    url = 'https://biendata.com/competition/meteorology/ld_grid/2018-04-01-0/2018-04-01-23/2k0d1d8'

    url_preamble = 'https://biendata.com/competition/'
    
    if city == "London":
        url_city = 'ld'
    elif city == "Beijing":
        url_city = 'bj'
    else:
        print("*** ERROR: unknown city " + city)
        exit(9999)

    if datatype == "air":
        url_datatype = 'airquality/'
    elif datatype == "met":
        url_datatype = 'meteorology/'
    elif datatype == "grid":
        url_datatype = 'meteorology/'
        url_city = url_city + '_grid'
    else:
        print("*** ERROR: unknown datatype " + datatype)
        exit(9998)

    url_from_datetime = '/' + from_year + '-' + from_month + '-' + from_day + '-' + from_hour
    url_to_datetime   = '/' + to_year   + '-' + to_month   + '-' + to_day   + '-' + to_hour

    url = url_preamble + url_datatype + url_city + url_from_datetime + url_to_datetime + '/2k0d1d8'
    print (url)

def load_one_city(city, datatype, from_datetime, to_datetime):
   if datatype == "all":
       load_one_datatype(city, 'air', from_datetime, to_datetime)
       load_one_datatype(city, 'met', from_datetime, to_datetime)
       load_one_datatype(city, 'grid', from_datetime, to_datetime)
   else:
       load_one_datatype(city, datatype, from_datetime, to_datetime)

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