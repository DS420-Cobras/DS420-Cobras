# KDD Load tutorial
# taken from https://biendata.com/forum/view_post_category/9
# 
# Before running, type 'pip install requests' (no quotes) to install the requests library.

import requests
import pandas as pd

url = 'https://biendata.com/competition/meteorology/bj/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("bj_meteorology_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)

url = 'https://biendata.com/competition/airquality/bj/2018-04-01-0/2018-04-01-23/2k0d1d8'
respones= requests.get(url)
with open ("bj_airquality_2018-04-01-0-2018-04-01-23.csv",'w') as f:
    f.write(respones.text)

metDf = pd.read_csv('bj_meteorology_2018-04-01-0-2018-04-01-23.csv')
airDf = pd.read_csv('bj_airquality_2018-04-01-0-2018-04-01-23.csv')

print(metDf.head())
print(airDf.head())
