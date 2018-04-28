import load_data

def performBeijingAnalysis(allDf):
    "Analysis of Beijing dataframe"
    bejAirDf = allDf[('Beijing', 'air')]
    bejMetDf = allDf[('Beijing', 'met')]
    bejGrd = allDf[('Beijing', 'grid')]

def mainWorkflow():
    "This is the function for the main workflow"
    allDf = load_data.getPandasDataframes()
    for key, value in allDf.items():
        print(key)
        print(value.head())
    performBeijingAnalysis(allDf)

if __name__ == '__main__':
    mainWorkflow()

