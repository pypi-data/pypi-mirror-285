import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
from AssayingAnomalies.Functions.calcPtfRets import calcPtfRets
from AssayingAnomalies.Functions.estFactorRegs import estFactorRegs
from AssayingAnomalies.Functions.calcTcosts import calcTcosts
from AssayingAnomalies.Functions.prt_sort_results import prt_sort_results

def runUnivSort(params, ret, ind, mcap, dates, **kwargs):
    """
    Executes a univariate sorting strategy on financial data, calculating portfolio returns,
    estimating factor models, and evaluating trading costs if specified.

    :param params: Dictionary of parameters influencing calculations such as factor models.
    :type params: dict
    :param ret: Returns of stocks over time.
    :type ret: np.ndarray | pd.DataFrame
    :param ind: Indicator matrix for portfolio membership of each stock at each time.
    :type ind: np.ndarray | pd.DataFrame
    :param mcap: Market capitalizations of stocks.
    :type mcap: np.ndarray | pd.DataFrame
    :param dates: Dates corresponding to the return data.
    :type dates: np.ndarray | pd.DataFrame
    :param kwargs: Additional optional keyword arguments:
        - 'timePeriod': Start and end dates or a vector of dates.
        - 'factorModel': Type of factor model to use.
        - 'addLongShort': Include long-short portfolio analysis.
        - 'printResults': Print the results.
        - 'plotFigure': Plot figures of the strategy results.
        - 'holdingPeriod': Holding period for stocks in portfolios.
        - 'weighting': Weighting scheme ('v' for value-weighted, 'e' for equal-weighted).

    :return: A dictionary containing various metrics and results of the portfolio analysis.
    :rtype: dict
    """

    # Convert input DataFrames to Numpy array
    if isinstance(ret, pd.DataFrame):
        ret = ret.to_numpy()

    if isinstance(ind, pd.DataFrame):
        ind = ind.to_numpy()

    if isinstance(mcap, pd.DataFrame):
        mcap = mcap.to_numpy()

    if isinstance(dates, pd.DataFrame):
        dates = dates.values.flatten()

    # Default parameter values
    p = {
        'factorModel': 4,
        'addLongShort': 1,
        'printResults': 1,
        'plotFigure': 0,
        'timePeriod': [dates[0], dates[-1]],
        'holdingPeriod': 1,
        'weighting': 'v',
        'tcosts': -99,
    }

    # Update parameters with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Check if weighting is correctly specified
    expected_weighting = {'V', 'v', 'E', 'e'}
    if p['weighting'] not in expected_weighting:
        raise ValueError("Invalid weighting value. Must be one of {'V', 'v', 'E', 'e'}")

    # Update parameters with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Check whether the dimensions are correct
    if ret.shape != ind.shape:
        raise ValueError(f"'ret' and 'ind' have different dimensions: {ret.shape} and {ind.shape}.")
    if ret.shape[0] != dates.shape[0]:
        raise ValueError(f"'ret' and 'dates' have different dimensions: {ret.shape} and {dates.shape}.")
    if ret.shape != mcap.shape:
        raise ValueError(f"'ret' and 'mcap' have different dimensions: {ret.shape} and {mcap.shape}.")

    # Check if the factor model code (if entered) is correct
    if isinstance(p['factorModel'], int) and p['factorModel'] not in {1, 3, 4, 5, 6}:
        raise ValueError("Factor model must be 1, 3, 4, 5, 6, or a user-defined matrix.")

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
        ret = ret[s:e + 1, :]
        ind = ind[s:e + 1, :]
        dates = dates[s:e + 1]
        mcap = mcap[s:e + 1, :]

    # Delete all stocks (i.e., columns) that are not held in any portfolio in the full sample
    stock_is_held = np.sum(ind, axis=0) > 0
    ret = ret[:, stock_is_held]
    ind = ind[:, stock_is_held]
    mcap = mcap[:, stock_is_held]

    # Calculate the ptf returns, # stocks, and market caps
    holding_period = p['holdingPeriod']
    weighting = p['weighting'].lower() # returns the user specified weighting as lowercase string
    pret, ptf_num_stocks, ptf_market_cap = calcPtfRets(ret, ind, mcap, holding_period, weighting)

    # Estimate the factor model regressions
    factor_model = p['factorModel']
    add_long_short = p['addLongShort']
    res = estFactorRegs(params=params, pret=pret, dates=dates, factorModel=factor_model, addLongShort=add_long_short)

    # Check if we need to estimate trading costs
    if p['tcosts'] != -99:
        tcosts = p['tcosts']
        if len(tcosts) == 1:
            # If it's just a constant tcost
            tcosts = tcosts * (mcap / mcap)
        else:
            # Remove the stocks that are not held
            tcosts = tcosts[:, stock_is_held]

            # Check if we have to subset
            if 's' in locals():
                tcosts = tcosts[s:e, :]

        # Calculate the actual trading costs
        ptf_costs, ptf_to, dW = calcTcosts(tcosts, ind, mcap, weighting=p['weighting'])

        # Store temporarily the tcosts and net portfolio returns for the
        # long/short portfolio
        tcosts_ts = ptf_costs[:, 0] + ptf_costs[:, -1]
        net_pret = res['pret'][:, -1] - tcosts_ts

        # Regress the net long/short portfolio returns on a constant
        net_res = sm.OLS(100 * net_pret, sm.add_constant(np.ones(net_pret.shape))).fit()

        # Store the tcosts output
        res['tcostsTS'] = tcosts_ts
        res['netpret'] = net_pret
        res['toTS'] = np.column_stack((ptf_to[:, 0], ptf_to[:, -1]))
        res['netxret'] = net_res['beta']
        res['tnetxret'] = net_res['tstat']
        res['turnover'] = np.nanmean(np.nanmean(res['toTS'], axis=0) / 2)
        res['tcosts'] = np.nanmean(res['tcostsTS'])
        res['ptfCosts'] = ptf_costs
        res['ptfTO'] = ptf_to

    # Store a few more variables
    res['w'] = p['weighting']
    res['dates'] = dates
    res['hperiod'] = p['holdingPeriod']
    res['ptfMarketCap'] = ptf_market_cap
    res['nPorts'] = int(ind.max())

    # Add the long-short portfolio time-series # of stocks
    if p['addLongShort'] != 0:
        res['ptfNumStocks'] = np.column_stack((ptf_num_stocks, ptf_num_stocks[:, -1] + ptf_num_stocks[:, 0]))
    else:
        res['ptfNumStocks'] = ptf_num_stocks

    # Print the results
    if p['printResults'] != 0:
        prt_sort_results(res, lsprt=p['addLongShort'])

    # Plot the figure
    if p['plotFigure'] != 0 and p['addLongShort'] != 0:
        plt.figure(83)
        plot_strategy_figs(res) # TODO:F Need to make this function

    return res
