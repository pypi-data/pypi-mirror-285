import pandas as pd
import numpy as np

def assign_to_portfolios(var: pd.DataFrame, ptfNumThresh: any([int, list]), breaksFilterInd: any([None, pd.DataFrame]),
                         portfolioMassInd: any([None, pd.DataFrame])) -> pd.DataFrame:

    # Initialize DataFrame to hold the bin assignments
    ind = pd.DataFrame(index=var.index, columns=var.columns)

    # Create quintiles.
    # If user passed a list, e.g. [30, 70] then we will infer the number of portfolios desired and created quintiles.
    if isinstance(ptfNumThresh, list):
        quintiles = [p/100 for p in ptfNumThresh]
        quintiles.insert(0, 0)
        quintiles.insert(len(quintiles), 1)
        ptfNumThresh = len(ptfNumThresh) + 1
    else:
        quintiles = np.linspace(0, 1, ptfNumThresh+1)

    # Check if we are doing cap-weighted breaks
    if portfolioMassInd is None:
        # In this case, we are not doing cap-weighting. We will check to see if the user supplied a breaks filter, e.g.
        # if breaksFilterInd is a matrix like NYSE, where only NYSE firm months have 1 otherwise zero. We previously
        # assigned nan to observations to the zeros, which we don't want to use for breakpoints
        if breaksFilterInd is not None:
            breaksFilterInd = breaksFilterInd[breaksFilterInd == 1]
            # Weight according to whether or not the firm-month is included in the index, e.g. if it is in NYSE or not.
            weighted_var = var * breaksFilterInd
            # Calculate bin_cutoffs (ignoring nan values)
            bin_cutoffs = weighted_var.quantile(q=quintiles, axis=1).T

        else:
            bin_cutoffs = var.quantile(q=quintiles, axis=1).T

        # Want to make the left and right most points are a little bit further form the previous points to ensure all
        # data is inc.
        bin_cutoffs.iloc[:, 0] -= 1e-6
        bin_cutoffs.iloc[:, -1] += 1e-6

        # Use the cutoff values to assign to portoflios
        for idx in var.index:
            row_data = var.loc[idx].astype(float)
            row_bins = bin_cutoffs.loc[idx].astype(float)
            ports = np.digitize(row_data, row_bins, right=True)
            ind.loc[idx] = ports

        outside_bin_port_value = ptfNumThresh + 1
        ind.replace({outside_bin_port_value: 0}, inplace=True)

        return ind

    else:
        # In this case, we ARE doing cap-weighting. We will first check to see if the user supplied a breaks filter,
        # e.g. if breaksFilterInd is a matrix like NYSE indicating firm-months belonging to NYSE as 1, then we will
        # assign nan to observations in var that are zero in the breaksFilterInd

        # First see if there is a NYSE filter
        if breaksFilterInd is not None:
            breaksFilterInd = breaksFilterInd[breaksFilterInd == 1]
            portfolioMassInd = portfolioMassInd[breaksFilterInd]
            # Weight according to whether or not the firm-month is included in the index, e.g. if it is in NYSE or not
            # and its contribution to total market cap in that month.
            weights = portfolioMassInd.div(portfolioMassInd.sum(axis=1), axis=0)  # Normalize each row to sum to 1.
            weighted_var = var * weights
        else:
            weights = portfolioMassInd.div(portfolioMassInd.sum(axis=1), axis=0)  # Normalize each row to sum to 1.
            weighted_var = var * weights

        # Calculate bin_cutoffs (ignoring nan values)
        bin_cutoffs = weighted_var.quantile(q=quintiles, axis=1).T

        # Want to make the left and right most points are a little bit further form the previous points to ensure all
        # data is inc.
        bin_cutoffs.iloc[:, 0] -= 1e-6
        bin_cutoffs.iloc[:, -1] += 1e-6

        # Use the cutoff values to assign to portoflios
        # Initialize DataFrame to hold the bin assignments
        ind = pd.DataFrame(index=weighted_var.index, columns=weighted_var.columns)

        for idx in weighted_var.index:
            row_data = weighted_var.loc[idx].astype(float)
            row_bins = bin_cutoffs.loc[idx].astype(float)
            ports = np.digitize(row_data, row_bins, right=True)
            ind.loc[idx] = ports

        outside_bin_port_value = ptfNumThresh + 1
        ind.replace({outside_bin_port_value: 0}, inplace=True)

    return ind
