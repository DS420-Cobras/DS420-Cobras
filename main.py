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
import load_weather
from itertools import product
import submit_preds

allDf = load_data.getPandasDataframes()

beijingWeatherLoaded = ['aotizhongxin_aq','badaling_aq','beibuxinqu_aq','daxing_aq','dingling_aq','donggaocun_aq','dongsi_aq','dongsihuan_aq','fangshan_aq','fengtaihuayuan_aq',
'guanyuan_aq','gucheng_aq','huairou_aq','liulihe_aq','mentougou_aq','miyun_aq','miyunshuiku_aq','nansanhuan_aq','nongzhanguan_aq','pingchang_aq','pinggu_aq',
'qianmen_aq','shunyi_aq','tiantan_aq','tongzhou_aq','wanliu_aq','wanshouxigong_aq','xizhimenbei_aq','yanqin_aq','yizhuang_aq','yongdingmennei_aq']

def doAnalysis2(cityBej = True):
    "Perform full analysis on the specified city"
    cityName = 'Beijing' if cityBej else "London"
    # Air data
    bejDf = allDf[(cityName, 'air')]
    bejDf['time'] = pd.to_datetime(bejDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')

    startDate = np.min(bejDf['time'])
    now = datetime.datetime.utcnow()
    endDate = datetime.datetime.strptime(str(now.date().year) + '-' + str(now.date().month) + '-' + str(now.date().day), '%Y-%m-%d') + datetime.timedelta(hours=96)
    firstPredTime = datetime.datetime.strptime(str(now.date().year) + '-' + str(now.date().month) + '-' + str(now.date().day+1), '%Y-%m-%d')
    lastPredTime = datetime.datetime.strptime(str(now.date().year) + '-' + str(now.date().month) + '-' + str(now.date().day+3), '%Y-%m-%d')

    # Dataframe useful for final predictions
    submissionTimes = []
    subTime = firstPredTime
    while subTime <lastPredTime:
        submissionTimes.append(subTime)
        subTime = subTime + datetime.timedelta(hours=1)
    subTimeToIdDict = {t:i for i,t in enumerate(submissionTimes)}

    stationlist = ['dongsi_aq', 'tiantan_aq', 'guanyuan_aq', 'wanshouxigong_aq', 'aotizhongxin_aq', 'nongzhanguan_aq', 'wanliu_aq', 'beibuxinqu_aq', 'zhiwuyuan_aq', 'fengtaihuayuan_aq', 'yungang_aq', 'gucheng_aq', 'fangshan_aq',
               'daxing_aq', 'yizhuang_aq', 'tongzhou_aq', 'shunyi_aq', 'pingchang_aq', 'mentougou_aq', 'pinggu_aq', 'huairou_aq', 'miyun_aq', 'yanqin_aq', 'dingling_aq', 'badaling_aq', 'miyunshuiku_aq',
               'donggaocun_aq', 'yongledian_aq', 'yufa_aq', 'liulihe_aq', 'qianmen_aq', 'yongdingmennei_aq', 'xizhimenbei_aq', 'nansanhuan_aq', 'dongsihuan_aq']
    if not cityBej:
        stationlist = ['CD1', 'BL0', 'GR4', 'MY7', 'HV1', 'GN3', 'GR9', 'LW2', 'GN0', 'KF1', 'CD9','ST5', 'TH4']
    submissionDf = pd.DataFrame(list(product(stationlist, submissionTimes)), columns=['station_id', 'time'])
    indxArray = []
    for i in range(len(submissionDf)):
        indxArray.append(str(subTimeToIdDict[submissionDf['time'][i]]))
    submissionDf['test_id'] = submissionDf['station_id'] + '#' + np.asarray(indxArray)

    # Do not fit over all the stations. Only fit over the stations we want. The benefit is that we have less data to deal with and less cleanup later on
    # The disadvantage is overfitting. ToDo: Fix this later.
    bejDf = bejDf[bejDf['station_id'].isin(stationlist)]

    stationsNeeded = np.unique(bejDf['station_id'])

    weatherDf = load_weather.getWeatherDataRange(startDate, endDate, stationsNeeded, cityName, False)
    weatherDf['time'] = weatherDf['datetime']

    # ToDo: Change inner join to left join
    bejDf = bejDf.merge(weatherDf, how='inner', on=['station_id', 'time'])
    submissionDf = submissionDf.merge(weatherDf, how='inner', on=['station_id', 'time'])

    bejDf.drop(labels='id', axis=1, inplace=True)
    bejDf.drop(labels='datetime', axis=1, inplace=True)
    bejDf.drop(labels='lat', axis=1, inplace=True)
    bejDf.drop(labels='long', axis=1, inplace=True)
    
    # ToDo: Undo. Removed because they have a lot of empty cells. Replace with more meaningful values
    bejDf.drop(labels='ozone', axis=1, inplace=True)
    submissionDf.drop(labels='ozone', axis=1, inplace=True)

    bejDf.drop(labels='precipIntensity', axis=1, inplace=True)
    submissionDf.drop(labels='precipIntensity', axis=1, inplace=True)

    bejDf.drop(labels='precipProbability', axis=1, inplace=True)
    submissionDf.drop(labels='precipProbability', axis=1, inplace=True)

    bejDf.drop(labels='pressure', axis=1, inplace=True)
    submissionDf.drop(labels='pressure', axis=1, inplace=True)

    bejDf.drop(labels='uvIndex', axis=1, inplace=True)
    submissionDf.drop(labels='uvIndex', axis=1, inplace=True)

    bejDf.drop(labels='windGust', axis=1, inplace=True)
    submissionDf.drop(labels='windGust', axis=1, inplace=True)

    bejDf.drop(labels='cloudCover', axis=1, inplace=True)
    submissionDf.drop(labels='cloudCover', axis=1, inplace=True)

    bejDf.drop(labels='precipType', axis=1, inplace=True)
    submissionDf.drop(labels='precipType', axis=1, inplace=True)

    bejDf.drop(labels='visibility', axis=1, inplace=True)
    submissionDf.drop(labels='visibility', axis=1, inplace=True)

    bejDf['hour'] = bejDf['time'].dt.hour
    bejDf['day'] = bejDf['time'].dt.day
    bejDf['month'] = bejDf['time'].dt.month
    bejDf['dayofweek'] = bejDf['time'].dt.dayofweek

    submissionDf['hour'] = submissionDf['time'].dt.hour
    submissionDf['day'] = submissionDf['time'].dt.day
    submissionDf['month'] = submissionDf['time'].dt.month
    submissionDf['dayofweek'] = submissionDf['time'].dt.dayofweek

    # Business Hours Variable (between 8am and 6pm)
    #bejDf['businessHours'] = 0
    #bejDf.loc[(bejDf['hour'] >= 8) & (bejDf['hour']<=18)==0, 'businessHours'] = 1

    if not cityBej:
        bejDf.drop(labels='CO_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='O3_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='SO2_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='NO2_Concentration', axis=1, inplace=True)

    bejDf.dropna(inplace=True)

    bejDf['summary'] = bejDf['summary'].astype('category')
    bejDf['icon'] = bejDf['icon'].astype('category')
    submissionDf['summary'] = submissionDf['summary'].astype('category')
    submissionDf['icon'] = submissionDf['icon'].astype('category')

    submissionDf['name'] = submissionDf['station_id'] + '#' + submissionDf['time'].dt.hour.apply(str)

    # Handle categorical data
    # ToDo: Use drop_first  and dummy_na arguments of get_dummies and move this method before drop_na
    bejDf = pd.get_dummies(bejDf, 'dum')
    # Set certain categorical columns to zero before calling get_dummies so that we do not overwrite values
    submissionDf['dum_Breezy'] = np.uint8(0)
    submissionDf['dum_Windy and Partly Cloudy'] = np.uint8(0)
    submissionDf['dum_Breezy and Partly Cloudy'] = np.uint8(0)
    submissionDf['dum_wind'] = np.uint8(0)
    submissionDf['dum_Foggy'] = np.uint8(0)
    submissionDf['dum_Windy and Partly Cloudy'] = np.uint8(0)
    submissionDf['dum_Breezy and Foggy'] = np.uint8(0)
    submissionDf['dum_fog'] = np.uint8(0)
    submissionDf['dum_Breezy and Mostly Cloudy'] = np.uint8(0)
    submissionDf['dum_Windy'] = np.uint8(0)
    test_id = submissionDf['test_id']
    submissionDf.drop(labels='test_id', axis=1, inplace=True)
    submissionDf = pd.get_dummies(submissionDf, 'dum') #ToDo: Fix. Should use the same dataframe as bejDf
    submissionDf['test_id'] = test_id

    for col in {'dum_Overcast', 'dum_Rain and Breezy', 'dum_rain', 'dum_Light Rain', 'dum_Breezy and Overcast', 'dum_Light Rain and Breezy', 'dum_cloudy'}:
        if col not in set(submissionDf):
            submissionDf[col] = np.uint8(0)

    # What predictions do we get without direct time component?
    bejDf.drop(labels='time', axis=1, inplace=True)
    submissionDf.drop(labels='time', axis=1, inplace=True)
    
    #bejDf.to_csv('temp.csv', index=False)

    # Drop the pollution columns that we do not need
    if cityBej:
        bejDf.drop(labels='NO2_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='CO_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='SO2_Concentration', axis=1, inplace=True)

    targets = ['PM25_Concentration', 'PM10_Concentration', 'O3_Concentration']
    if not cityBej:
        targets = ['PM25_Concentration', 'PM10_Concentration']
    features = [col for col in list(bejDf) if (col not in targets)]

    assert((set(bejDf) - set(submissionDf) - set(targets)) == set())

    for target in targets:
        # K-Fold cross validation
        kf = sklearn.model_selection.KFold(n_splits=5, shuffle=True, random_state=42)
        bejDf.reset_index(drop=True)
        modelScores = []
        for train_index, test_index in kf.split(bejDf):
            X_train, X_test = bejDf.iloc[train_index][features], bejDf.iloc[test_index][features]
            Y_train = bejDf.iloc[train_index][[target]]
            Y_test = bejDf.iloc[test_index][[target]]

            lm = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=42)
            lm.fit(X_train, Y_train.values.ravel())
            score = lm.score(X_test, Y_test)
            modelScores.append((score, lm))
        modelScores.sort()
        modelUsed = modelScores[len(modelScores)//2 +1][1] # Not picking the best model as it could have been best because of the way we split the initial data
        scoreUsed = modelScores[len(modelScores)//2 +1][0]
        print(target, [val[0] for val in modelScores], scoreUsed)
        submissionDf[target] = modelUsed.predict(submissionDf.iloc[:][features])
    retainColumns = ['test_id']
    retainColumns += targets
    for col in list(submissionDf):
        if col in retainColumns:
            continue
        submissionDf.drop(labels=col, axis=1, inplace=True)
    renameDict = {'PM25_Concentration':'PM2.5', 'PM10_Concentration':'PM10', 'O3_Concentration':'O3'}
    for key in renameDict:
        submissionDf.rename(columns={key:renameDict[key]}, inplace=True)

    # Final checks
    if cityBej:
        assert(len(submissionDf) == 1680)
        assert(len(list(submissionDf)) == 4)
    else:
        assert(len(submissionDf) == 624)
        assert(len(list(submissionDf)) == 3)

    return submissionDf


bejSubDf = doAnalysis2(cityBej=True)
lonSubDf = doAnalysis2(cityBej=False)

combDf = pd.concat([bejSubDf, lonSubDf])
dt = datetime.datetime.utcnow().date()
filename = 'mainSubmission' + "_" + str(dt.day) + "_ " + str(dt.month) + "_" + str(dt.year) + ".csv"
combDf.to_csv(filename, index=False, sep=',', columns=['test_id', 'PM2.5', 'PM10', 'O3'])

#submit_preds.submit_preds(filename, 'yashbhandari', 'Sample means', filename=filename)