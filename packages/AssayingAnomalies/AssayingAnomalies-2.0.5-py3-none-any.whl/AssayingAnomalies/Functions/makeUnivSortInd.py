import numpy as np
import pandas as pd
from AssayingAnomalies.Functions.check_and_clean_sort_variables import check_and_clean_sort_variables
from AssayingAnomalies.Functions.assign_to_portfolios import assign_to_portfolios


def makeUnivSortInd(var, ptfNumThresh, breaksFilterInd=None, portfolioMassInd=None) -> pd.DataFrame:
    # Validate inputs
    check_and_clean_sort_variables(var, ptfNumThresh, breaksFilterInd, portfolioMassInd)

    # Convert input DataFrame to Numpy array
    if isinstance(var, np.ndarray):
        var = pd.DataFrame(var)

    # Changing to Dataframe and then boolean
    if isinstance(breaksFilterInd, np.ndarray):
        breaksFilterInd = pd.DataFrame(breaksFilterInd, index=var.index, columns=var.columns)


    if isinstance(portfolioMassInd, np.ndarray):
        portfolioMassInd = pd.DataFrame(portfolioMassInd, index=var.index, columns=var.columns)

    # Assign firm-months to their corresponding portfolios
    ind = assign_to_portfolios(var, ptfNumThresh, breaksFilterInd, portfolioMassInd)
    return ind


# saveFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'
# me = pd.read_csv(saveFolder + 'me.csv', index_col=0).astype(float)
# NYSE = pd.read_csv(saveFolder + 'NYSE.csv', index_col=0)
# test_ind = makeUnivSortInd(-me, 10, breaksFilterInd=NYSE)
# test_ind = makeUnivSortInd(-me, [30, 70], breaksFilterInd=NYSE)
