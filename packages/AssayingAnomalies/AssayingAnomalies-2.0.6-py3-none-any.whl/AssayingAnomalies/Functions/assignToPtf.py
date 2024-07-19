import numpy as np


def assignToPtf(x, bPtsMat):
    """
    Function that assigns each firm-month to the bin it belongs to in the
    particular month. It assigns a zero if a firm-month is not held in any
    portfolio.

    Parameters
    ----------
    x : numpy array or pandas DataFrame
        Matrix based on which we want to assign the bins.
    bPtsMat : numpy array
        A matrix with the breakpoints (values) for each time period.
            e.g. np.nanpercentile(me, np.linspace(0, 100, 5), axis=1).T

    Returns
    -------
    ind : numpy array
        A matrix that indicates the bin each stock-time is in.
    """

    # Store several dimensions
    nStocks = x.shape[1]
    nPeriods = x.shape[0]
    nBPoints = bPtsMat.shape[1]

    # Create a matrix with the same dimensions as x
    ind = np.zeros((nPeriods, nStocks))

    # Assign the indicator for the first portfolio
    bPtsPtfOne = bPtsMat[:, 0]
    rptdBPtsPtfOne = np.repeat(bPtsPtfOne[:, np.newaxis], nStocks, axis=1)
    ind[x < rptdBPtsPtfOne] = 1

    # Repeat the same for all the other breakpoints
    for j in range(1, nBPoints + 1):
        bPtsPtfJ = bPtsMat[:, j - 1]
        rptdBPtsPtfJ = np.repeat(bPtsPtfJ[:, np.newaxis], nStocks, axis=1)
        ind[x >= rptdBPtsPtfJ] = j + 1

    return ind


# saveFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'
# me = pd.read_csv(saveFolder + 'me.csv', index_col=0).astype(float)
# test_bpts = np.nanpercentile(me, np.linspace(0, 100, 5), axis=1).T
# test_ind = assignToPtf(me, test_bpts)