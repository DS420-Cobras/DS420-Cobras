import load_data
import pandas as pd
import numpy as np
import submit_preds

allDf = load_data.getPandasDataframes()

bejAirDf = allDf[('Beijing', 'air')]
#bejMetDf = allDf[('Beijing', 'met')]
#bejGrd = allDf[('Beijing', 'grid')]

lonAirDf = allDf[('London', 'air')]

#bejAirDf['newTime'] = pd.to_datetime(bejAirDf['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')

bej25 = bejAirDf['PM25_Concentration'].mean()
bej10 = bejAirDf['PM10_Concentration'].mean()
bejO3 = bejAirDf['O3_Concentration'].mean()

lon25 = lonAirDf['PM25_Concentration'].mean()
lon10 = lonAirDf['PM10_Concentration'].mean()

stationlist = ['dongsi_aq', 'tiantan_aq', 'guanyuan_aq', 'wanshouxigong_aq', 'aotizhongxin_aq', 'nongzhanguan_aq', 'wanliu_aq', 'beibuxinqu_aq', 'zhiwuyuan_aq', 'fengtaihuayuan_aq', 'yungang_aq', 'gucheng_aq', 'fangshan_aq',
               'daxing_aq', 'yizhuang_aq', 'tongzhou_aq', 'shunyi_aq', 'pingchang_aq', 'mentougou_aq', 'pinggu_aq', 'huairou_aq', 'miyun_aq', 'yanqin_aq', 'dingling_aq', 'badaling_aq', 'miyunshuiku_aq',
               'donggaocun_aq', 'yongledian_aq', 'yufa_aq', 'liulihe_aq', 'qianmen_aq', 'yongdingmennei_aq', 'xizhimenbei_aq', 'nansanhuan_aq', 'dongsihuan_aq']
stArr = [st + '#' + str(i) for st in stationlist for i in range(48)]
bejSubDf = pd.DataFrame({'test_id':stArr})
bejSubDf["PM2.5"] = bej25
bejSubDf["PM10"] = bej10
bejSubDf["O3"] = bejO3
#bejSubDf.to_csv('bej.csv', index=False)

stationlist = ['CD1', 'BL0', 'GR4', 'MY7', 'HV1', 'GN3', 'GR9', 'LW2', 'GN0', 'KF1', 'CD9','ST5', 'TH4']
stArr = [st + '#' + str(i) for st in stationlist for i in range(48)]
lonSubDf = pd.DataFrame({'test_id':stArr})
lonSubDf["PM2.5"] = lon25
lonSubDf["PM10"] = lon10
lonSubDf["O3"] = np.NaN
#lonSubDf.to_csv('lon.csv', index=False)

columns = ['test_id', 'PM2.5', 'PM10','O3']
combDf = pd.concat([bejSubDf[columns], lonSubDf[columns]])
combDf.to_csv("submission_preds.csv", index=False, sep=',')


submit_preds.submit_preds('submission_preds.csv', 'leosalemann', 'Sample means', filename='mean.csv')