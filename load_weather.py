import forecastio #module to get weather data from darksky.net
import pandas as pd
import numpy as np
import json
from pandas.io.json import json_normalize
from calendar import monthrange
import os.path
import datetime
#function to get weather
def get_met_data(year, month, day, numdays, api_key, lat, lng, station_id):
    #get url to retrieve weather information
    start_date = datetime.datetime(year, month, day)
    date_list = [start_date + datetime.timedelta(days = x) for x in range(0, numdays)]
    hist = np.arange(0, len(date_list)).tolist()
    forecast = []
    for n in hist:
        forecast.append(forecastio.load_forecast(api_key, lat, lng, time = date_list[n]))
    #jspn object
    met_data = pd.DataFrame()
    for i in np.arange(0, len(forecast)).tolist():
        data = json_normalize(forecast[i].json['hourly']['data'])
        met_data = pd.concat([met_data, data])
    #missing variables from original data added    
    met_data['datetime'] = met_data['time'].apply(lambda x: datetime.datetime.fromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'))
    met_data['lat'] = lat
    met_data['long'] = lng
    met_data['station_id'] = station_id
    return met_data
#parameters
api_key = '276d9b4ae748ec5d42ab2ababe8435cc' #apikey obtained from darksky.net 
start = '2018-04-05' #start day
numdays = 3 #forecast horizon
#Cargamos la tabla con las coordenadas
start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
#csv with stations, latitude and longitude, and api keys available from 'https://github.com/patarol/kdd2018_stations_list/blob/master/stations_list.csv'
station_met =  pd.read_csv(r'viz\Beijing_points_mini.csv')
#call get_met_data function
forecast_48 = pd.DataFrame()
for i in np.arange(station_met.shape[0]).tolist():
    print(station_met['station_id'][i])
    forecast_48 = pd.concat([forecast_48, get_met_data(start_date.year, start_date.month, start_date.day, numdays, api_key, 
                                             station_met['latitude'][i], station_met['longitude'][i], station_met['station_id'][i])])
forecast_48.to_csv(r'viz\Beijing_weather.csv')
