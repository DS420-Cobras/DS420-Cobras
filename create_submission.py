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
from datetime import datetime
import pandas as pd

def create_submission(BeijingDf, LondonDf):
	"Input two dataframes: Beijing and London air quality predictions"
	columns = ['station_id', 'time','PM25_Concentration', 'PM10_Concentration','O3_Concentration']
	combDf = pd.concat([bj_air[columns], ld_air[columns]])
	combDf['hour'] = [datetime.strptime(combDf['time'].iloc[i], '%Y-%m-%d %H:%M:%S').hour for i in combDf.index]
	combDf['test_id'] = [str(df['station_id'].iloc[i]+'#'+str(df['hour'].iloc[i])) for i in df.index]
	combDf = combDf.drop(['station_id', 'time', 'hour'], axis=1)
	combDf = combDf[['test_id', 'PM25_Concentration', 'PM10_Concentration','O3_Concentration']]
	combDf = combDf.rename(index=str, columns={"PM25_Concentration": "PM2.5", "PM10_Concentration": "PM10", "O3_Concentration": "O3"})
	combDf