from .runUnivSort import runUnivSort
import pandas as pd
import numpy as np
import os


def makeIndustryReturns(params, FFind):
    """
    Calculate and return industry-level returns for individual stocks.

    This function takes configuration parameters and a DataFrame specifying
    industry classifications for stocks. It reads return, market equity (ME),
    and date data from specified paths in 'params'. The function then runs
    a universe sort (using 'runUnivSort') based on these inputs, and computes
    industry-level returns. These returns are then assigned to individual stocks
    within each industry.

    Parameters:
    params (Config object): A configuration object containing various parameters
                            and file paths needed for processing.
    FFind (DataFrame): A DataFrame specifying the industry classification for each stock.

    Returns:
    tuple: A tuple containing two elements:
           - iret (DataFrame): A DataFrame with industry-level returns.
           - ireta (DataFrame): A DataFrame with industry-level returns assigned to individual stocks.

    The index of both 'iret' and 'ireta' DataFrames is based on the dates from the 'ret' DataFrame.
    The columns of 'ireta' correspond to individual stocks.

    Note:
    - This function relies on 'runUnivSort' to compute industry-level returns.
    - Industry classifications in 'FFind' should start from 1 and not 0.
    """

    comp_path = params.compFolder + os.sep
    crsp_path = params.crspFolder + os.sep

    ret = pd.read_csv(crsp_path + 'ret.csv', index_col=0).astype(float)
    me = pd.read_csv(crsp_path + 'me.csv', index_col=0).astype(float)
    dates = pd.read_csv(crsp_path + 'dates.csv', index_col=0).astype(float)

    res = runUnivSort(params, ret, FFind, me, dates, factorModel=1, addLongShort=0, printResults=1, plotFigure=0)

    iret = res['pret']
    nInds = iret.shape[1]
    nStocks = len(ret.columns)

    # Initialize ireta with NaNs
    ireta = pd.DataFrame(np.nan, index=ret.index, columns=ret.columns)

    # Assign industry returns to individual stocks
    for i in range(nInds):
        # Replicate industry returns across all stocks for the current industry
        rptdIret = pd.DataFrame(np.tile(iret[:, i], (len(ret.columns), 1)).T, index=ret.index, columns=ret.columns)

        # Apply the replicated returns to stocks belonging to the current industry
        industry_mask = (FFind == (i + 1))  # Adjusted for zero-based indexing in Python
        ireta[industry_mask] = rptdIret[industry_mask]

    return iret, ireta

