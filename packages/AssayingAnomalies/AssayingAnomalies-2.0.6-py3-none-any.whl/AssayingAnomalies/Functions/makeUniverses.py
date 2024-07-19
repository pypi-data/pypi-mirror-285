import numpy as np
import pandas as pd
from datetime import datetime
import os
from AssayingAnomalies.Functions.runUnivSort import runUnivSort
from AssayingAnomalies.Functions.makeUnivSortInd import makeUnivSortInd
from AssayingAnomalies.Functions.rank_with_nan import rank_with_nan


def makeUniverses(params):
    """This function creates and stores a structure that contains indicators for small/large caps based on two
    classifications: Fama-French (< or > than NYSE 50th percentile) and Russell ((not) in the top 1000 stocks based on
    market cap).
    ------------------------------------------------------------------------------------------
    Required Inputs:

    ------------------------------------------------------------------------------------------
    Output:
        -None

    ------------------------------------------------------------------------------------------
    Examples:
    makeUniverses(Params)
    ------------------------------------------------------------------------------------------
    Dependencies:
        -Uses rowrank(), runUnivSort()
    ------------------------------------------------------------------------------------------
    References
    1. Novy-Marx, R. and M. Velikov, 2023, Assaying anomalies, Working paper.

    """

    # Timekeeping
    print(f"\n\n\nNow creating universes. Run began at {datetime.now()}.\n")

    # Set dataPaths
    # crspFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'
    crspFolder = params.crspFolder + os.sep

    ret = pd.read_csv(crspFolder + 'ret.csv', index_col=0)
    me = pd.read_csv(crspFolder + 'me.csv', index_col=0)
    me.index = me.index.astype(int)
    me.columns = pd.to_numeric(me.columns, errors='coerce').astype(int)
    NYSE = pd.read_csv(crspFolder + 'NYSE.csv', index_col=0)
    ff = pd.read_csv(crspFolder + 'ff.csv', index_col=0)
    dates = pd.read_csv(crspFolder + 'dates.csv', index_col=0)

    # create a matrix ranking each stock from largest to smallest each year
    # rme = pd.DataFrame(rankdata(-me, method='average', axis=1, nan_policy='omit')) # TODO:Note Once I update to scipy >= 1.10.0, this line will replace the following 9 lines of code.
    # rme = np.zeros_like(me)
    # for i in range(len(me)):
    #     temp = np.array(me.iloc[i, :]) # select ith row of me
    #     new_ar = np.nan * np.zeros_like(temp) # create array of nan's same length as 'temp'
    #     mask_indx = np.where(~np.isnan(temp))[0] # location of non-nan values in 'temp'
    #     temp = temp[~np.isnan(temp)] # removes nan values
    #     temp = rankdata(-temp) # ranks the stocks from largest to smallest
    #     new_ar[mask_indx] = temp # replaces the nan values in new_ar with corresponding ranks
    #     rme[i] = new_ar # sets ith row of rme.
    rme = pd.DataFrame(rank_with_nan(-me))
    rme.columns = me.columns
    rme.index = me.index
    rme.columns = rme.columns.astype(int)
    # rme.columns = pd.to_numeric(rme.columns, errors='coerce').astype(int)
    # checking apples rank in 202012. Should return 1
    if dates.values.flatten()[-1] >=202012:
        print("Apple's rank as of December 2020 is " + str(rme.loc[202012, 14593]))


    "The next section of code relies on a function 'makeUnivSortInd(me, 2, NYSE) which I will create below and then move to a seperate file later on"
    # Create empty dictionary to store FF and Russell results
    universes = {}

    # Do the FF universe first
    indFF = makeUnivSortInd(me, 2, NYSE)  # make FF index

    # Get factor loadings, portfolio returns, etc.
    results_ff = runUnivSort(params=params, ret=ret, ind=indFF, mcap=me, dates=dates, factorModel=1, printResults=1, plotFigure=0)

    # Create dictionary that will be used to store FF universe data
    universe_1 = {
        'head': 'ff',
        'ind': indFF,
        'res': results_ff
    }

    # create excess portfolio returns and store in dictionary
    universe_1['xret'] = universe_1['res']['pret'][:, :2] - np.column_stack((ff.rf.values, ff.rf.values))

    # And the Russell universe next
    indRuss = np.zeros_like(rme)
    indRuss[rme > 1000] = 1
    indRuss[rme <= 1000] = 2
    indRuss[indRuss == 0] = np.nan

    results_russell = runUnivSort(params=params, ret=ret, ind=indRuss, mcap=me, dates=dates, factorModel=1, printResults=1, plotFigure=0)

    # Create dictionary that will be used to store FF universe data
    universe_2 = {
        'head': 'Russell',
        'ind': indRuss,
        'res': results_russell
    }

    # create excess portfolio returns and store in dictionary
    universe_2['xret'] = universe_2['res']['pret'][:, :2] - np.column_stack((ff.rf.values, ff.rf.values))

    # store both universes
    universes[universe_1['head']] = universe_1
    universes[universe_2['head']] = universe_2

    # saving the universes dictionary as a pickle for now # :TODO:N
    pd.to_pickle(universes, crspFolder + 'universe.pkl')

    # Make cumulative market cap percentile. Add a tiny bit of noise to ensure proper bucketing
    tempme = me + (np.random.rand(*me.shape) - 0.5) / 1_000_000
    rme = rank_with_nan(-tempme)

    # Initialize the cumulative market cap percentile matrix
    mep = np.empty(me.shape)
    mep[:] = np.nan

    # Store number of months
    n_months = me.shape[0]

    # Change 'me' to numpy for the loop below to work
    me = me.to_numpy()

    # loop over the months
    for i in range(n_months):
        temp = me[i, :]
        ii = np.isfinite(temp)
        temp = temp[ii]
        temp = np.cumsum(-np.sort(-temp))
        temp = temp / temp[-1]
        jj = rme[i, ii].astype(int) - 1
        mep[i, ii] = temp[jj]

    # Save the market cap percentile matrix.
    mep = pd.DataFrame(mep, columns=NYSE.columns, index=NYSE.index)
    mep.to_csv(crspFolder + 'mep.csv')

    # Timekeeping
    print(f"\n\n\nUniverse creation completed at {datetime.now()}.\n")

    return

# makeUniverses()
