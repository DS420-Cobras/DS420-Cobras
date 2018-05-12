#!/usr/bin/python

# Input dataframes format:

# id	station_id	time	PM25_Concentration	PM10_Concentration	NO2_Concentration	CO_Concentration	O3_Concentration	SO2_Concentration
# 2941450	dongsi_aq	2018-03-31 07:00:00	105.0	172.0	53.0	0.8	127.0	14.0
# 2941451	tiantan_aq	2018-03-31 07:00:00	95.0	123.0	54.0	0.9	121.0	15.0
# 2941452	guanyuan_aq	2018-03-31 07:00:00	95.0	139.0	66.0	0.8	123.0	13.0
#
#
# The function takes Beijing and London prediction dataframes and outputs a dataframe in the following format:
#  
# test_id	PM2.5	PM10	O3
# dongsi_aq#0	100	75	13
# dongsi_aq#1	102	87	2
# dongsi_aq#2	85	85	2
# dongsi_aq#3	88	82	2
# dongsi_aq#4	95	77	2
# dongsi_aq#5	95	59	13
# dongsi_aq#6	95	60	13
# dongsi_aq#7	103	84	2
# dongsi_aq#8	109	86	2
#
# test_id is station_id+'#'+hour
#
# The dataframe is saved as a csv, "submission.csv"
#




from datetime import datetime
import pandas as pd

def create_submission(BeijingDf, LondonDf):
	"Input two dataframes: Beijing and London air quality predictions"
	columns = ['station_id', 'time','PM25_Concentration', 'PM10_Concentration','O3_Concentration']
	combDf = pd.concat([BeijingDf[columns], LondonDf[columns]])
	combDf['hour'] = [datetime.strptime(combDf['time'].iloc[i], '%Y-%m-%d %H:%M:%S').hour for i in combDf.index]
	combDf['test_id'] = [str(df['station_id'].iloc[i]+'#'+str(df['hour'].iloc[i])) for i in df.index]
	combDf = combDf.drop(['station_id', 'time', 'hour'], axis=1)
	combDf = combDf[['test_id', 'PM25_Concentration', 'PM10_Concentration','O3_Concentration']]
	combDf = combDf.rename(index=str, columns={"PM25_Concentration": "PM2.5", "PM10_Concentration": "PM10", "O3_Concentration": "O3"})
	combDf.to_csv("submission_preds.csv", index=False, sep='\t')

