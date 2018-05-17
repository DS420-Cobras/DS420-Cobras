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
import os.path

# Use MeanMedianEnsamble, Smape, fastPred
algosPresent = ['Smape', 'MeanMedianEnsamble', 'Means', 'Median', 'LassoStationFit', 'RandomForest', 'StationHourMedian']
algoToUse = algosPresent[1]

f = open('log.txt', 'a')

allDf = load_data.getPandasDataframes()

# Copied from discussion forum
#def calc_smape(labels, forecasts): 
#    # arrange both indices 
#    forecasts = forecasts.loc[labels.index].copy() # calc symmetric absolute percentage error (not SMAPE) 
#    sape_df = ((labels-forecasts).abs()/((labels+forecasts)/2)) # set sape value 0 if actual value and forecast value are both 0 
#    sape_df[(labels==0)&(forecasts==0)] = 0 # form the dataframe in line, drop nan, and calc SMAPE 
#    sape_array = sape_df.values.reshape([-1]) 
#    smape = sape_array[~np.isnan(sape_array)].mean() 
#    return smape # labels and forecasts have same format 

def smape(actual, predicted):
    dividend= np.abs(np.array(actual) - np.array(predicted))
    denominator = np.array(actual) + np.array(predicted)
    
    return 2 * np.mean(np.divide(dividend, denominator, out=np.zeros_like(dividend), where=denominator!=0, casting='unsafe'))

class MeanMedianEnsamble(sklearn.base.RegressorMixin):
    "Ensemble method that predicts average of mean and median"
    def __init__(self, features=[]):
        # We are doing cheating here. We are adding station_id in the features list
        if 'station_id' not in features:
            features.append('station_id')
        self.meanModel = MeansFit(features)
        self.medianModel = MediansFit(features)

    def fit(self, X, Y):
        self.meanModel.fit(X, Y)
        self.medianModel.fit(X, Y)

    def predict(self, X):
        m1 = self.meanModel.predict(X)
        m2 = self.medianModel.predict(X)
        return (m1 + m2)/2

class MeansFit(sklearn.base.RegressorMixin):
    "Predict the mean value"
    def __init__(self, features=[]):
        # We are doing cheating here. We are adding station_id in the features list
        if 'station_id' not in features:
            features.append('station_id')
    
    def fit(self, X, Y):
        self.groupMeans_ = {}
        self.overallMean_ = np.mean(Y)
        df = X.copy()
        df['target'] = Y
        for index, row in df.groupby(['station_id']).mean().iterrows():
            v = row['target']
            self.groupMeans_[index] = self.overallMean_ if np.isnan(v) else v
        df = None
        return self

    def predict(self, X):
        values = [(self.groupMeans_[station] if station in self.groupMeans_ else self.overallMean_) for station in X['station_id'] ]
        return np.asarray(values)

class MediansFit(sklearn.base.RegressorMixin):
    "Predict the medians value"
    def __init__(self, features=[]):
        # We are doing cheating here. We are adding station_id in the features list
        if 'station_id' not in features:
            features.append('station_id')
    
    def fit(self, X, Y):
        self.groupMedian_ = {}
        self.overallMedian_ = np.median(Y)
        df = X.copy()
        df['target'] = Y
        for index, row in df.groupby(['station_id']).median().iterrows():
            v = row['target']
            self.groupMedian_[index] = self.overallMedian_ if np.isnan(v) else v
        df = None
        return self

    def predict(self, X):
        values = [(self.groupMedian_[station] if station in self.groupMedian_ else self.overallMedian_) for station in X['station_id'] ]
        return np.asarray(values)

class StationHourMedian(sklearn.base.RegressorMixin):
    "Predict the medians value"
    def __init__(self, features=[]):
        # We are doing cheating here. We are adding station_id in the features list
        if 'station_id' not in features:
            features.append('station_id')
        if 'hour2' not in features:
            features.append('hour2')
        self.medFit = MediansFit(features)
    
    def fit(self, X, Y):
        self.medFit.fit(X, Y)
        self.groupMedian_ = {}
        df = X.copy()
        df['target'] = Y
        for index, row in df.groupby(['station_id', 'hour2']).median().iterrows():
            v = row['target']
            if not np.isnan(v):
                self.groupMedian_[index] = v
        df = None
        return self

    def predict(self, X):
        #features = [col for col in list(X) if col != 'station_id']
        values = []
        for index, row in X.iterrows():
            station = row['station_id']
            hour2 = row['hour2']
            if (station, hour2) in self.groupMedian_:
                Y = self.groupMedian_[(station, hour2)]
                values.append(Y)
            elif station in self.medFit.groupMedian_:
                values.append(self.medFit.groupMedian_[station])
            else:
                values.append(self.medFit.overallMedian_)
                #Y = self.medFit.predict([row])
                #values.append(Y[0])
        return np.asarray(values)

