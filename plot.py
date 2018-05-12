import matplotlib.pyplot as plt
import seaborn as sns
import math

def CreateMultiplePredictedAndActualValuesPlots(multipleFitValues, multipleActualValues, algoName):
    "Create multiple residual subplots for the fit values"
    assert(len(multipleFitValues) == len(multipleActualValues))
    l = len(multipleFitValues)
    numRows = math.ceil(math.sqrt(l))
    numCols = math.ceil(l/numRows)
    f, axes = plt.subplots(numRows, numCols)
    f.suptitle("Residuals vs. Actual values plots for "+algoName, fontsize=14)
    f.set_figheight(12)
    f.set_figwidth(16)
    count = 0
    if l == 1:
        axes = [[axes]]
    for axesRow in axes:
        for ax in axesRow:
            if count == l:
                break
            residuals = multipleFitValues[count]-multipleActualValues[count]
            sns.regplot(multipleActualValues[count], residuals, ax=ax, fit_reg=False, label='actual')
            sns.regplot(multipleFitValues[count], residuals, ax=ax, fit_reg=False, label='predicted')
            ax.set_xlabel('Target Variable')
            ax.set_ylabel('Residuals')
            ax.get_xaxis().set_ticks([])
            ax.legend()
            count = count + 1
            plt.gca().set_prop_cycle(None)
    plt.show()
