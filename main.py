import load_data
import pandas as pd
import sklearn.linear_model
import sklearn.ensemble
import matplotlib.pyplot as plt
import plot
import time
import datetime
import numpy as np

allDf = load_data.getPandasDataframes()

bejAirDf = allDf[('Beijing', 'air')]
bejMetDf = allDf[('Beijing', 'met')]
bejGrd = allDf[('Beijing', 'grid')]

bejAirDf['newTime'] = pd.to_datetime(bejAirDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
bejMetDf['time'] = pd.to_datetime(bejMetDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
bejGrd['time'] = pd.to_datetime(bejGrd['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')

bejMetDf = bejMetDf.rename(columns={'station_id':'met_station'})
bejGrd = bejGrd.rename(columns={'station_id':'met_station'})

bejDf = pd.DataFrame()
for key in ['station_id', 'PM25_Concentration', 'PM10_Concentration', 'NO2_Concentration', 'CO_Concentration', 'O3_Concentration', 'SO2_Concentration']:
    bejDf[key] = bejAirDf[key]
bejDf['time'] = bejAirDf['newTime']

bejDf['hour'] = bejAirDf['newTime'].dt.hour
#bejDf['minute'] = bejAirDf['newTime'].dt.minute
#bejDf['second'] = bejAirDf['newTime'].dt.second
bejDf['day'] = bejAirDf['newTime'].dt.day
bejDf['month'] = bejAirDf['newTime'].dt.month
#bejDf['year'] = bejAirDf['newTime'].dt.year
bejDf['dayofweek'] = bejAirDf['newTime'].dt.dayofweek
# bejDf['dayofweek'] = pd.Categorical(bejDf['dayofweek'], ordered=False)

valueDict = {(row['station_id'],row['time'].to_pydatetime()):row['PM10_Concentration'] for index, row in bejDf.iterrows()}
bejDf['PM10_3'] = bejDf['PM10_Concentration']
bejDf['PM10_3B'] = bejDf['PM10_Concentration']
bejDf['PM10_3C'] = bejDf['PM10_Concentration']
for index, row in bejDf.iterrows():
    rtime = row['time'].to_pydatetime()
    rtime = rtime - datetime.timedelta(hours=1)
    rtime2 = rtime - datetime.timedelta(hours=1)
    rtime3 = rtime2 - datetime.timedelta(hours=1)
    bejDf.at[index, 'PM10_3'] = valueDict.get((row['station_id'], rtime), np.NaN)
    bejDf.at[index, 'PM10_3B'] = valueDict.get((row['station_id'], rtime2), np.NaN)
    bejDf.at[index, 'PM10_3C'] = valueDict.get((row['station_id'], rtime3), np.NaN)


stationDf = bejDf[bejDf['station_id']=='tiantan_aq']

#ToDo: limit to one station for now
#bejDf = stationDf

if False:
    plt.scatter(x=bejDf.PM25_Concentration, y=bejDf.PM10_Concentration)
    plt.xlabel("time", fontsize=14)
    plt.ylabel("PM10_Concentration", fontsize=14)
    f = plt.gcf()
    f.set_figheight(10)
    f.set_figwidth(15)
    plt.show()


# Business Hours Variable (between 8am and 6pm)
bejDf['businessHours'] = 0
bejDf.loc[(bejDf['hour'] >= 8) & (bejDf['hour']<=18)==0, 'businessHours'] = 1

# import geospatial data
bj1718meo = pd.read_csv('viz/stash/beijing_17_18_meo.csv')
bj1718meo = bj1718meo.rename(columns={'station_id':'met_station'})
bj_meo_stations = pd.read_csv('viz/stash/Beijing_meo_stations.csv')
bj_grid_stations = pd.read_csv('viz/stash/beijing_grid_stations.csv', names=['met_station', 'latitude', 'longitude'])
bj_ring = pd.read_csv('viz/stash/Beijing_Neighbors.csv')
bj_nn = pd.read_excel('viz/stash/Beijing_Neighbors.xlsx')
bj_nn = bj_nn.rename(columns={"aq_station": "station_id"})
bj_nn[bj_nn['met_station']=='fangshan_met'] =  'fangshan_meo'


# Join the data
temp = bejDf.merge(bj_nn, on='station_id', how='left')
bejWeather = pd.concat([bejMetDf, bejGrd])
temp = pd.merge(temp, bejWeather,  how='left', on=['met_station','time'])
temp = temp.drop(columns='id')

# Clean some duplicate categorical variables from weather
temp['weather'].replace('Cloudy','CLOUDY', inplace=True)
temp['weather'].replace('Sunny/clear','CLEAR_DAY', inplace=True)
temp['weather'].replace('Rain','RAIN', inplace=True)


# Replace some outliers with median values
temp.loc[temp['humidity']== 999999, 'humidity'] = temp['humidity'].median()
temp.loc[temp['pressure']== 999999, 'pressure'] = temp['pressure'].median()
temp.loc[temp['temperature']== 999999, 'temperature'] = temp['temperature'].median()

# coordinates from weather stations
bj_grid_met_stations = pd.concat([bj_grid_stations, bj_meo_stations.rename(columns={'station_id':'met_station'})], ignore_index=True)
temp = pd.merge(temp, bj_grid_met_stations, how='left', on = 'met_station')

# remove the NANs. not ideal
temp_no_null = temp.dropna()
tempNum = temp_no_null.select_dtypes([np.number])
tempNum.drop(['latitude','longitude'], axis=1, inplace=True)
temp_no_null[tempNum.columns]=tempNum.apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))
bejDfFinal = pd.get_dummies(temp_no_null, 'dum')

# Handle categorical data
#bejDf = pd.get_dummies(bejDf, 'dum')

ct = datetime.datetime.utcnow() - datetime.timedelta(hours=48)
splitDate = pd.datetime(ct.year,ct.month,ct.day,  ct.hour)
trainDf = bejDfFinal[bejDfFinal['time'] < splitDate]
testDf = bejDfFinal[bejDfFinal['time'] >= splitDate]

cur = datetime.datetime.utcnow()
current_time = pd.datetime(cur.year,cur.month,cur.day,cur.hour)
d = list(testDf.time)
date_list = [current_time - datetime.timedelta(hours=x) for x in range(0, 48)]
date_list = [pd.to_datetime(i, format='%Y-%m-%d %H:%M:%S') for i in date_list]
missingDatesFromTestDf = np.setdiff1d(sorted(date_list),list(set(sorted(d))))
print(list(missingDatesFromTestDf))


targets = ['PM25_Concentration', 'PM10_Concentration', 'O3_Concentration']
features = [col for col in list(testDf) if ((col not in targets) and (col != 'time'))]

#print(trainDf[features].head(20))

#lm = sklearn.linear_model.LinearRegression(n_jobs=-1)
lm = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=42)
lm.fit(trainDf[features], trainDf[targets])
print(lm.score(testDf[features], testDf[targets]))

#lm.fit(trainDf[features], trainDf['PM10_Concentration'])
#print(lm.score(testDf[features], testDf['PM10_Concentration']))

#predictedValues = lm.predict(testDf[features])
#actualValues = testDf['PM10_Concentration']
#mn = bejDf['PM10_Concentration'].mean()
#for i in range(len(predictedValues)):
#    predictedValues[i] = mn
#plot.CreateMultiplePredictedAndActualValuesPlots([predictedValues], [actualValues], 'LinearRegression')
