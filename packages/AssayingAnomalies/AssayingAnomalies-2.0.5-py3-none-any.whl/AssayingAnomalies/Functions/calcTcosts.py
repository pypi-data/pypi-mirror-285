import numpy as np
import pandas as pd

#  #TODO:Note I am currently not allowing the user to request variable number of outputs - they will always receive three. I have also not implemented 'varargin' functionality.
def calcTcosts(tcosts, ind, me, weighting='v', ptfRets=None):
    # Validate inputs
    if not (isinstance(tcosts, np.ndarray) or isinstance(tcosts, pd.DataFrame)):
        raise ValueError("Input 'tcosts' must be a NumPy array or a DataFrame.")

    if not (isinstance(ind, np.ndarray) or isinstance(ind, pd.DataFrame)):
        raise ValueError("Input 'ind' must be a NumPy array or a DataFrame.")

    if not (isinstance(me, np.ndarray) or isinstance(me, pd.DataFrame)):
        raise ValueError("Input 'me' must be a NumPy array or a DataFrame.")

    # Convert DataFrames to NumPy arrays
    if isinstance(tcosts, pd.DataFrame):
        tcosts = tcosts.values

    if isinstance(ind, pd.DataFrame):
        ind = ind.values

    if isinstance(me, pd.DataFrame):
        me = me.values

    # Determine weights based on the 'weighting' input
    if isinstance(weighting, str):
        if weighting.lower() == 'v':
            w = me
        elif weighting.lower() == 'e':
            w = me / me
        else:
            raise ValueError(
                "Optional 'weighting' input should be one of 'v', 'V', 'e', 'E', or a user-defined matrix that has the same dimensions as the 'tcosts' matrix.")
    elif isinstance(weighting, np.ndarray) or isinstance(weighting, pd.DataFrame):
        if weighting.shape == me.shape:
            if isinstance(weighting, pd.DataFrame):
                w = weighting.values
            else:
                w = weighting
        else:
            raise ValueError(
                "Optional 'weighting' input should be one of 'v', 'V', 'e', 'E', or a user-defined matrix that has the same dimensions as the 'tcosts' matrix.")
    else:
        raise ValueError(
            "Optional 'weighting' input should be one of 'v', 'V', 'e', 'E', or a user-defined matrix that has the same dimensions as the 'tcosts' matrix.")

    # Store a few constants
    nMonths, nStocks = tcosts.shape
    nPtfs = int(np.nanmax(ind))

    # Initiate the trading costs, turnover, and change in weight matrices
    ptfTC = np.full((nMonths, nPtfs), np.nan)
    ptfTO = np.full((nMonths, nPtfs), np.nan)
    dWs = np.full((nMonths, nStocks, nPtfs), np.nan)

    # Take all the rebalancing months
    indRebMonths = np.where(np.sum(ind > 0, axis=1) > 0)[0]

    # Figure out the rebalancing frequency
    rebFrequencies = np.diff(indRebMonths, prepend=np.nan)
    rebFrequencies = rebFrequencies[~np.isnan(rebFrequencies)]
    rebFreq = np.argmax(np.bincount(rebFrequencies.astype(int)))

    # Store the increase in market capitalization. This is a shortcut to
    # calculating the gross ex-dividend return
    gretxd = me / np.roll(me, rebFreq, axis=0)
    gretxd[:rebFreq] = np.nan

    # Loop over the portfolios
    for i in range(nPtfs):

        # Initialize the weights for this portfolio
        thisPtfW = np.zeros(ind.shape)

        # Assign the weights from the w matrix
        thisPtfW[ind == (i + 1)] = w[ind == (i + 1)]

        # Calculate the sum of the weights & turn into a matrix
        sumThisPtfW = np.nansum(thisPtfW, axis=1)
        sumThisPtfWMat = np.repeat(sumThisPtfW[:, np.newaxis], nStocks, axis=1)

        # Calculate the weights on the way out
        wOut = thisPtfW / sumThisPtfWMat

        # Lag the outweights by the rebalancing frequency
        lagWOut = np.roll(wOut, rebFreq, axis=0)
        lagWOut[:rebFreq] = 0

        # Allow for increasing the base of the strategy to (1+r). This requires
        # the user to have passed on ptfRets with the correct dimensions
        if ptfRets.shape == (nMonths, nPtfs):
            wOut = wOut * (1 + np.repeat(ptfRets[:, i][:, np.newaxis], nStocks, axis=1))

        # Calculate the weights on the way in: last month's weight times the
        # current month return ex-dividends
        wIn = lagWOut * gretxd

        # Store the change in weights
        dWs[:, :, i] = wOut - wIn

        # Store the turnover and trading costs
        ptfTO[:, i] = np.nansum(np.abs(dWs[:, :, i]), axis=1)
        ptfTC[:, i] = np.nansum(np.abs(dWs[:, :, i] * tcosts), axis=1)

        # Calculate the net dW (dW(Long) - dW(Short))
    dW = dWs[:, :, -1] - dWs[:, :, 0]

    return ptfTC, ptfTO, dW
