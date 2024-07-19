import numpy as np
import pandas as pd

def makePastPerformance(returns, lag_start, lag_end):
    """
    PURPOSE: This function calculates cumulative returns for momentum variables.
    --------------------------------------
    :param returns: pandas DataFrame or numpy array
            - dates x permno monthly returns
    :param lag_start: int
            - how many periods ago does the lag start (including this month) ; e.g. lag_start = 12
    :param lag_end:
            - how many periods ago does the lag end (excluding this month); e.g. lag_end = 1
    ---------------------------------------
    :return: returns: numpy array
            - an array with cumulative returns
    ----------------------------------------
    EXAMPLES:
            Classic Momentum: from 12 months ago to one month ago (NOT including last month)
                - R = makePastPerformance(returns=ret, lag_start=12, lag_end=1)
    """
    # first make sure returns is a numpy array
    if isinstance(returns, pd.DataFrame):
        returns = returns.values

    n_rows, n_cols = returns.shape
    R = np.full((n_rows, n_cols), np.nan)

    # check to see if the number of lags is 1
    if lag_start - lag_end == 1:
        # if the number of lags is one then check to see if the starting lag is 1 and if it is then set R = returns.
        if lag_start == 1:
            R = returns
        # if the starting lag isn't one but the number of lags is one then set then create lagged returns matrix and
        # set the first 'lag_start' number of rows to nan.
        else:
            R[lag_start - 1:, :] = returns[:-lag_start + 1, :]
    else:
        # Set the missing returns to 0
        is_nan_ind = np.isnan(returns)
        returns[is_nan_ind] = 0

        # Use log returns for quicker calculation.
        tret = np.log(1 + returns)
        RR = np.full((n_rows, n_cols), np.nan)

        if lag_end == 0:
            RR = tret
        else:
            RR[lag_end:, :] = tret[:-lag_end, :]
            # RR[:lag_end, :] = np.nan
        # print(f"RR:")
        # print(RR)
        # calculate the cumulative log returns
        for i in range(lag_end + 1, lag_start):
            RR[i:, :] += tret[:-i, :]
            RR[:i, :] = np.nan
            # print(f"Iteration {i}:")
            # print(RR)

        R = RR
        # set the first 'frm - 1' rows to nan
        R[:lag_start - 1, :] = np.nan
        # put the nans back that were originally there.
        R[is_nan_ind] = np.nan
        # take exponential to get back returns
        R = np.exp(R)

    return R


# use the below lines to filter out stocks that don't have sharecodes 10 or 11.
# import pandas as pd
# saveFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'
# shrcd = pd.read_csv(saveFolder + 'shrcd.csv', index_col=0).fillna(0).replace([np.inf, -np.inf], 0).astype(int)
# shrcd = shrcd.astype(int)
# colsToKeep = np.where(((shrcd == 10) | (shrcd == 11).any()))[1]
# colsToKeep = np.unique(colsToKeep)
# ret_dom = ret.reindex(columns=ret.columns[colsToKeep])
# ret_dom = ret.iloc[:, colsToKeep]
# test = makePastPerformance(ret_dom, 12, 1)

# use the below returns for a quick way to test the output in python and matlab, respectively.
# returns_python = pd.DataFrame({
#     'A': [0.01, -0.02, 0.03, -0.04, 0.05, -0.06, 0.07, -0.08, 0.09, -0.10, 0.11, -0.12, 0.13, -0.14, 0.15],
#     'B': [0.02, 0.03, -0.04, 0.01, -0.06, 0.07, -0.08, 0.05, -0.10, 0.11, -0.12, 0.09, -0.14, 0.15, -0.16],
#     'C': [-0.03, 0.04, 0.01, 0.02, 0.07, -0.08, 0.05, 0.06, 0.11, -0.12, 0.09, 0.10, 0.15, -0.16, 0.13],
#     'D': [0.04, -0.01, 0.02, 0.03, -0.08, 0.05, 0.06, 0.07, -0.12, 0.09, 0.10, 0.11, -0.16, 0.13, 0.14],
# })

#  returns_matlab = [
#  0.01,  0.02, -0.03,  0.04;
# -0.02,  0.03,  0.04, -0.01;
#  0.03, -0.04,  0.01,  0.02;
# -0.04,  0.01,  0.02,  0.03;
#  0.05, -0.06,  0.07, -0.08;
# -0.06,  0.07, -0.08,  0.05;
#  0.07, -0.08,  0.05,  0.06;
# -0.08,  0.05,  0.06,  0.07;
#  0.09, -0.10,  0.11, -0.12;
# -0.10,  0.11, -0.12,  0.09;
#  0.11, -0.12,  0.09,  0.10;
# -0.12,  0.09,  0.10,  0.11;
#  0.13, -0.14,  0.15, -0.16;
# -0.14,  0.15, -0.16,  0.13;
#  0.15, -0.16,  0.13,  0.14;
# ]

# test = makePastPerformance(returns_python, 12, 1)

