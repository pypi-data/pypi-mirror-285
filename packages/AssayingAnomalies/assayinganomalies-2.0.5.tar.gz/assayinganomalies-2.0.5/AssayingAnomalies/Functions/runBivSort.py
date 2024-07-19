import numpy as np
import pandas as pd
from AssayingAnomalies.Functions.estFactorRegs import estFactorRegs
from AssayingAnomalies.Functions.prt_sort_results import prt_sort_results
from AssayingAnomalies.Functions.runUnivSort import runUnivSort
from AssayingAnomalies.Functions.grs_test_p import grs_test_p


def runBivSort(params, ret, ind, nptf1, nptf2, mcap, dates, **kwargs):
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

    # Run a univariate sort to get the underlying portfolios
    res = runUnivSort(params=params, ret=ret, ind=ind, mcap=mcap, dates=dates, **p)

    # Add the GRS test results to 'res' dictionary
    res["grsPval"], res["grsFstat"], res["grsDoF"] = grs_test_p(res)

    # Store a few constants
    nMonths = len(res["dates"])

    # Conditional strategies: High minus low var 1, conditioned on var 2
    longShortCondStrats = np.empty((nMonths, nptf2))
    longShortCondStrats[:] = np.nan
    for i in range(nptf2):
        thisLongInd = (nptf1 - 1) * nptf2 + i
        thisShortInd = i
        longShortCondStrats[:, i] = res["pret"][:, thisLongInd] - res["pret"][:, thisShortInd]

    cond_res_1 = estFactorRegs(params, longShortCondStrats, res["dates"], p["factorModel"], addLongShort=0, inputIsExcessRets=1)

    # Conditional strategies: High minus low var 2, conditioned on var 1
    longShortCondStrats = np.empty((nMonths, nptf1))
    longShortCondStrats[:] = np.nan
    for i in range(nptf1):
        thisLongInd = (i * nptf2) + nptf2 - 1
        thisShortInd = (i * nptf2)
        longShortCondStrats[:, i] = res["pret"][:, thisLongInd] - res["pret"][:, thisShortInd]

    cond_res_2 = estFactorRegs(params, longShortCondStrats, res["dates"], p["factorModel"], addLongShort=0, inputIsExcessRets=1)

    # Update cond_res with the second set of conditional results
    cond_res = {'cond_res_1': cond_res_1, 'cond_res_2': cond_res_2}

    if p['printResults'] != 0:
        # Print the GRS results
        grsres1 = (f"{res['grsPval'][0]:.2f}     {res['grsFstat'][0]:.2f}     {round(res['grsDoF'][0][0])}     "
                   f"{round(res['grsDoF'][0][1])}")
        grsres2 = (f"{res['grsPval'][1]:.2f}     {res['grsFstat'][1]:.2f}     {round(res['grsDoF'][1][0])}     "
                   f"{round(res['grsDoF'][1][1])}")
        print("      GRS test results:  p-value     F-stat  df1  df2")
        print(f"      full test -        {grsres1}")
        print(f"      partial test -     {grsres2}")

        # # Add a few descriptors to the structure
        for i in range(2):
            cond_res[f'cond_res_{i+1}']['w'] = p['weighting']
            cond_res[f'cond_res_{i+1}']['hperiod'] = p['holdingPeriod']


        # # Print the conditional strategies
        prt_sort_results(cond_res['cond_res_1'], lsprt=0)
        prt_sort_results(cond_res['cond_res_2'], lsprt=0)

        # Print the average returns, number of firms, and market cap
        print("Portfolio Average Excess Returns (%/month)")
        print("     ")
        if res['xret'].shape[0] == nptf1 * nptf2: # adding this to check if the l/s port xret has been appended or not
            print(np.round(res['xret'], decimals=4).reshape(nptf2, nptf1))
        else:
            print(np.round(res['xret'][:-1], decimals=4).reshape(nptf2, nptf1))
        print("Portfolio Average Number of Firms")
        print("     ")
        if res['xret'].shape[0] == nptf1 * nptf2:
            print(np.round(np.nanmean(res['ptfNumStocks'], axis=0), decimals=0).reshape(nptf2, nptf1))
        else:
            print(np.round(np.nanmean(res['ptfNumStocks'], axis=0), decimals=0)[:-1].reshape(nptf2, nptf1))
        print("Portfolio Average Firm Size ($10^6)")
        print("     ")
        if res['xret'].shape[0] == nptf1 * nptf2:
            print(np.round(np.nanmean(res['ptfMarketCap'] / res['ptfNumStocks'], axis=0), decimals=0).reshape(nptf2, nptf1))
        else:
            print(np.round(np.nanmean(res['ptfMarketCap'] / res['ptfNumStocks'][:, :-1], axis=0), decimals=0).reshape(nptf2, nptf1))

    return res, cond_res

# # Test the function
# import scipy.io
# import os
# from AssayingAnomalies import Config
# from AssayingAnomalies.Functions.makeBivSortInd import makeBivSortInd
#
# params = Config()
# params.prompt_user()
# params.make_folders()
# path = r"C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\AssayingAnomalies-main\AssayingAnomalies-main\Data" + os.sep
# R = scipy.io.loadmat(path + 'R.mat')['R']
# # R = pd.read_csv(path + 'R.csv', index_col=0)
# me = scipy.io.loadmat(path + 'me.mat')['me']
# NYSE = scipy.io.loadmat(path + 'NYSE.mat')['NYSE']
# ind1 = makeBivSortInd(me, 5, R, 5)
# ret = scipy.io.loadmat(path + 'ret.mat')['ret']
# dates = scipy.io.loadmat(path + os.sep + 'CRSP' + os.sep + 'dates.mat')['dates']
# dates = dates.flatten()
# test_res1, test_cond_res1 = runBivSort(params=params, ret=ret, ind=ind1, nptf1=5, nptf2=5, dates=dates, mcap=me)
#
# ind2 = makeBivSortInd(me, 2, R, [30, 70])
# test_res2, test_cond_res2 = runBivSort(params=params, ret=ret, ind=ind2, nptf1=3, nptf2=2, dates=dates, mcap=me)
#
# ind3 = makeBivSortInd(me, 5, R, 5, sort_type='conditional')
# test_res3, test_cond_res3 = runBivSort(params=params, ret=ret, ind=ind3, nptf1=5, nptf2=5, dates=dates, mcap=me)
