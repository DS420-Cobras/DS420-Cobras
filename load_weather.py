import forecastio #module to get weather data from darksky.net
import pandas as pd
import numpy as np
import json
from pandas.io.json import json_normalize
from calendar import monthrange
import os.path
import datetime

#api_key = '276d9b4ae748ec5d42ab2ababe8435cc' #apikey obtained from darksky.net 
#api_key = '999653ec682af395046067847b4f4948' #apikey obtained from darksky.net by Yash
api_key = '40a186e05ecf67b4dfd467472fdd35bb' #another apikey obtained from darksky.net by Yash

def get_met_data(start_date, numdays, api_key, lat, lng, station_id):
    "Function to get weather"

    #get url to retrieve weather information
    date_list = [start_date + datetime.timedelta(days = x) for x in range(0, numdays)]
    hist = np.arange(0, len(date_list)).tolist()
    forecast = []
    for n in hist:
        # If this raises an error, it's probably because you exhausted the allocated calls for the
        # api key currently in use.  Scroll up to top, switch which key is active, or go get another.
        forecast.append(forecastio.load_forecast(api_key, lat, lng, date_list[n]))
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

def getWeatherDataRange(startDate, endDate, stationsNeeded, cityName, shortRun = True):
    "Retrieves the weather data from file or from web"
    assert(startDate<endDate)
    if os.path.exists('viz\\' + cityName + '_weather.csv'):
        cached =  pd.read_csv('viz\\' + cityName + '_weather.csv')
    else:
        cached = pd.DataFrame()
    if 'datetime' in set(cached):
        cached['datetime'] = pd.to_datetime(cached['datetime'], errors='coerce', format='%Y-%m-%d %H:%M:%S')

    alreadyHave = {(row[1],row[2]) for row in cached.loc[:, ['station_id', 'datetime']].itertuples()}

    datesNeeded = []
    curDate = startDate
    while curDate <= endDate:
        datesNeeded.append(curDate)
        curDate = curDate + datetime.timedelta(hours=24)
    count = 0
    station_met =  pd.read_csv('viz\\' + cityName + '_points.csv')
    for stations in stationsNeeded:
        if count == 0 and shortRun:
            break
        stationInfo = station_met[station_met['station_id'] == stations]
        print(str(stationInfo['station_id'].values[0]))
        prevCount = count
        for dates in datesNeeded:
            if count == 3 and shortRun:
                break
            if (stations, dates) not in alreadyHave:
                count += 1
                cached = pd.concat([cached, get_met_data(dates, 1, api_key, float(stationInfo['latitude']), float(stationInfo['longitude']), str(stationInfo['station_id'].values[0]) )])
        for i in range(5): # Try 5 times
            cached = cached[np.logical_not(cached.duplicated())] # Remove duplicates if they somehow make it into the system
            cached = cached[np.logical_not(cached[['station_id', 'time']].duplicated())]
            if cached['datetime'].dtype == np.dtype('O'):
                cached['datetime'] = pd.to_datetime(cached['datetime'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
            if count != prevCount: # Only write to file if we loaded something from internet
                try:
                    cached.to_csv(os.path.join('viz', cityName + '_weather.csv'), index=False)
                except:
                    if i == 4:
                        raise
                else:
                    break
    return cached
