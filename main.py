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
#bejDf['dayofweek'] = bejAirDf['newTime'].dt.dayofweek
#bejDf['dayofweek'] = pd.Categorical(bejDf['dayofweek'], ordered=False)

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
bejDf = stationDf

if False:
    plt.scatter(x=bejDf.PM25_Concentration, y=bejDf.PM10_Concentration)
    plt.xlabel("time", fontsize=14)
    plt.ylabel("PM10_Concentration", fontsize=14)
    f = plt.gcf()
    f.set_figheight(10)
    f.set_figwidth(15)
    plt.show()

# ToDo: We should not drop NA values since we are losing 1/3 of the dataset
bejDf.dropna(inplace=True)

# Handle categorical data
bejDf = pd.get_dummies(bejDf, 'dum')

ct = datetime.datetime.utcnow() - datetime.timedelta(days=3)
splitDate = pd.datetime(ct.year,ct.month,ct.day,  ct.hour)
trainDf = bejDf[bejDf['time'] < splitDate]
testDf = bejDf[bejDf['time'] >= splitDate]

targets = ['PM25_Concentration', 'PM10_Concentration', 'NO2_Concentration', 'CO_Concentration', 'O3_Concentration', 'SO2_Concentration']
features = [col for col in list(testDf) if ((col not in targets) and (col != 'time'))]

#print(trainDf[features].head(20))

lm = sklearn.linear_model.LinearRegression(n_jobs=-1)
#lm = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=42)
#lm.fit(trainDf[features], trainDf[targets])
#print(lm.score(testDf[features], testDf[targets]))

lm.fit(trainDf[features], trainDf['PM10_Concentration'])
print(lm.score(testDf[features], testDf['PM10_Concentration']))

predictedValues = lm.predict(testDf[features])
actualValues = testDf['PM10_Concentration']
mn = bejDf['PM10_Concentration'].mean()
for i in range(len(predictedValues)):
    predictedValues[i] = mn
#plot.CreateMultiplePredictedAndActualValuesPlots([predictedValues], [actualValues], 'LinearRegression')
