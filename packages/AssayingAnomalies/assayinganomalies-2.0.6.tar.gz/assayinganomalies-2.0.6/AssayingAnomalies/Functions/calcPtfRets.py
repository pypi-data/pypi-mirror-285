import numpy as np
import pandas as pd


def calcPtfRets(ret, ind, mcap, hper, weighting):
    """
    Purpose: Calculates portfolio returns, number of stocks, and market capitalizations for each portfolio indicated
            by 'ind'
    -----------------------------------------------------------------------------------------------------------------------
    Usage:
    -----------------------------------------------------------------------------------------------------------------------
    Inputs:
        -ret - a matrix of stock returns
        -ind - a matrix of portfolio index
        -mcap - a matrix of market capitalization numbers
        -hper - ascalar indicating the ptf holding period
        weighting - weighting scheme (one of {'V', 'v', 'E', 'e'})
    Outputs:
        -pret - matrix of raw value-weighted portfolio returns
        -ptfNumStocks - matrix of number of firms in each portfolio
        -ptfMarketCap - matrix of total market capitalization of each portfolio
    -----------------------------------------------------------------------------------------------------------------------
    Examples:
    ptfRet, ptfNumStocks, ptfMarketCap = calcPtfRets(ret, ind, me, 1, 'e') # Equal-weighted returns with 1-month holding
                                                                            period.
    -----------------------------------------------------------------------------------------------------------------------
    Dependencies:
        -makeUniverses()
    -----------------------------------------------------------------------------------------------------------------------
    References:
        1. Novy-Marx, R. and M. Velikov, 2023, Assaying anomalies, Working paper.
    """

    # if isinstance(mcap, pd.DataFrame):
    #     mcap = mcap.to_numpy()
    #
    # if isinstance(ind, pd.DataFrame):
    #     ind = ind.to_numpy()

    # create lagged dataframes
    lme = np.roll(mcap, 1, axis=0)
    lind = np.roll(ind, 1, axis=0)
    # the code above takes whatever was in the last row and moves it to the first, which we must now correct.
    lme[0] = np.nan
    lind[0] = 0

    # trying it with numpy slicing
    # lme = mcap[1:, :]
    # lind = ind[1:, :]

    # Check weighting scheme
    if weighting == 'e' or weighting=='E':
        weightingMcap = np.ones_like(mcap)
    else:
        weightingMcap = lme

    # store a couple of variables
    nPtfs = np.max(np.max(ind)).astype(int)
    nMonths, nStocks = ret.shape

    def mode(arr):
        # count the frequency of each unique value in the array
        values, counts = np.unique(arr, return_counts=True)
        # locate the index of the most frequent value(s)
        index = np.nanargmax(counts)
        # return the most frequent value(s)
        return values[index] if counts[index] > 1 else None

    # Carry over the index in case we are not rebalancing every month
    nNonZero = np.sum(lind > 0, axis=1) # counts the number of stocks that are in at least one portfolio for each month
    indReb = np.where(nNonZero)[0] # find the column indices of the
    rebFreq = mode(indReb - np.roll(indReb, 1, axis=0))
    startMonth = np.where(nNonZero > 0)[0][0] + 1
    endMonth = min(np.where(nNonZero > 0)[0][-1] + rebFreq, nMonths)

    for i in range(startMonth, endMonth):
        if nNonZero[i] == 0:
            lind[i, :] = lind[i - 1, :]

    # Initialize the output matrices
    ptfNumStocks = np.zeros((nMonths, nPtfs))
    ptfMarketCap = np.zeros((nMonths, nPtfs))
    ptfRet = np.zeros((nMonths, nPtfs))

    # Loop over the portfolios
    for i in range(nPtfs):
        ptfInd = (lind == i+1).astype(float)
        # ptfInd = (lind == 1)

        if hper > 1:
            for h in range(1, hper):
                ptfInd = ptfInd.astype(bool) | (lind[max(0, i-h), :] == i)

        # Make sure we are only using stock-months with available lagged market cap & return observations
        # ptfInd = 1*(ptfInd & np.isfinite(lme) & np.isfinite(ret))
        ptfInd = ptfInd.astype(bool) & np.isfinite(lme) & np.isfinite(ret)
        ptfInd = ptfInd.astype(float)
        ptfInd[ptfInd == 0] = np.nan

        # Calculate the number of stocks in the portfolio in each month
        # print(np.nansum(ptfInd, axis=1))
        ptfNumStocks[:, i] = np.nansum(ptfInd, axis=1)

        # Calculate the portfolios market cap in each month and then
        sumWghtMcap = np.nansum(weightingMcap*ptfInd, axis=1)
        ptfMarketCap[:, i] = sumWghtMcap # stores the portfolios market cap for each month
        sumWghtMcap = np.tile(sumWghtMcap, (nStocks, 1)).T # repeats the above column to form an dates x nStocks array

        # Calculate and stores the portfolio return
        ptfRet[:, i] = np.nansum(ptfInd*ret*weightingMcap / sumWghtMcap, axis=1)

    return ptfRet, ptfNumStocks, ptfMarketCap

