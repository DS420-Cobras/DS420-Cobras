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

def doAnalysis(cityBej=True):
    "Name of the city for which we are doing analysis"
    cityName = 'Beijing' if cityBej else "London"

    # Met data
    if cityBej:
        bejMetDf = allDf[(cityName, 'met')]
        bejMetDf['time'] = pd.to_datetime(bejMetDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
        bejMetDf = bejMetDf.rename(columns={'station_id':'met_station'})

    # Grid data
    bejGrd = allDf[(cityName, 'grid')]
    bejGrd['time'] = pd.to_datetime(bejGrd['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    bejGrd = bejGrd.rename(columns={'station_id':'met_station'})

    # Air data
    bejDf = allDf[(cityName, 'air')]

    if not cityBej:
        bejDf.drop(labels=['CO_Concentration', 'O3_Concentration', 'SO2_Concentration'], axis=1, inplace=True)

    # Time related feature engineering
    bejDf['time'] = pd.to_datetime(bejDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    bejDf['hour'] = bejDf['time'].dt.hour
    bejDf['day'] = bejDf['time'].dt.day
    bejDf['month'] = bejDf['time'].dt.month
    bejDf['dayofweek'] = bejDf['time'].dt.dayofweek

    bejDf.drop(labels='id', axis=1, inplace=True)

    # Business Hours Variable (between 8am and 6pm)
    bejDf['businessHours'] = 0
    bejDf.loc[(bejDf['hour'] >= 8) & (bejDf['hour']<=18)==0, 'businessHours'] = 1

    # import geospatial data
    bj_grid_stations = pd.read_csv('viz/' + cityName +'_points.csv')
    bj_nn = pd.read_excel('viz/' + cityName + '_Neighbors.xlsx')
    bj_nn = bj_nn.rename(columns={"aq_station": "station_id"})

    # Join the data
    bejDf = bejDf.merge(bj_nn, on='station_id', how='left')
    if cityBej:
        bejWeather = pd.concat([bejMetDf, bejGrd])
    else:
        bejWeather = pd.concat([bejGrd])
    bejDf = pd.merge(bejDf, bejWeather,  how='left', on=['met_station','time'])

    # Drop columns not useful in analysis
    bejDf.drop(labels='id', axis=1, inplace=True)

    # Clean some duplicate categorical variables from weather
    bejDf['weather'].replace('Cloudy','CLOUDY', inplace=True)
    bejDf['weather'].replace('Sunny/clear','CLEAR_DAY', inplace=True)
    bejDf['weather'].replace('Rain','RAIN', inplace=True)
    bejDf['weather'] = bejDf['weather'].astype('category')

    # Create categorical columns from string columns
    bejDf['met_station'] = bejDf['met_station'].astype('category')
    bejDf['station_id'] = bejDf['station_id'].astype('category')

    # Replace some outliers with median values
    bejDf.loc[bejDf['humidity']== 999999, 'humidity'] = bejDf['humidity'].median()
    bejDf.loc[bejDf['pressure']== 999999, 'pressure'] = bejDf['pressure'].median()
    bejDf.loc[bejDf['temperature']== 999999, 'temperature'] = bejDf['temperature'].median()

    # coordinates from weather stations
    bejDf = pd.merge(bejDf, bj_grid_stations, how='left', on = 'station_id')

    # remove the NANs. not ideal
    bejDf.drop(['latitude','longitude'], axis=1, inplace=True)
    bejDf.dropna(inplace=True)

    # Normalize the columns
    scalarCols = [col for col in bejDf.columns if bejDf[col].dtype == np.number]
    scaler = sklearn.preprocessing.MinMaxScaler(copy = True)
    bejDf[scalarCols] = scaler.fit_transform(bejDf[scalarCols])

    # Handle categorical data
    bejDf = pd.get_dummies(bejDf, 'dum')

    # Create test and training set
    ct = datetime.datetime.utcnow() - datetime.timedelta(hours=48)
    splitDate = pd.datetime(ct.year,ct.month,ct.day,  ct.hour)
    trainDf = bejDf[bejDf['time'] < splitDate]
    testDf = bejDf[bejDf['time'] >= splitDate]

    cur = datetime.datetime.utcnow()
    current_time = pd.datetime(cur.year,cur.month,cur.day,cur.hour)
    d = list(testDf.time)
    date_list = [current_time - datetime.timedelta(hours=x) for x in range(0, 48)]
    date_list = [pd.to_datetime(i, format='%Y-%m-%d %H:%M:%S') for i in date_list]
    missingDatesFromTestDf = np.setdiff1d(sorted(date_list),list(set(sorted(d))))
    print(list(missingDatesFromTestDf))

    # No use of time anymore
    bejDf.drop(labels='time', axis=1, inplace=True)
    #print("Training:", np.unique([str(bejDf[col].dtype) for col in list(bejDf)]))

    if cityBej:
        targets = ['PM25_Concentration', 'PM10_Concentration', 'O3_Concentration']
    else:
        targets = ['PM25_Concentration', 'PM10_Concentration']
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


    if False:
        plt.scatter(x=bejDf.PM25_Concentration, y=bejDf.PM10_Concentration)
        plt.xlabel("time", fontsize=14)
        plt.ylabel("PM10_Concentration", fontsize=14)
        f = plt.gcf()
        f.set_figheight(10)
        f.set_figwidth(15)
        plt.show()

doAnalysis(cityBej=True)
#doAnalysis(cityBej=False)