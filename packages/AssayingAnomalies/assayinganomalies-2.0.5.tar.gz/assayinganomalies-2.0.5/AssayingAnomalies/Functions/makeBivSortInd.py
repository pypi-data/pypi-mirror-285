import numpy as np
import pandas as pd
from AssayingAnomalies.Functions.makeUnivSortInd import makeUnivSortInd


def makeBivSortInd(var1, ptfNumThresh1, var2, ptfNumThresh2, sort_type='unconditional', breaksFilterInd=None,
                   portfolioMassInd=None):
    """
    Creates a portfolio index matrix for a bivariate sort indicating which portfolio each stock-month belongs to.
    --------------------------------------------------------------------------------------------------------------------
    Required Inputs:
        var1 : numpy.ndarray or pd.DataFrame
            Matrix with first variable used for sorting.
        ptfNumThresh1 : int or numpy.ndarray
            Scalar or vector used to determine the number of portfolios in the first direction.
        var2 : numpy.ndarray or pd.DataFrame
            Matrix with second variable used for sorting.
        ptfNumThresh2 : int or numpy.ndarray
            Scalar or vector used to determine the number of portfolios in the second direction.
    --------------------------------------------------------------------------------------------------------------------
    Optional Inputs:
        sort_type : str, default 'unconditional'
            String indicating whether bivariate sort is 'unconditional' or 'conditional'.
        breaksFilterInd : numpy.ndarray or pd.DataFrame, default None
            Optional matrix used to filter portfolio breakpoints.
        portfolioMassInd : numpy.ndarray or pd.DataFrame, default None
            Optional matrix used for portfolio mass indicators.
    --------------------------------------------------------------------------------------------------------------------
    Returns:
        ind : numpy.ndarray
            A matrix that indicates the portfolio each stock-month falls under.
    --------------------------------------------------------------------------------------------------------------------
    Examples:
        # 5x5 unconditional sort on size and momentum
        ind = makeBivSortInd(me, 5, R, 5)

        # 2x3 (FF-style tertiles) unconditional sort on size and momentum
        ind = makeBivSortInd(me, 2, R, [30, 70])

        # 5x5 conditional sort on size and momentum
        ind = makeBivSortInd(me, 5, R, 5, sort_type='conditional')

        # 5x5 unconditional sort on size and momentum with breaksFilterInd
        ind = makeBivSortInd(me, 5, R, 5, breaksFilterInd=breaksFilterInd)

        # 5x5 unconditional sort on size and momentum with portfolioMassInd
        ind = makeBivSortInd(me, 5, R, 5, portfolioMassInd=portfolioMassInd)

        # 5x5 conditional sort on size and momentum with breaksFilterInd
        ind = makeBivSortInd(me, 5, R, 5, sort_type='conditional', breaksFilterInd=NYSE)
    --------------------------------------------------------------------------------------------------------------------
    """
    # Validate inputs
    if not (isinstance(var1, pd.DataFrame) or isinstance(var1, np.ndarray)):
        raise ValueError("Input 'var1' must be a DataFrame or a NumPy array.")

    if not (isinstance(var2, pd.DataFrame) or isinstance(var2, np.ndarray)):
        raise ValueError("Input 'var2' must be a DataFrame or a NumPy array.")

    # Convert input DataFrames to Numpy arrays
    if isinstance(var1, pd.DataFrame):
        var1 = var1.values

    if isinstance(var2, pd.DataFrame):
        var2 = var2.values

    if not np.isscalar(ptfNumThresh1) and not isinstance(ptfNumThresh1, (np.ndarray, list)):
        raise ValueError("Input 'ptfNumThresh1' must be a scalar, list, or a NumPy array.")

    if not np.isscalar(ptfNumThresh2) and not isinstance(ptfNumThresh2, (np.ndarray, list)):
        raise ValueError("Input 'ptfNumThresh2' must be a scalar, list, or a NumPy array.")

    if sort_type not in ['unconditional', 'conditional']:
        raise ValueError("sortType must be either 'unconditional' or 'conditional'.")

    if breaksFilterInd is not None:
        if not (isinstance(breaksFilterInd, pd.DataFrame) or isinstance(breaksFilterInd, np.ndarray)):
            raise ValueError("Input 'breaksFilterInd' must be a DataFrame, a NumPy array, or None.")
        if var1.shape != breaksFilterInd.shape or var2.shape != breaksFilterInd.shape:
            raise ValueError("Input 'breaksFilterInd' must have the same shape as 'var1 and 'var2'.")

    if portfolioMassInd is not None:
        if not (isinstance(portfolioMassInd, pd.DataFrame) or isinstance(portfolioMassInd, np.ndarray)):
            raise ValueError("Input 'portfolioMassInd' must be a DataFrame, a NumPy array, or None.")
        if var1.shape != portfolioMassInd.shape or var2.shape != portfolioMassInd.shape:
            raise ValueError("Input 'portfolioMassInd' must have the same shape as 'var1' and 'var2'.")

    # If user passed a list instead of numpy array for ptfNumThresh, we will need to change it to numpy array
    if isinstance(ptfNumThresh1, list):
        ptfNumThresh1 = np.array(ptfNumThresh1)
    if isinstance(ptfNumThresh2, list):
        ptfNumThresh2 = np.array(ptfNumThresh2)

    ind = np.zeros(var1.shape)

    # Sort based on the first variable
    ind1 = makeUnivSortInd(var1, ptfNumThresh1, breaksFilterInd=breaksFilterInd, portfolioMassInd=portfolioMassInd)

    # Store the number of portfolios
    n1 = int(np.nanmax(ind1))

    # Check the double sort type
    if sort_type == 'unconditional':
        # If unconditional
        # Sort based on the second variable
        ind2 = makeUnivSortInd(var2, ptfNumThresh2, breaksFilterInd=breaksFilterInd, portfolioMassInd=portfolioMassInd)

        # Store the number of portfolios
        n2 = int(np.nanmax(ind2))

        # Create the combined n1 x n2 portfolios
        for i in range(1, n1 + 1):
            for j in range(1, n2 + 1):
                ind[(ind1 == i) & (ind2 == j)] = (i - 1) * n2 + j  # Give it a number, in the end, all will be from 1 to n1 * n2
    else:
        # If conditional
        for i in range(1, n1 + 1):
            # Sort within each of the portfolios sorted based on the first variable
            temp = var2.copy()
            temp[ind1 != i] = np.nan
            temp_ind = makeUnivSortInd(temp, ptfNumThresh2, breaksFilterInd=breaksFilterInd,
                                       portfolioMassInd=portfolioMassInd)
            n2 = np.nanmax(temp_ind)
            ind[(ind1 == i) & (temp_ind > 0)] = temp_ind[(ind1 == i) & (temp_ind > 0)] + n2 * (i - 1)

    return ind


# Test the function
# import scipy.io
# import os
#
# path = r"C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\AssayingAnomalies-main\AssayingAnomalies-main\Data" + os.sep
# R = scipy.io.loadmat(path + 'R.mat')['R']
# # R = pd.read_csv(path + 'R.csv', index_col=0)
# me = scipy.io.loadmat(path + 'me.mat')['me']
# NYSE = scipy.io.loadmat(path + 'NYSE.mat')['NYSE']
# test = makeBivSortInd(me, 5, R, 5)
# test = makeBivSortInd(me, 2, R, [30, 70])
# test = makeBivSortInd(me, 5, R, 5, sort_type='conditional')
