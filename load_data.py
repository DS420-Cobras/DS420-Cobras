
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
