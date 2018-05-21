import load_data
import pandas as pd
import numpy as np
import submit_preds

allDf = load_data.getPandasDataframes()

bejAirDf = allDf[('Beijing', 'air')]
#bejMetDf = allDf[('Beijing', 'met')]
#bejGrd = allDf[('Beijing', 'grid')]

lonAirDf = allDf[('London', 'air')]

bejOverallMean = {'PM25_Concentration':bejAirDf['PM25_Concentration'].mean(), 'PM10_Concentration':bejAirDf['PM10_Concentration'].mean(), 'O3_Concentration':bejAirDf['O3_Concentration'].mean(),
                 'NO2_Concentration':bejAirDf['NO2_Concentration'].mean(), 'CO_Concentration':bejAirDf['CO_Concentration'].mean(), 'SO2_Concentration':bejAirDf['SO2_Concentration'].mean()}

lonOverAllMean = {'PM25_Concentration':lonAirDf['PM25_Concentration'].mean(), 'PM10_Concentration':lonAirDf['PM10_Concentration'].mean(), 'O3_Concentration':lonAirDf['O3_Concentration'].mean(),
                 'NO2_Concentration':lonAirDf['NO2_Concentration'].mean(), 'CO_Concentration':lonAirDf['CO_Concentration'].mean(), 'SO2_Concentration':lonAirDf['SO2_Concentration'].mean()}

bejMeans = bejMeans = {index:{i:bejOverallMean[i] if np.isnan(v) else v for i, v in row.items()} for index, row in bejAirDf.groupby(['station_id']).mean().iterrows()}
lonMeans = {index:{i:v for i, v in row.items()} for index, row in lonAirDf.groupby(['station_id']).mean().iterrows()}

stationlist = ['dongsi_aq', 'tiantan_aq', 'guanyuan_aq', 'wanshouxigong_aq', 'aotizhongxin_aq', 'nongzhanguan_aq', 'wanliu_aq', 'beibuxinqu_aq', 'zhiwuyuan_aq', 'fengtaihuayuan_aq', 'yungang_aq', 'gucheng_aq', 'fangshan_aq',
               'daxing_aq', 'yizhuang_aq', 'tongzhou_aq', 'shunyi_aq', 'pingchang_aq', 'mentougou_aq', 'pinggu_aq', 'huairou_aq', 'miyun_aq', 'yanqin_aq', 'dingling_aq', 'badaling_aq', 'miyunshuiku_aq',
               'donggaocun_aq', 'yongledian_aq', 'yufa_aq', 'liulihe_aq', 'qianmen_aq', 'yongdingmennei_aq', 'xizhimenbei_aq', 'nansanhuan_aq', 'dongsihuan_aq']
stArr = [st + '#' + str(i) for st in stationlist for i in range(48)]
bej25Arr = [bejMeans[st]['PM25_Concentration'] for st in stationlist for i in range(48)]
bej10Arr = [bejMeans[st]['PM10_Concentration'] for st in stationlist for i in range(48)]
bejO3Arr = [bejMeans[st]['O3_Concentration'] for st in stationlist for i in range(48)]
bejSubDf = pd.DataFrame({'test_id':stArr, "PM2.5":bej25Arr, 'PM10':bej10Arr, 'O3':bejO3Arr})

stationlist = ['CD1', 'BL0', 'GR4', 'MY7', 'HV1', 'GN3', 'GR9', 'LW2', 'GN0', 'KF1', 'CD9','ST5', 'TH4']
stArr = [st + '#' + str(i) for st in stationlist for i in range(48)]
lon25Arr = [lonMeans[st]['PM25_Concentration'] for st in stationlist for i in range(48)]
lon10Arr = [lonMeans[st]['PM10_Concentration'] for st in stationlist for i in range(48)]
lonSubDf = pd.DataFrame({'test_id':stArr, "PM2.5":lon25Arr, 'PM10':lon10Arr, 'O3':np.NaN})

columns = ['test_id', 'PM2.5', 'PM10','O3']
combDf = pd.concat([bejSubDf[columns], lonSubDf[columns]])
combDf.to_csv("submission_preds.csv", index=False, sep=',')


# submit_preds.submit_preds('submission_preds.csv', 'leosalemann', 'fastPred', filename='mean.csv')