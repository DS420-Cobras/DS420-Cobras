import load_data
import pandas as pd
import sklearn.linear_model

allDf = load_data.getPandasDataframes()

bejAirDf = allDf[('Beijing', 'air')]
bejMetDf = allDf[('Beijing', 'met')]
bejGrd = allDf[('Beijing', 'grid')]

bejAirDf['newTime'] = pd.to_datetime(bejAirDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')

bejDf = pd.DataFrame()
for key in ['station_id', 'PM25_Concentration', 'PM10_Concentration', 'NO2_Concentration', 'CO_Concentration', 'O3_Concentration', 'SO2_Concentration']:
    bejDf[key] = bejAirDf[key]

bejDf['hour'] = bejAirDf['newTime'].dt.hour
bejDf['minute'] = bejAirDf['newTime'].dt.minute
bejDf['second'] = bejAirDf['newTime'].dt.second
bejDf['day'] = bejAirDf['newTime'].dt.day
bejDf['month'] = bejAirDf['newTime'].dt.month
bejDf['year'] = bejAirDf['newTime'].dt.year

#print(bejDf.head())
#print(bejDf.tail())

# ToDo: We should not drop NA values since we are losing 1/3 of the dataset
#print(bejDf.describe())
bejDf.dropna(inplace=True)
#print(bejDf.describe())

# Handle categorical data
bejDf = pd.get_dummies(bejDf, 'dum')
#print(bejDf.head())
#print(bejDf.tail())

targets = ['PM25_Concentration', 'PM10_Concentration', 'NO2_Concentration', 'CO_Concentration', 'O3_Concentration', 'SO2_Concentration']
features = [col for col in list(bejDf) if col not in targets]

lm = sklearn.linear_model.LinearRegression(n_jobs=-1)
for key in targets:
    lm.fit(bejDf[features], bejDf[key])
    print(key, lm.score(bejDf[features], bejDf[key]))