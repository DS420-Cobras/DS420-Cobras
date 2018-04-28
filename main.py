import load_data
import pandas as pd
import sklearn.linear_model
import sklearn.ensemble
import matplotlib.pyplot as plt
import plot

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

splitDate = pd.datetime(2018,4,20)
trainDf = bejDf[bejDf['time'] < splitDate]
testDf = bejDf[bejDf['time'] >= splitDate]

targets = ['PM25_Concentration', 'PM10_Concentration', 'NO2_Concentration', 'CO_Concentration', 'O3_Concentration', 'SO2_Concentration']
features = [col for col in list(testDf) if ((col not in targets) and (col != 'time'))]

print(testDf[features].head(20))

lm = sklearn.linear_model.LinearRegression(n_jobs=-1)
#lm = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=42)
#lm.fit(trainDf[features], trainDf[targets])
#print(lm.score(testDf[features], testDf[targets]))

lm.fit(trainDf[features], trainDf['PM10_Concentration'])
print(lm.score(testDf[features], testDf['PM10_Concentration']))

predictedValues = lm.predict(testDf[features])
actualValues = testDf['PM10_Concentration']
plot.CreateMultiplePredictedAndActualValuesPlots([predictedValues], [actualValues], 'LinearRegression')
