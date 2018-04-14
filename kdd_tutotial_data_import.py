# KDD Load tutorial
# taken from https://biendata.com/forum/view_post_category/9
# 
# Before running, type 'pip install requests' (no quotes) to install the requests library.

import requests
import pandas as pd

#-----------------------< BEIJING >----------------------

# Beijing met
url = 'https://biendata.com/competition/meteorology/bj/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("data/Beijing/met/bj_meteorology_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)

# Beijing air
url = 'https://biendata.com/competition/airquality/bj/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("data/Beijing/air/bj_airquality_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)


# Beijing grid
url = 'https://biendata.com/competition/meteorology/bj_grid/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("data/Beijing/grid/bj_grid_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)

#-----------------------< LONDON >----------------------

# London met
url = 'https://biendata.com/competition/meteorology/ld/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("data/London/met/ld_meteorology_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)

# London air
url = 'https://biendata.com/competition/airquality/ld/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("data/London/air/ld_airquality_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)


# London grid
url = 'https://biendata.com/competition/meteorology/ld_grid/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("data/London/grid/ld_grid_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)


metDf = pd.read_csv('data/Beijing/met/bj_meteorology_2018-04-01-0-2018-04-01-23.csv')
airDf = pd.read_csv('data/Beijing/air/bj_airquality_2018-04-01-0-2018-04-01-23.csv')

print(metDf.head())
print(airDf.head())