class LassoStationFit(sklearn.base.RegressorMixin):
    "Predict the lasso regrssion"
    def __init__(self, features=[]):
        # We are doing cheating here. We are adding station_id in the features list
        if 'station_id' not in features:
            features.append('station_id')
    
    def fit(self, X, Y):
        self.groupModl_ = {}
        self.overallMedian_ = np.median(Y)
        df = X.copy()
        df['target'] = Y
        features = [col for col in list(df) if col not in ('target', 'station_id')]
        for name, group in df.groupby(['station_id']):
            modl = sklearn.linear_model.LassoCV(random_state=42, positive=True)
            modl.fit(group[features], group['target'])
            self.groupModl_[name] = modl
        df = None
        return self

    def predict(self, X):
        features = [col for col in list(X) if col != 'station_id']
        values = []
        for index, row in X.iterrows():
            station = row['station_id']
            if station in self.groupModl_:
                Y = self.groupModl_[station].predict([row[features]])
                values.append(Y[0])
            else:
                values.append(self.overallMedian_)
        return np.asarray(values)



class SmapeFit(sklearn.base.RegressorMixin):
    "Predict the value based on the smallest smape"
    def fit(self, X, Y):
        self.mfit.fit(X, Y)
        self.groupmapes_ = {}
        df = X.copy()
        df['target'] = Y
        for name, group in df.groupby(['station_id']):
            mn = np.min(group['target'])
            mx = np.mean(group['target'])
            mn = 0 if mn < 0 else mn
            mx = 0 if mx < 0 else mx
            if mn >= mx:    continue
            stp = (mx - mn)/500
            minError = None
            minErrorVal = None
            v = mn
            count = 0
            while v < mx:
                v += stp
                pVal = [v]*len(group)
                err = smape(group['target'], pVal)
                if (minError == None) or (minError > err):
                    minError = err
                    minErrorVal = v
                    count = 0
                else:
                    count += 1
                if count > 20:
                    break
            self.groupmapes_[name] = minErrorVal
        df = None
        return self

    def predict(self, X):
        values = [(self.groupmapes_[station] if station in self.groupmapes_ else self.mfit.overallMean_) for station in X['station_id'] ]
        return np.asarray(values)

    def __init__(self, features=[]):
        self.mfit = MeansFit(features)


