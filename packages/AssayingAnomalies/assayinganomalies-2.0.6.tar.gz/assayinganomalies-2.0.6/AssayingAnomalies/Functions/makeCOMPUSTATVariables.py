"""makeCOMPUSTATVariables(parameters, dataframe, quarterlyIndicator) uses the stored annual and quarterly COMPUSTAT-CRSP
linked files to create matrices of dimensions number of months by number of stocks for all variables."""

import numpy as np
import pandas as pd
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor


def makeCOMPUSTATVariables(params, data, quarterly_indicator=False):
    # set paths
    crspFolder = params.crspFolder + os.sep
    compFolder = params.compFolder + os.sep

    # load a few variables
    permno = pd.read_csv(crspFolder + 'permno.csv', dtype=np.int32, index_col=0)
    dates = pd.read_csv(crspFolder + 'dates.csv', dtype=np.int32, index_col=0)
    ret = pd.read_csv(crspFolder + 'ret.csv', index_col=0)

    # ret columns names need to be integers for comparison later on
    data['permno'] = data['permno'].astype(int)
    ret.columns = ret.columns.values.astype(float).astype(int)

    # Store a few constants
    nStocks = len(permno)
    nMonths = len(dates)
    nObs = nStocks * nMonths

    # Create the linking table with CRSP
    # rptdDates = np.tile(dates, (nStocks, 1)).T.flatten()
    # rptdPermno = np.tile(permno, (nMonths, 1)).flatten()
    # crspMatLink = np.vstack((rptdPermno, rptdDates)).T
    # crspMatLinkTab = pd.DataFrame(crspMatLink, columns=['permno', 'd
    # Store the variable names & drop the permno and dates
    varNames = data.columns[1:].values
    idxToDrop = np.isin(varNames, ['permno', 'dates'])
    varNames = varNames[~idxToDrop]

    # Store the number of variable names
    nVarNames = len(varNames)

    # Create dataframes of single varNames
    # test = varNames[2:4]
    # for i, col in enumerate(test):
    # print(data.columns)
    if not params.num_cpus > 1:
        for i, col in enumerate(varNames):
            print(f"Now working on COMPUSTAT variable {col}, which is {i + 1}/{nVarNames}")
            # temptable = pd.pivot_table(crsp_msf, index='permno', columns='dates', values = i)
            temptable = pd.pivot(data, index='dates', columns='permno', values=col)
            # temptable.to_csv(compFolder + col + '.csv')

            # Align columns and rows with ret
            # Get firms that are in ret but not in compustat variable
            missing_permnos = ret.columns.difference(temptable.columns)

            # Create corresponding columns
            for permno in missing_permnos:
                temptable[permno] = np.nan

            # Align index (dates)
            missing_dates = ret.index.difference(temptable.index)
            for date in missing_dates:
                temptable.loc[date] = np.nan

            # Sort index and columns to match 'ret'
            temptable = temptable.reindex(index=ret.index, columns=ret.columns)
            # print(temptable.shape)

            if quarterly_indicator is True and col != 'FQTR':
                stocks_with_data_ind = temptable.columns[temptable.notna().any().values]
                n_stocks_with_data = len(stocks_with_data_ind)

                # Loop through them
                for c in stocks_with_data_ind:
                    # Find the first and last rows
                    first_r = temptable.loc[:, c].first_valid_index().astype(int)
                    last_r = temptable.loc[:, c].last_valid_index().astype(int)

                    # Loop through the rows/months
                    for r in range(first_r + 1, min(nMonths, last_r + 3)):
                        if np.isnan(temptable.at[r, c]):
                            # Fill in the missing ones
                            temptable.at[r, c] = temptable.at[r - 1, c]

            # Save the  temptable
            temptable.to_csv(compFolder + col.upper() + '.csv')

    else:  # :TODO When aligning columns, use .reindex instead. It is much faster.
        def process_and_save_var(permno, dates, col, quarterly_indicator=False):
            print(f"Now working on COMPUSTAT variable {col}")
            # temptable = pd.pivot_table(crsp_msf, index='permno', columns='dates', values = i)
            temptable = pd.pivot(data, index='dates', columns='permno', values=col)
            # temptable.to_csv(compFolder + col + '.csv')

            # Align columns and rows.
            temptable = temptable.reindex(index=dates.values.flatten(), columns=permno.values.flatten(), fill_value=np.nan)

            # # Align columns and rows with ret
            # # Get firms that are in ret but not in compustat variable
            # missing_permnos = ret.columns.difference(temptable.columns)
            #
            # # Create corresponding columns
            # for permno in missing_permnos:
            #     temptable[permno] = np.nan
            #
            # # Align index (dates)
            # missing_dates = ret.index.difference(temptable.index)
            # for date in missing_dates:
            #     temptable.loc[date] = np.nan
            #
            # # Sort index and columns to match 'ret'
            # temptable = temptable.reindex(index=ret.index, columns=ret.columns)
            # print(temptable.shape)

            if quarterly_indicator is True and col != 'FQTR':
                stocks_with_data_ind = temptable.columns[temptable.notna().any().values]
                n_stocks_with_data = len(stocks_with_data_ind)

                # Loop through them
                for c in stocks_with_data_ind:
                    # Find the first and last rows
                    first_r = temptable.loc[:, c].first_valid_index().astype(int)
                    last_r = temptable.loc[:, c].last_valid_index().astype(int)

                    # Loop through the rows/months
                    for r in range(first_r + 1, min(nMonths, last_r + 3)):
                        if np.isnan(temptable.at[r, c]):
                            # Fill in the missing ones
                            temptable.at[r, c] = temptable.at[r - 1, c]

            # Save the  temptable
            temptable.to_csv(compFolder + col.upper() + '.csv')

            # Print statement
            print(f"Completed COMPUSTAT variable {col} with shape {temptable.shape}")

        with ThreadPoolExecutor(max_workers=params.num_cpus) as executor:
            # Submit tasks to the thread pool
            if quarterly_indicator:
                futures = [executor.submit(process_and_save_var, permno, dates, var, quarterly_indicator=True) for var in varNames]
            else:
                futures = [executor.submit(process_and_save_var, permno, dates, var, quarterly_indicator=False) for var in varNames]
            # wait for each task to complete and print any errors if they exist.
            for future in futures:
                future.result()  # Waits for the individual task to complete

# Uncomment to debug
# from AssayingAnomalies import Config
# params = Config()
# params.set_up()
# data = pd.read_csv(params.crspFolder + os.sep + 'adj_comp_fundq_linked.csv')
# makeCOMPUSTATVariables(params=params, data=data, quarterly_indicator=True)
#
