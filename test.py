import unittest
import load_data

class Test_test(unittest.TestCase):
    def test_GetPandasDataframes(self):
        allDf = load_data.getPandasDataframes()

        # Check if we got all of the data frames
        expectedKeys = [('Beijing', 'air'), ('Beijing', 'met'), ('Beijing', 'grid'), ('London', 'air'), ('London', 'met'), ('London', 'grid')]
        actualKeys = [key for key in allDf.keys()]
        self.assertEqual(expectedKeys, actualKeys)
        #print(allDf.keys())

        # Check if we got the same columns for the data frames
        expectedColNames = {('Beijing', 'air'):['id', 'station_id', 'time', 'PM25_Concentration', 'PM10_Concentration', 'NO2_Concentration', 'CO_Concentration', 'O3_Concentration', 'SO2_Concentration'],
                            ('Beijing', 'met'):['id', 'station_id', 'time', 'weather', 'temperature', 'pressure', 'humidity', 'wind_direction', 'wind_speed'],
                            ('Beijing', 'grid'):['id', 'station_id', 'time', 'weather', 'temperature', 'pressure', 'humidity', 'wind_direction', 'wind_speed'],
                            ('London', 'air'):['id', 'station_id', 'time', 'PM25_Concentration', 'PM10_Concentration', 'NO2_Concentration', 'CO_Concentration', 'O3_Concentration', 'SO2_Concentration'],
                            ('London', 'met'):['None'],
                            ('London', 'grid'):['id', 'station_id', 'time', 'weather', 'temperature', 'pressure', 'humidity', 'wind_direction', 'wind_speed']
}
        for (key,colNames) in expectedColNames.items():
            self.assertEqual(colNames, list(allDf[key]))
            #print(key, list(values))

        # Check if we downloaded enough columns
        expectedLengths = {('Beijing', 'air'):(16625, 9), ('Beijing', 'met'):(9117, 9), ('Beijing', 'grid'):(330677, 9), ('London', 'air'):(9728, 9),
('London', 'grid'):(436468, 9), ('London', 'met'):(0, 1)}
        for key, lengths in expectedLengths.items():
            self.assertLessEqual(lengths[0], allDf[key].shape[0])
            self.assertLessEqual(lengths[1], allDf[key].shape[1])

if __name__ == '__main__':
    unittest.main()
