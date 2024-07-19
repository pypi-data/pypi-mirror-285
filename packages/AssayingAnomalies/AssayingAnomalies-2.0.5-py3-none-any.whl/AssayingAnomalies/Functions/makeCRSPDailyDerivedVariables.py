import numpy as np
import pandas as pd
from datetime import datetime
import os
import dask.dataframe as dd
from AssayingAnomalies.Functions.getFFDailyFactors import getFFDailyFactors
from AssayingAnomalies.Functions.make_CAR3 import make_CAR3
from AssayingAnomalies.Functions.make_ivol import make_ivol


def makeCRSPDailyDerivedVariables(params):
    # Timekeeping
    print(f"\nNow working on making CRSP daily derived variables. Run started at {datetime.now()}.\n")

    # set the path to crsp daily folder
    crsp_folder = params.crspFolder + os.sep

    # set the path to crsp daily folder
    daily_crsp_folder = params.daily_crsp_folder + os.sep

    # set the path to ff data folder
    ff_data_folder = params.ff_data_folder + os.sep

    "Make market capitalization"
    dme = np.abs(dd.read_parquet(daily_crsp_folder + 'dprc.parquet')) \
          * dd.read_parquet(daily_crsp_folder + 'dshrout.parquet') / 1000
    dme = dme.where(dme != 0, np.nan)
    dme = dme.compute()
    dme.to_parquet(daily_crsp_folder + 'dme.parquet')

    "Load the necessary data from storage"
    dret_x_dl = pd.read_parquet(daily_crsp_folder + 'dret_x_adj.parquet').sort_index()
    permno = pd.read_csv(crsp_folder + 'permno.csv', index_col=0)
    crsp_dsedelist = pd.read_csv(daily_crsp_folder + 'crsp_dsedelist.csv', index_col=0)

    "get permnos to drop"
    #get the indices of the permnos in crsp_msedelist.permno  that are NOT in permno
    mask = np.isin(crsp_dsedelist.permno, permno, invert=True)
    # get the permnos to remove
    toDrop = crsp_dsedelist.permno[mask]

    "drop these permnos from crsp_dsedelist dataframe"
    crsp_dsedelist = crsp_dsedelist.set_index('permno')
    crsp_dsedelist = crsp_dsedelist.drop(toDrop)
    #changing permnos back to a column instead of index
    crsp_dsedelist.reset_index(inplace=True)

    # The index of dret_x_dl is 'YYYY-MM-DD' but ddates is saved as 'YYYYMMDD', therefor I recreate the series to match.
    ddates = dd.read_parquet(daily_crsp_folder + 'crsp_dsf*.parquet', columns='date').unique().astype(str)
    ddates = ddates.compute()

    "fill in the delisting returns"
    dret = dret_x_dl.copy()
    for i in range(len(crsp_dsedelist)):
        # for i in range(500):
        "find the index in permno of ith permno in the delist dataframe"
        c = np.where(permno == crsp_dsedelist['permno'][i])[0][0]
        # print(c)
        "find the index in dates that corresponds to the delisting date of the ith permno"
        r_dt_ar = np.where(ddates == crsp_dsedelist['dlstdt'][i])[0]
        if r_dt_ar.size == 0:
            continue
        else:
            r_dt = r_dt_ar[0]
        # print(r_dt)
        "returns a series of row numbers in ret dataframe where the delisted permno has finite returns"
        r_last_array = np.where(np.isfinite(dret.iloc[:, c]) == True)[0]
        "check to see of the array is empty, and if it is, skip to the next iteration of the loop"
        if r_last_array.size == 0:
            continue
        else:
            "selects the last index, i.e., the row number of the final finite return for delisted permno"
            r_last = r_last_array[-1] + 1
            # print(r_last)
        if np.isfinite(dret.iloc[r_dt, c]):
            if r_last < len(ddates):
                "assigns the delisting return to the position following the last finite return"
                dret.iloc[(r_last), c] = crsp_dsedelist.dlret[i]
        else:
            dret.iloc[r_dt, c] = crsp_dsedelist.dlret[i]

    "Save the returns dataframe"
    dret.columns = dret.columns.astype(str)
    dret.to_parquet(daily_crsp_folder + 'dret.parquet')

    "Adjust NASDAQ volume following Gao and Ritter (2010). See their Appendix B for more details"
    "To adjust the volume, we first need to create the daily exchange code matrix"
    exchcd = pd.read_csv(crsp_folder + 'exchcd.csv', index_col=0)
    exchcd.index = pd.to_datetime(exchcd.index.astype(int), format='%Y%m')
    ddates = pd.read_csv(daily_crsp_folder + 'ddates.csv', index_col=0).values.flatten().astype(int)
    ddates = pd.to_datetime(ddates, format='%Y%m%d')
    dexchcd = exchcd.reindex(ddates, method='ffill')
    dexchcd.to_parquet(daily_crsp_folder + 'dexchcd.parquet')

    # Slice dexchcd to match the size of dvol
    dvol = pd.read_parquet(daily_crsp_folder + 'dvol_x_adj.parquet').sort_index()
    dvol_columns = pd.read_parquet(daily_crsp_folder + 'dvol_x_adj.parquet').columns

    # Note: The adjusted_dvol computation assumes dvol data aligns exactly with dexchcd in structure and partitioning
    "Requires too much memory to do entire dataframe at once. Will try and go column by column."
    # Divide by 2 prior to Feb 2001
    # Divide by 1.8 for most of 2001
    # Divide by 1.6 for 2002 and 2003
    columns_to_process = dexchcd.columns[(dexchcd == 3).any()].to_list()
    for column in columns_to_process:
        print(column)
        col_index = dvol_columns.get_loc(column)
        # Since iterating over columns, I only need the row numbers where both conditions are satisfied for a particular column
        rows_first = np.where((dexchcd[column] == 3) & (dexchcd.index < pd.Timestamp('2001-02-01')))[0]
        rows_mid = np.where((dexchcd[column] == 3) & (dexchcd.index >= pd.Timestamp('20010201')) & (dexchcd.index < pd.Timestamp('20020101')))[0]
        rows_last = np.where((dexchcd[column] == 3) & (dexchcd.index >= pd.Timestamp('20020101')) & (dexchcd.index < pd.Timestamp('20040101')))[0]

        dvol.iloc[rows_first, col_index] = dvol.iloc[rows_first, col_index] / 2
        dvol.iloc[rows_mid, col_index] = dvol.iloc[rows_mid, col_index] / 1.8
        dvol.iloc[rows_last, col_index] = dvol.iloc[rows_last, col_index] / 1.6

    dvol.columns = dvol.columns.astype(str)
    dvol.to_parquet(daily_crsp_folder + 'dvol.parquet')

    "Download, clean up, and save the Fama-French factors from Ken French's website"
    getFFDailyFactors(params=params)

    "Make Amihud values"
    # first 12 month rolling amihud values

    # load the monthly returns, monthly price, and monthly dates, matrices
    ret = pd.read_csv(crsp_folder + 'ret.csv', index_col=0).astype(float)
    prc = pd.read_csv(crsp_folder + 'prc.csv', index_col=0).astype(float)
    dates = pd.read_csv(crsp_folder + 'dates.csv', index_col=0).astype(int)

    # replace zero-volume observations with nan and calculate dollar volume
    dprc = pd.read_parquet(daily_crsp_folder + 'dprc.parquet').sort_index()
    dollar_volume = np.abs(dprc) * np.abs(dvol)
    zeroVolInd = (dollar_volume == 0)
    dollar_volume[zeroVolInd] = np.nan

    # calculate the daily price impact
    dret = pd.read_parquet(daily_crsp_folder + 'dret.parquet').sort_index().astype(float)
    price_impact = np.divide(np.abs(dret), dollar_volume)

    # Take the absolute value of the monthly price and store the number of months
    prc = np.abs(prc)
    nmonths = len(ret.index)

    # Reload ddates in YYYYMMDD format
    ddates = pd.read_csv(daily_crsp_folder + 'ddates.csv', index_col=0).astype(int)

    # initialize amihud matrix
    amihud = np.full_like(ret, np.nan)

    # Calculate amihud
    for i in range(11, nmonths):
        print(f"Month {i+1}/{nmonths}")
        # Find the days in the last year
        start_date = dates.iloc[i - 11]
        end_date = dates.iloc[i]
        index_year = ((ddates // 100 >= start_date) & (ddates // 100 <= end_date))

        # Ensure index_year is a 1D boolean array
        index_year = index_year.values.flatten()

        # Store monthly price impact for last year
        last_yr_pi = price_impact[index_year].copy()

        # Apply the filters (200 obs & price > $5)
        idx_to_drop = np.isfinite(last_yr_pi).sum(axis=0) < 200
        idx_to_drop |= prc.iloc[i, :].values.flatten() <= 5
        last_yr_pi.iloc[:, idx_to_drop] = np.nan

        # Calculate the mean price impact for the last year, ignoring NaN values
        amihud[i, :] = np.nanmean(last_yr_pi, axis=0)

    amihud = pd.DataFrame(amihud)
    amihud.index = dates.values.flatten()
    amihud.columns = permno.values.flatten().astype(str)
    amihud.to_parquet(crsp_folder + 'amihud.parquet')

    "Make other measures from the daily data"
    # Realized volatilities
    # Initialize the matrices
    n_months, n_stocks = ret.shape
    RVOL_matrices = {period: np.full((n_months, n_stocks), np.nan) for period in [1, 3, 6, 12, 36, 60]}
    dshvol = np.full_like(ret, np.nan)
    dshvolM = np.full_like(ret, np.nan)
    dretmax = np.full_like(ret, np.nan)
    dretmin = np.full_like(ret, np.nan)

    # First turn the dates and ddates dataframes into arrays
    ddates_array = ddates.values.flatten()
    dates_array = dates.values.flatten()

    # Find the first month index
    first_month_date = ddates_array[0] // 100
    if first_month_date in dates_array:
        first_month = np.where(dates_array == first_month_date)[0][0]
    else:
        raise ValueError("First month date not found in dates array")

    # Monthly loop range
    last_month = len(dates)

    # Calculate measures
    for i in range(first_month, last_month):
        for period, RVOL in RVOL_matrices.items():
            start_index = max(i - period + 1, 0)
            ind = (ddates_array // 100 >= dates_array[start_index]) & (ddates_array // 100 <= dates_array[i])

            # Ensure ind is a 1D boolean array and matches the number of rows in dret
            ind = ind.flatten()

            # Apply the indexing to the DataFrame
            selected_dret = dret.loc[ind, :]

            RVOL[i, :] = np.nanstd(selected_dret, axis=0)

        ind1 = (ddates_array // 100 == dates_array[i])

        # Ensure ind1 is a 1D boolean array and matches the number of rows in dvol
        ind1 = ind1.flatten()

        # Apply the indexing to the DataFrame
        selected_dvol = dvol.loc[ind1, :]

        dshvol[i, :] = np.nansum(selected_dvol, axis=0)
        dshvolM[i, :] = np.nanmax(selected_dvol, axis=0)
        dretmax[i, :] = np.nanmax(selected_dvol, axis=0)
        dretmin[i, :] = np.nanmin(selected_dvol, axis=0)

    # Save the matrices
    for period, RVOL_matrix in RVOL_matrices.items():
        filename = f'RVOL{period}.csv'
        RVOL_matrix = pd.DataFrame(RVOL_matrix)
        RVOL_matrix.to_csv(crsp_folder + filename)

    dshvol = pd.DataFrame(dshvol)
    dshvol.columns = dshvol.columns.astype(str)
    dshvol.to_parquet(crsp_folder + 'dshvol.parquet')

    dshvolM = pd.DataFrame(dshvolM)
    dshvolM.columns = dshvolM.columns.astype(str)
    dshvolM.to_parquet(crsp_folder + 'dshvolM.parquet')

    dretmax = pd.DataFrame(dretmax)
    dretmax.columns = dretmax.columns.astype(str)
    dretmax.to_parquet(crsp_folder + 'dretmax.parquet')

    dretmin = pd.DataFrame(dretmin)
    dretmin.columns = dretmin.columns.astype(str)
    dretmin.to_parquet(crsp_folder + 'dretmin.parquet')

    "Make IVOLs"
    make_ivol()

    "Make CAR3s: Inilialize the CAR3 matrix, calculate abnormal returns, iterate through each month to compute the" \
    "CAR3 value for each stock at each announcement date"
    # load additional variables
    # rdq = pd.read_csv(params.compFolder + os.sep + 'RDQ.csv', index_col=0)
    # fqtr = pd.read_csv(params.compFolder + os.sep + 'FQTR.csv', index_col=0)
    # # nyse = pd.read_csv(params.crspFolder + os.sep + 'NYSE.csv', index_col=0)
    # me = pd.read_csv(params.crspFolder + os.sep + 'me.csv', index_col=0)
    #
    # # For some reason RDQ and FQTR has an additional row at the beginning of the matrix. It doesn't correspond to any
    # # date so I will check if this is the case and remove it.
    # if pd.isna(rdq.index[0]):
    #     rdq = rdq.iloc[1:, :]
    #
    # if pd.isna(fqtr.index[0]):
    #     fqtr = fqtr.iloc[1:, :]
    #
    # # Only leave the announcement dates
    # rdq = rdq.where(~fqtr.isna(), np.nan)
    #
    # # Initialize the CAR3 matrix
    # CAR3 = np.full_like(rdq, np.nan)
    #
    # # Calculate the abnormal return (in excess of the market); (ret_{i,t} - ret_{mkt,t})
    # rptdMkt_values = (1 + dmkt + drf).values
    # rptdMkt = np.tile(rptdMkt_values, (len(me.columns), 1)).T
    # dxret = 1 + dret - rptdMkt
    #
    # # Monthly loop range
    # first_month = np.where(rdq.notna().sum(axis=1) > 0)[0][0]
    # last_month = len(dates)
    #
    # # Loop over the months
    # for i in range(first_month, last_month):
    #     # Find all the announcements in the current month
    #     idx_announcements = np.where(rdq.iloc[i, :].notna())[0]
    #
    #     # Loop over the announcements
    #     for c in idx_announcements:
    #         permno = rdq.columns[c]  # Get the permno (column label) from rdq
    #
    #         # Check if the permno is in the columns of dxret
    #         if permno in dxret.columns:
    #             dxret_col_index = dxret.columns.get_loc(permno)  # Find the corresponding column in dxret
    #
    #             # Get the announcement date and find the corresponding row in ddates
    #             announcement_date = rdq.iloc[i, c]
    #             r = np.where(ddates == announcement_date)[0]
    #
    #             # Calculate the CAR3 if we found a match
    #             if r.size > 0 and r[0] < len(ddates) - 1:
    #                 CAR3[i, c] = np.prod(dxret.iloc[r[0] - 1:r[0] + 2, dxret_col_index]) - 1
    #
    # # Fill the observations between quarters; Matlab uses a helper function, but this isn't necessary in Python
    # CAR3 = pd.DataFrame(CAR3).ffill(axis=0)
    #
    # # Change the columns names to be integers
    # ret.columns = [int(float(col)) for col in ret.columns]
    # CAR3.columns = [int(float(col)) for col in rdq.columns]
    #
    # # Identify common columns between 'ret' and 'CAR3'
    # common_columns = ret.columns.intersection(CAR3.columns)
    #
    # # Initialize a mask with False for all entries in CAR3
    # idx_to_drop = pd.DataFrame(False, index=ret.index, columns=CAR3.columns)
    #
    # # Update the mask for common columns based on NaN values in 'ret'
    # idx_to_drop.loc[:, common_columns] = ret[common_columns].isna()
    #
    # # Remove all observations where ret is nan
    # CAR3[idx_to_drop] = np.nan
    #
    # # Save
    # # CAR3.to_csv(crsp_folder + 'CAR3.csv')
    # CAR3.columns = CAR3.columns.astype(str)
    # CAR3.to_parquet(crsp_folder + 'CAR3.parquet')

    make_CAR3()

    "Timekeeping"
    print(f"\nCRSP daily derived variables run ended at {datetime.now()}.\n")

    return


if __name__ == "__main__":
    from AssayingAnomalies import Config
    configure = Config()
    params = configure.load_params()
    makeCRSPDailyDerivedVariables(params)