def doAnalysis2(cityBej = True):
    "Perform full analysis on the specified city"
    cityName = 'Beijing' if cityBej else "London"
    # Air data
    bejDf = allDf[(cityName, 'air')]
    bejDf['time'] = pd.to_datetime(bejDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    bejDf['test_id'] = "None"

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

    bejDfCols = list(bejDf)
    for col in bejDfCols:
        if col not in list(submissionDf):
            submissionDf[col] = bejDf.iloc[0][col]
    # We need ids to debug duplicate rows
    idStart = np.max(bejDf['id']) + 1
    for index, row in submissionDf.iterrows():
        submissionDf.at[index, 'id'] = idStart
        idStart += 1

    submissionCount = len(submissionDf)

    # Merge the two together for feature engineering part. We will separate them out later on
    bejDf = pd.concat([bejDf, submissionDf])
    submissionDf = None

    stationsNeeded = np.unique(bejDf['station_id'])

    weatherDf = load_weather.getWeatherDataRange(startDate, endDate, stationsNeeded, cityName, False)
    weatherDf['time'] = weatherDf['datetime']
    assert(len(weatherDf[weatherDf[['station_id', 'time']].duplicated()]) == 0)

    # We are okay with the inner join because of the assert statement immediately afterwards.
    # What we are saying here is that if the weather data is not available for a certain station at a certain time, then we will not do this analysis at all
    prev = len(bejDf)
    newBejDf = bejDf.merge(weatherDf, how='inner', on=['station_id', 'time']) # Created newBejDf to help with debugging
    assert(len(newBejDf) == prev) # We have weather data corresponding to all of the input data
    bejDf = newBejDf
    newBejDf = None
    assert(len(bejDf[bejDf['test_id'] != "None"]) == submissionCount) # We did not lose a single line for submission file

    bejDf.drop(labels='id', axis=1, inplace=True)
    bejDf.drop(labels='datetime', axis=1, inplace=True)
    bejDf.drop(labels='lat', axis=1, inplace=True)
    bejDf.drop(labels='long', axis=1, inplace=True)
    
    # ToDo: Undo. Removed because they have a lot of empty cells. Replace with more meaningful values
    bejDf.drop(labels='ozone', axis=1, inplace=True)
    bejDf.drop(labels='precipIntensity', axis=1, inplace=True)
    bejDf.drop(labels='precipProbability', axis=1, inplace=True)
    bejDf.drop(labels='pressure', axis=1, inplace=True)
    bejDf.drop(labels='uvIndex', axis=1, inplace=True)
    bejDf.drop(labels='windGust', axis=1, inplace=True)
    bejDf.drop(labels='cloudCover', axis=1, inplace=True)
    bejDf.drop(labels='precipType', axis=1, inplace=True)
    bejDf.drop(labels='visibility', axis=1, inplace=True)

    # Make categorical columns for for time based attributes
    bejDf['hour'] = bejDf['time'].dt.hour
    bejDf['day'] = bejDf['time'].dt.day
    bejDf['month'] = bejDf['time'].dt.month
    bejDf['dayofweek'] = bejDf['time'].dt.dayofweek
    bejDf['hour'] = bejDf['hour'].apply(lambda x:'hour'+str(x))
    bejDf['hour'] = bejDf['hour'].astype('category')
    bejDf['day'] = bejDf['day'].apply(lambda x:'day'+str(x))
    bejDf['day'] = bejDf['day'].astype('category')
    bejDf['month'] = bejDf['month'].apply(lambda x:'month'+str(x))
    bejDf['month'] = bejDf['month'].astype('category')
    bejDf['dayofweek'] = bejDf['dayofweek'].apply(lambda x:'dayofweek'+str(x))
    bejDf['dayofweek'] = bejDf['dayofweek'].astype('category')

    # Extra column for a median model
    bejDf['hour2'] = bejDf['time'].dt.hour

    # Business Hours Variable (between 8am and 6pm).
    #bejDf['businessHours'] = 0
    #bejDf.loc[(bejDf['hour'] >= 8) & (bejDf['hour']<=18)==0, 'businessHours'] = 1

    # Drop the pollution columns that we do not need
    if not cityBej:
        bejDf.drop(labels='CO_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='O3_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='SO2_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='NO2_Concentration', axis=1, inplace=True)
    else:
        bejDf.drop(labels='NO2_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='CO_Concentration', axis=1, inplace=True)
        bejDf.drop(labels='SO2_Concentration', axis=1, inplace=True)

    # Do not include negative values in the target columns
    negTargetColumns = ['PM25_Concentration', 'PM10_Concentration', 'O3_Concentration']
    for col in negTargetColumns:
        if col in set(bejDf):
            bejDf.loc[bejDf[col]<0, col] =np.NaN

    # ToDo: Come up with a strategy for handling na values
    bejDf.dropna(inplace=True)
    assert(len(bejDf[bejDf['test_id'] != "None"]) == submissionCount) # We did not lose a single line of submission file
    prev = len(bejDf)

    bejDf['summary'] = bejDf['summary'].astype('category')
    bejDf['icon'] = bejDf['icon'].astype('category')

    # Handle categorical data
    # ToDo: Use dummy_na argument of get_dummies and move this method before drop_na
    test_id = bejDf['test_id']
    station_id = bejDf['station_id'] # Keeping this alive for means prediction
    bejDf.drop(labels='test_id', axis=1, inplace=True)
    bejDf = pd.get_dummies(bejDf, prefix='dum', drop_first=True)
    bejDf['test_id'] = test_id
    bejDf['station_id'] = station_id

    # What predictions do we get without direct time component?
    bejDf.drop(labels='time', axis=1, inplace=True)
    assert(len(bejDf[bejDf['test_id'] != "None"]) == submissionCount) # We did not lose a single line of submission file

    targets = ['PM25_Concentration', 'PM10_Concentration', 'O3_Concentration']
    if not cityBej:
        targets = ['PM25_Concentration', 'PM10_Concentration']
    features = [col for col in list(bejDf) if (col not in targets)]
    features.remove('test_id')
    features.remove('station_id')
    features.remove('hour2')

    #for target in targets:
    #    bejDf[target].hist()
    #    plt.show()
    #    #print(target, np.min(bejDf[target]), np.max(bejDf[target]))

    assert((set(bejDf) - set(targets) - set(features)) == {'test_id', 'station_id', 'hour2'})
    assert(len(bejDf[bejDf['test_id'] != "None"]) == submissionCount) # We did not lose a single line of submission file

    # Now, just before we begin modeling, we seperate out the supplied data
    bejDf.reset_index(drop=True)
    df = bejDf[bejDf['test_id'] == 'None']

    algoName = None

    for target in targets:
        # K-Fold cross validation
        #shuf = False
        #if target == 'O3_Concentration':
        #    shuf = True
        shuf = True
        kf = sklearn.model_selection.KFold(n_splits=5, shuffle=shuf, random_state=42)
        modelScores = []
        for train_index, test_index in kf.split(df):
            if algoToUse == 'Means':
                lm = MeansFit(features)
            elif algoToUse == 'Smape':
                lm = SmapeFit(features)
            elif algoToUse == 'RandomForest':
                lm = sklearn.ensemble.RandomForestRegressor(n_jobs=-1, random_state=42, criterion='mse')
            elif algoToUse == 'Median':
                lm = MediansFit(features)
            elif algoToUse == 'LassoStationFit':
                lm = LassoStationFit(features)
            elif algoToUse == 'MeanMedianEnsamble':
                lm = MeanMedianEnsamble(features)
            elif algoToUse == 'StationHourMedian':
                lm = StationHourMedian(features)
            algoName = algoToUse

            X_train, X_test = df.iloc[train_index][features], df.iloc[test_index][features]
            Y_train, Y_test = df.iloc[train_index][[target]], df.iloc[test_index][[target]]

            lm.fit(X_train, Y_train.values.ravel())
            Y_predicted = np.abs(lm.predict(X_test))
            #Y_predicted = lm.predict(X_test)
            #score = sklearn.metrics.r2_score(Y_test, Y_predicted)
            score = smape(Y_test, Y_predicted)
            modelScores.append((score, lm))
        if shuf:
            modelScores.sort()
            modelUsed = modelScores[0][1]
            scoreUsed = modelScores[0][0]
        else:
            modelUsed = modelScores[-1][1] # Pick the model that predicted the last set of values
            scoreUsed = modelScores[-1][0]
        print(target, [val[0] for val in modelScores], scoreUsed)
        f.write(cityName + " " + target + " " + algoName + " " + str(datetime.datetime.utcnow()) + " " + str([val[0] for val in modelScores]) + " " + str(scoreUsed) + '\n')
        
        # Use the best model for making predictions
        bejDf.loc[bejDf['test_id'] != 'None', target] = np.abs(modelUsed.predict(bejDf.loc[bejDf['test_id'] != 'None', features]))
        if 'hour2' in features:
            features.remove('hour2')
    retainColumns = ['test_id']
    retainColumns += targets
    for col in list(bejDf):
        if col in retainColumns:
            continue
        bejDf.drop(labels=col, axis=1, inplace=True)
    renameDict = {'PM25_Concentration':'PM2.5', 'PM10_Concentration':'PM10', 'O3_Concentration':'O3'}
    for key in renameDict:
        bejDf.rename(columns={key:renameDict[key]}, inplace=True)

    submissionDf = bejDf[bejDf['test_id'] != 'None']
    # Final checks
    if cityBej:
        assert(len(submissionDf) == 1680)
        assert(len(list(submissionDf)) == 4)
    else:
        assert(len(submissionDf) == 624)
        assert(len(list(submissionDf)) == 3)

    return submissionDf, algoName


bejSubDf, algoName = doAnalysis2(cityBej=True)
lonSubDf, algoName = doAnalysis2(cityBej=False)

combDf = pd.concat([bejSubDf, lonSubDf])
dt = datetime.datetime.utcnow()
filename = algoName + "_" + str(dt.date().day) + "_" + str(dt.date().month) + "_" + str(dt.date().year) + "_" + str(dt.time().hour) + "_" + str(dt.time().minute) + "_" + str(dt.time().second) + ".csv"
filename = os.path.join("Submissions", filename)

#combDf.to_csv(filename, index=False, sep=',', columns=['test_id', 'PM2.5', 'PM10', 'O3'])
#submit_preds.submit_preds(filename, 'yashbhandari', algoName, filename=filename)

f.close()