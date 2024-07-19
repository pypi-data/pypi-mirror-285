import pandas as pd
import numpy as np
from datetime import datetime
import os
from .getFFFactors import getFFFactors
from .makeIndustryClassifications import makeIndustryClassifications
from .makeUniverses import makeUniverses
from .makePastPerformance import makePastPerformance
from .makeIndustryReturns import makeIndustryReturns


def makeCRSPDerivedVariables(params):
    """
    This function creates and stores a structure that contains indicators for small/large caps based on two
    classifications: Fama-French (< or > than NYSE 50th percentile) and Russell ((not) in the top 1000 stocks based on
    market cap).
    ------------------------------------------------------------------------------------------
    Required Inputs:

    ------------------------------------------------------------------------------------------
    Output:
        -None

    ------------------------------------------------------------------------------------------
    Examples:
    makeCRSPDerivedVariables(Params)
    ------------------------------------------------------------------------------------------
    Dependencies:
        -Requires makeCRSPMonthlyData() to have been run
    ------------------------------------------------------------------------------------------
    References
    1. Novy-Marx, R. and M. Velikov, 2023, Assaying anomalies, Working paper.

    """
    # Timekeeping
    print(f"\nNow working on making CRSP derived variables. Run started at {datetime.now()}.\n")

    # crspFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'
    crspFolder = params.crspFolder + os.sep

    "Load the necessary data from cloud"
    ret_x_dl = pd.read_csv(crspFolder + 'ret_x_dl.csv', index_col=0)
    permno = pd.read_csv(crspFolder + 'permno.csv', index_col=0)
    dates = pd.read_csv(crspFolder + 'dates.csv', index_col=0)
    crsp_msedelist = pd.read_csv(crspFolder + 'crsp_msedelist.csv', index_col=0)

    "get permnos to drop"
    #get the indices of the permnos in crsp_msedelist.permno  that are NOT in permno
    mask = np.isin(crsp_msedelist.permno, permno, invert=True)
    # get the permnos to remove
    toDrop = crsp_msedelist.permno[mask]

    "drop these permnos from msf_delist dataframe"
    crsp_msedelist = crsp_msedelist.set_index('permno')
    crsp_msedelist = crsp_msedelist.drop(toDrop)
    #changing permnos back to a column instead of index
    crsp_msedelist.reset_index(inplace=True)

    "Fill in the delisting returns. Prefer to put the delisting return in the delisting month but if that's not " \
    "possible, either because theres already a return there or its not within the date range, then we put it in the " \
    "following month. If that's not possible then we don't assign it."
    crsp_msedelist['dlstdt'] = pd.to_datetime(crsp_msedelist['dlstdt']).dt.to_period('M')
    crsp_msedelist['dlstdt'] = crsp_msedelist['dlstdt'].dt.strftime('%Y%m').astype(int)
    crsp_msedelist['permno'] = crsp_msedelist['permno'].astype(str)
    ret = ret_x_dl.copy()
    ret.index = ret.index.astype(int)

    # Iterate through each permno in crsp_msedelist
    for perm in ret.columns:
        print(perm)
        # Get the delist date and return for the permno
        delist_info = crsp_msedelist[crsp_msedelist['permno'] == perm]
        delist_date = delist_info['dlstdt'].iloc[0]
        delist_return = delist_info['dlret'].iloc[0]

        # Find the delisting month and the last month with a return observation
        if delist_date in ret.index:
            r_dt = delist_date
            r_last = ret[perm].last_valid_index()

            # Convert r_dt to a datetime object to get the previous month
            r_dt_datetime = pd.to_datetime(r_dt, format='%Y%m')
            prev_month = int((r_dt_datetime - pd.DateOffset(months=1)).strftime('%Y%m'))

            # Choose where to assign the delisting return
            if pd.isna(ret.at[r_dt, perm]) and pd.notna(ret.at[prev_month, perm]):
                r = r_dt
            elif r_last in ret.index and r_last < ret.index[-1]:
                r = r_last
            else:
                r = None

            # Assign the delisting return if a suitable date is found
            if r is not None:
                ret.at[r, perm] = delist_return

    # Get the delisting return for Kodak. Should equal -0.5381
    c = np.where(permno == 11754)[0][0]
    r = np.where(dates == 201201)[0][0]
    kodak_delist_ret = ret.iloc[r, c]
    print(f'Adjusting for delisting complete. Kodak\'s delisting return was {kodak_delist_ret:.4f}')

    "Save the returns dataframe"
    ret.to_csv(crspFolder + 'ret.csv')

    "load additional objects"
    exchcd = pd.read_csv(crspFolder + 'exchcd.csv', index_col=0)
    vol_x_adj = pd.read_csv(crspFolder + 'vol_x_adj.csv', index_col=0)

    "Adjust NASDAQ volume following Gao and Ritter (2010). See their Appendix B for more details"
    vol = vol_x_adj.copy()

    "Requires too much memory to do entire dataframe at once. Will try and go row by row"
    # Divide by 2 prior to Feb 2001
    for i in range(len(exchcd.columns)):
    # for i in range(10):
    #     print(vol.index[i])
        # Since iterating over columns, I only need the row numbers where both conditions are satisfied for a particular column
        rows = np.where((exchcd.iloc[:, i]==3) & (exchcd.index < 200102))[0]
        vol.iloc[rows, i] = vol.iloc[rows, i]/2

    # Divide by 1.8 for most of 2001
    for i in range(len(exchcd.columns)):
    # for i in range(10):
    #     print(vol.index[i])
        # Since iterating over columns, I only need the row numbers where both conditions are satisfied for a particular column
        rows = np.where((exchcd.iloc[:, i]==3) & (exchcd.index >= 200102) & (exchcd.index < 200201))[0]
        vol.iloc[rows, i] = vol.iloc[rows, i]/1.8

    # Divide by 1.6 for 2002 and 2003
    for i in range(len(exchcd.columns)):
    # for i in range(10):
    #     print(vol.index[i])
        # Since iterating over columns, I only need the row numbers where both conditions are satisfied for a particular column
        rows = np.where((exchcd.iloc[:, i]==3) & (exchcd.index >= 200201) & (exchcd.index < 200401))[0]
        vol.iloc[rows, i] = vol.iloc[rows, i]/1.6

    vol.to_csv(crspFolder + 'vol.csv')

    "Make market capitalization"
    prc = pd.read_csv(crspFolder + 'prc.csv', index_col=0)
    shrout = pd.read_csv(crspFolder + 'shrout.csv', index_col=0)
    me = np.abs(prc) * shrout / 1000
    # replace zeros with nan
    me.replace(0, np.nan, inplace=True)
    me.to_csv(crspFolder + 'me.csv')

    "Make dates for plotting"
    # convert dates into decimal year format. E.g. 20230401 = 2023.25
    # "//" performs integer division which == 'floor' in MATLAB
    # and '%' == 'mod', which calculates the remainder.
    pdates = dates // 100 + dates % 100 / 12
    pdates.to_csv(crspFolder + 'pdates.csv')

    "Make the NYSE indicator variable"
    # This code creates a boolean array of the same size as exchcd that has a value of True where exchcd is equal to 1 and
    # False otherwise. The .astype(int) method is then used to convert the boolean values to integers, so True becomes 1 and
    # False becomes 0. This gives an array with the same shape as exchcd, but with 1s where exchcd is equal to 1 and 0s
    # elsewhere
    NYSE = (exchcd == 1).astype(int)
    NYSE.to_csv(crspFolder + 'NYSE.csv')

    "Download, clean up, and save the Fama-French factors from Ken French's website"
    getFFFactors(params=params)

    "Rename the SIC code variable and create Fama-French industry variables"
    makeIndustryClassifications(params=params)

    "Make & save the industry returns based on FF49 classification"
    FF49 = pd.read_csv(crspFolder + 'FF49.csv', index_col=0).astype(float)
    iFF49ret, iFF49reta = makeIndustryReturns(params, FF49)
    pd.DataFrame(iFF49ret).to_csv(crspFolder + 'iFF49ret.csv')
    pd.DataFrame(iFF49reta).to_csv(crspFolder + 'iFF49reta.csv')

    """Next the function makeUniverses is called."""
    # ---within makeUniverses is makeUnivSortInd, runUnivSort, calcPtfRets, calcTcosts, assignToPtf, estFactorRegs,
    makeUniverses(params=params)

    "Make Share Issuance Variables"
    shrout = pd.read_csv(crspFolder + 'shrout.csv', index_col=0)
    cfacshr = pd.read_csv(crspFolder + 'cfacshr.csv', index_col=0)
    ashrout = shrout * cfacshr
    ashrout.to_csv(crspFolder + 'ashrout.csv')
    dashrout = np.log(ashrout / ashrout.shift(12))
    dashrout.to_csv(crspFolder + 'dashrout.csv')

    "Make Momentumm varibles"
    ret = pd.read_csv(crspFolder + 'ret.csv', index_col=0)

    R = pd.DataFrame(makePastPerformance(ret, 12, 1), columns=ret.columns, index=ret.index)
    R62 = pd.DataFrame(makePastPerformance(ret, 6, 1), columns=ret.columns, index=ret.index)
    R127 = pd.DataFrame(makePastPerformance(ret, 12, 6), columns=ret.columns, index=ret.index)
    R3613 = pd.DataFrame(makePastPerformance(ret, 36, 12), columns=ret.columns, index=ret.index)

    R.to_csv(crspFolder + 'R.csv')
    R62.to_csv(crspFolder + 'R62.csv')
    R127.to_csv(crspFolder + 'R127.csv')
    R3613.to_csv(crspFolder + 'R3613.csv')

    "Test that your data matches up with some reference data"
    # TODO:Fix I haven't completed this section yet.

    "Timekeeping"
    print(f"\nCRSP monthly derived variables run ended at {datetime.now()}.\n")

    return

# makeCRSPDerivedVariables()

