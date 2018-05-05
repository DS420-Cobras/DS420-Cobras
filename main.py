import load_data
import pandas as pd
import sklearn.linear_model
import sklearn.ensemble
import matplotlib.pyplot as plt
import plot
import time
import datetime
import numpy as np
import sklearn.preprocessing

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

# Drop columns not useful in analysis
temp.drop(labels='id', axis=1, inplace=True)

# Clean some duplicate categorical variables from weather
temp['weather'].replace('Cloudy','CLOUDY', inplace=True)
temp['weather'].replace('Sunny/clear','CLEAR_DAY', inplace=True)
temp['weather'].replace('Rain','RAIN', inplace=True)
temp['weather'] = temp['weather'].astype('category')

# Create categorical columns from string columns
temp['met_station'] = temp['met_station'].astype('category')
temp['station_id'] = temp['station_id'].astype('category')

# Replace some outliers with median values
temp.loc[temp['humidity']== 999999, 'humidity'] = temp['humidity'].median()
temp.loc[temp['pressure']== 999999, 'pressure'] = temp['pressure'].median()
temp.loc[temp['temperature']== 999999, 'temperature'] = temp['temperature'].median()

# coordinates from weather stations
bj_grid_met_stations = pd.concat([bj_grid_stations, bj_meo_stations.rename(columns={'station_id':'met_station'})], ignore_index=True)
temp = pd.merge(temp, bj_grid_met_stations, how='left', on = 'met_station')

# remove the NANs. not ideal
temp.drop(['latitude','longitude'], axis=1, inplace=True)
temp.drop(['met_station'], axis=1, inplace=True)
temp.dropna(inplace=True)

#temp['met_station'] = temp['met_station'].astype('category')

# Normalize the columns
tempNum = temp.select_dtypes([np.number])
temp[tempNum.columns]=tempNum.apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))

# Handle categorical data
bejDfFinal = pd.get_dummies(temp, 'dum')

"""
for col in temp.columns:
    if str(temp[col].dtype) == 'category':
        continue
    if str(temp[col].dtype) == 'datetime64[ns]':
        continue
    
    print(col, temp[col].dtype)
    scaler = sklearn.preprocessing.StandardScaler(copy = True)
    temp[col] = scaler.fit_transform(temp[col].reshape(-1, 1))
"""

# Create test and training set
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

# No use of time anymore
bejDfFinal.drop(labels='time', axis=1, inplace=True)


targets = ['PM25_Concentration', 'PM10_Concentration', 'O3_Concentration']
#targets = ['PM10_Concentration']
features = [col for col in list(testDf) if ((col not in targets) and (col != 'time'))]

#print(trainDf[features].head(20))

#lm = sklearn.linear_model.LinearRegression(n_jobs=-1)
lm = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=42)
lm.fit(trainDf[features], trainDf[targets])
print(lm.score(testDf[features], testDf[targets]))

# Plot the feature importances of the random forest model
if False:
    importances = lm.feature_importances_
    std = np.std([tree.feature_importances_ for tree in lm.estimators_],
             axis=0)
    indices = np.argsort(importances)[::-1]

    # Print the feature ranking
    print("Feature ranking:")

    for f in range(trainDf[features].shape[1]):
        print("%d. feature %d (%f)" % (f + 1, indices[f], importances[indices[f]]))

    plt.figure(figsize=(15,10))
    plt.title("Feature importances")
    plt.bar(range(trainDf[features].shape[1]), importances[indices],
           color="r", yerr=std[indices], align="center")
    plt.xticks(range(trainDf[features].shape[1]), indices)
    plt.xlim([-1, trainDf[features].shape[1]])
    plt.show()

if False:
    #lm.fit(trainDf[features], trainDf['PM10_Concentration'])
    #print(lm.score(testDf[features], testDf['PM10_Concentration']))
    predictedValues = lm.predict(testDf[features])
    actualValues = testDf['PM10_Concentration']
    plot.CreateMultiplePredictedAndActualValuesPlots([predictedValues], [actualValues], 'Random Forest')
