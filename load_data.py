
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
def load_one_url (city, datatype, from_datetime, to_datetime):

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


def load_one_datatype(city, datatype, from_datetime, to_datetime):
    from_year  = int(from_datetime[:4]) #equiv. to left(from_datetime, 4)
    from_month = int(from_datetime[5:7])
    from_day   = int(from_datetime[8:10])
    from_hour  = int(from_datetime[11:len(from_datetime)])

    to_year  = int(to_datetime[:4]) #equiv. to left(to_datetime, 4)
    to_month = int(to_datetime[5:7])
    to_day   = int( to_datetime[8:10])
    to_hour  = int(to_datetime[11:len(to_datetime)])

    year = from_year
    if (from_year == to_year):
        last_month = to_month
    else:
        last_month = 12



    if ((from_year == to_year) and (from_month == to_month) and (from_day == to_day)):
        last_hour = 23
    else:
        last_hour = to_hour

    month = from_month
    day = from_day
    hour = from_hour

    while year <= int(to_year):
        print("year: " + str(year))
        if (year == int(to_year)):
            last_month = int(to_month)
        while month <= last_month:
            print("  month: " + str(month))
            if ((year == int(to_year)) and (month == int(to_month))):
                last_day = int(to_day)
            elif (month == 2):
                last_day = 28
            elif (month in {9, 4, 6, 11}):
                last_day = 30
            else:
                last_day = 31
            
            #while day <= last_day:
            #    print (str(year) + "-" + str(month) + "-" + str(day))
            #    day = day + 1
            month = month + 1
        year = year + 1
        month = 1


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