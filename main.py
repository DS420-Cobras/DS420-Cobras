import load_data

def mainWorkflow():
    "This is the function for the main workflow"
    allDf = load_data.getPandasDataframes()
    for key, value in allDf.items():
        print(key)
        print(value.head())

if __name__ == '__main__':
    mainWorkflow()