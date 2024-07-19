import numpy as np
import pandas as pd
import os
import statsmodels.api as sm
from scipy.stats.mstats import winsorize
from AssayingAnomalies.Functions.prt_FMB_results import prt_FMB_results


def run_Fama_MacBeth(y, RHS_variables, dates, **kwargs):
    """
    Perform a Fama-MacBeth regression using time series data. This function
    handles data preparation including lagging, winsorizing, and weighted regression,
    followed by the two-step Fama-MacBeth regression procedure.

    Parameters:
    y (numpy.ndarray or pd.DataFrame): The dependent variable in the regression,
                                       typically returns of assets, shaped as (time, firms).
    RHS_variables (list): A list of numpy.ndarrays or pd.DataFrames representing
                          independent variables. Each item should be of the shape (time, firms).
    dates (numpy.ndarray or pd.DataFrame): An array of dates corresponding to the time dimension.
    **kwargs: Keyword arguments for additional parameters:
        - numLags (int): Number of periods to lag variables. Default is 1.
        - timePeriod (list or int): Specified time period for the analysis. Default is full sample.
        - minobs (int): Minimum number of observations required. Default is 100.
        - weightMatrix (numpy.ndarray or pd.DataFrame): Matrix for weighted regression. Default is None.
        - trimIndicator (int): Indicator for whether to trim (1) or not (0). Default is 0.
        - winsorTrimPctg (float): Percentage for winsorizing. Default is 0 (no winsorizing).
        - printResults (int): Indicator for printing results (1) or not (0). Default is 1.
        - neweyWestLags (int): Number of lags for Newey-West standard errors. Default is 0 (OLS errors).
        - noConst (int): Include a constant (0) or not (1). Default is 0.
        - keepWarnings (int): Keep warnings (1) or not (0). Default is 0.

    Returns:
    dict: A dictionary containing:
        - 'beta': Coefficients from the cross-sectional regressions, [const, char1, char2, ... , charn]
        - 'bbhat': Averaged coefficients over time.
        - 't': T-statistics for the averaged coefficients.
        - 'Rbar2': Adjusted R-squared from each time period's regression.
        - 'mean_R2': Arithmetic mean of adjusted R-squared values.

    Raises:
    Exception: Outputs an error message and assigns NaN for regression failures.

    Notes:
    """
    # Convert input DataFrames to Numpy array
    if isinstance(y, pd.DataFrame):
        y = y.to_numpy()

    # Convert input DataFrames to Numpy arrays
    for i in range(len(RHS_variables)):
        if isinstance(RHS_variables[i], pd.DataFrame):
            RHS_variables[i] = RHS_variables[i].to_numpy()

    if isinstance(dates, pd.DataFrame):
        dates = dates.values.flatten().astype(int)

    # Default parameter values for **kwargs
    p = {
        'numLags': 1,
        'timePeriod': [dates[0], dates[-1]],
        'minobs': 100,
        'weightMatrix': None,
        'trimIndicator': 0,
        'winsorTrimPctg': 0,
        'printResults': 1,
        'neweyWestLags': 0,
        'noConst': 0,
        'keepWarnings': 0,
        'labels': None
    }

    # Update parameters with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Check if user entered a subsample
    if p['timePeriod'] != [dates[0], dates[-1]]:
        # Find the start date
        s = next(i for i, date in enumerate(dates) if date >= p['timePeriod'][0])

        # Find the end date, by finding the index 'e' of the last date in the 'dates' array that is <= specified end
        # date in 'p['timePeriod']'. "next()" retrieves first item produced by the generator expression
        if len(p['timePeriod']) == 2:
            # Whatever the user chose
            e = next(i for i, date in reversed(list(enumerate(dates))) if date <= p['timePeriod'][1])
        else:
            # Or the last date in the dates array
            e = len(dates) - 1

        # Subset the input arrays
        y = y[s:e + 1, :]
        for i in range(len(RHS_variables)):
            RHS_variables[i] = RHS_variables[i][s:e + 1, :]
        dates = dates[s:e + 1]

    # Store some constants
    T = len(dates)
    n_characteristics = len(RHS_variables)

    # Check if weighted least squares
    if p['weightMatrix'] is not None:
        if isinstance(p['weightMatrix'], pd.DataFrame):
            p['weightMatrix'] = p['weightMatrix'].to_numpy()
        # Lag the weight matrix
        p['weightMatrix'] = np.roll(p['weightMatrix'], shift=p['numLags'], axis=0)[p['numLags']:, :]

    # Lag the RHS variables
    if p['numLags'] > 0:
        y = y[:-p['numLags'], :]
        for i in range(n_characteristics):
            RHS_variables[i] = np.roll(RHS_variables[i], shift=p['numLags'], axis=0)[p['numLags']:, :]

    # Winsorize if necessary
    if p['winsorTrimPctg'] > 0:
        upper = 1 - p['winsorTrimPctg'] / 100
        lower = p['winsorTrimPctg'] / 100
        for i in range(n_characteristics):
            RHS_variables[i] = winsorize(RHS_variables[i], limits=[lower, upper], axis=1, nan_policy='omit')

    # Initialize lists for storage.
    coefficients = np.empty((T-1, n_characteristics + 1))
    adjusted_r_squared = np.empty(T-1)

    # First stage of FMB regression
    for t in range(T-1):
        X_t = [RHS_variables[j][t, :].flatten() for j in range(n_characteristics)]
        X_t = np.column_stack(X_t)
        X_t = sm.add_constant(X_t)

        Y_t = y[t, :]
        Y_t = Y_t.flatten()

        try:
            if p['weightMatrix']:
                W_t = p['weightMatrix'][t, :].flatten()
                results = sm.WLS(Y_t, X_t, weights=W_t, missing='drop', hasconst=True).fit()
            else:
                results = sm.OLS(Y_t, X_t, missing='drop', hasconst=True).fit()
            results.summary()
            coefficients[t, :] = results.params
            adjusted_r_squared[t] = results.rsquared_adj
        except Exception as e:
            # print(f"{e}")
            coefficients[t, :] = np.nan
            adjusted_r_squared[t] = np.nan

    # Calculate the arithmetic mean of adjusted_r_squared
    mean_R2 = np.nanmean(adjusted_r_squared)

    # Initialize array to hold the second stage results
    bhat = np.nan * np.ones(coefficients.shape[1])
    t_stat = np.nan * np.ones(coefficients.shape[1])

    # Second stage of FMB regression.
    for i in range(coefficients.shape[1]):
        y = coefficients[:, i]
        x = np.ones_like(y)

        if p['neweyWestLags'] > 0:
            # Newey-West estimator
            model = sm.OLS(y, x, missing='drop')
            results = model.fit(cov_type='HAC', cov_kwds={'maxlags': p['neweyWestLags']})
        else:
            # Simple OLS
            model = sm.OLS(y, x, missing='drop')
            results = model.fit()

        bhat[i] = results.params[0]
        t_stat[i] = results.tvalues[0]

    res = {
        'beta': coefficients,
        'bhat': bhat,
        't': t_stat,
        'Rbar2': adjusted_r_squared,
        'mean_R2': mean_R2,
    }

    if p['printResults'] == 1:
        prt_FMB_results(p, res['bhat'], res['t'])

    return res


#
# from AssayingAnomalies import Config
# params = Config()
# params.set_up()
#
# y = pd.read_csv(params.crspFolder + '/ret.csv', index_col=0).astype(float).to_numpy()
# R = pd.read_csv(params.crspFolder + '/R.csv', index_col=0).astype(float)
# me = pd.read_csv(params.crspFolder + '/me.csv', index_col=0).astype(float)
# RHS_variables = [100*np.log(me), R]
# dates = pd.read_csv(params.crspFolder + '/dates.csv', index_col=0)
#
# results = run_Fama_MacBeth(y, RHS_variables, dates)
#
