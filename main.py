import load_data


allDf = load_data.getPandasDataframes()
for key, value in allDf.items():
    print(key)
    print(value.head())

#ToDo: Figure out why we cannot see London met data
