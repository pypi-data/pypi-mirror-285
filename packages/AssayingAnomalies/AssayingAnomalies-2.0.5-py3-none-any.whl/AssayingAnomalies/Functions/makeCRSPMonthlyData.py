import numpy as np
import pandas as pd
from datetime import datetime
import os
from concurrent.futures import ThreadPoolExecutor


def makeCRSPMonthlyData(params):
    # Timekeeping
    print(f"\nNow working on making CRSP monthly data. Run started at {datetime.now()}.")

    "Set path"
    crsp_folder = params.crspFolder + os.sep

    """Load and clean msf dataframe"""
    crsp_msf = pd.read_csv(crsp_folder + 'crsp_msf.csv', index_col=0)

    "Convert dates to YYYYMM format. These are originally month end dates"
    # first convert dates to datatype - date-time"
    crsp_msf['dates'] = pd.to_datetime(crsp_msf.date)
    # then change to YYYYMM format
    crsp_msf['dates'] = crsp_msf['dates'].dt.strftime('%Y%m')
    crsp_msf['dates'] = crsp_msf['dates'].astype(int)

    "Load CRSP montly stock file with share code information"
    crsp_mseexchdates = pd.read_csv(crsp_folder + 'crsp_mseexchdates.csv', index_col=0)
    # only want to keep certain columns
    crsp_mseexchdates = crsp_mseexchdates.loc[:, ['permno', 'namedt', 'nameendt', 'shrcd', 'exchcd', 'siccd']]
    crsp_mseexchdates.duplicated(subset=['permno', 'siccd']).sum()

    # Merge the share code from the header file to crsp_msf
    crsp_msf = crsp_msf.merge(crsp_mseexchdates, how='outer', on='permno')
    duplicates = crsp_msf.duplicated(subset=['dates', 'permno', 'shrcd'])
    duplicates.sum()
    print(f"There are {duplicates.sum()} duplicate shrcd/permno/date values.")

    # creating index to drop
    idxToDrop1 = np.where(crsp_msf.date < crsp_msf.namedt)[0]
    idxToDrop2 = np.where(crsp_msf.date > crsp_msf.nameendt)[0]
    idxToDrop = np.concatenate((idxToDrop1, idxToDrop2))
    idxToDrop = np.sort(idxToDrop)

    # keeping those NOT in idxToDrop
    crsp_msf = crsp_msf.loc[~crsp_msf.index.isin(idxToDrop)]

    # delete dataframe to free up RAM (not sure if this actually does anything)
    del crsp_mseexchdates

    "Check to see if we should only keep share codes 10 or 11 (domestic common equity)"
    if params.domComEqFlag:
        crsp_msf = crsp_msf[crsp_msf['shrcd'].isin([10, 11])].copy()

    "Check to keep only the sample specified in params."
    first_date = params.sample_start*100 + 1
    last_date = (params.sample_end + 1)*100 + 1
    # idx_to_keep = np.where((crsp_msf['dates'] >= first_date) & (crsp_msf['dates'] <= last_date))
    # idx_to_keep = np.sort(idx_to_keep)
    # crsp_msf = crsp_msf.loc[crsp_msf.index.isin(idx_to_keep)]
    crsp_msf = crsp_msf[(crsp_msf['dates'] >= first_date) & (crsp_msf['dates'] <= last_date)].copy()

    "Rename returns to indicate they are without delisting adjustments"
    crsp_msf.rename(columns={'ret': 'ret_x_dl'}, inplace=True)
    "Rename volume to indicate it is without adjustment for NASDAQ"
    crsp_msf.rename(columns={'vol': 'vol_x_adj'}, inplace=True)

    "Save the link file for the COMPUSTAT matrices creation"
    crsp_link = crsp_msf.loc[:, ['permno', 'date']]
    crsp_link.to_csv(crsp_folder + 'crsp_link.csv')
    del crsp_link

    "Create and store the permno and dates vectors"
    permno = np.sort(crsp_msf['permno'].unique())
    dates = np.sort(crsp_msf['dates'].unique())

    "Save permno, dates"
    pd.DataFrame(permno).to_csv(crsp_folder + 'permno.csv')
    pd.DataFrame(dates).to_csv(crsp_folder + 'dates.csv')

    # Choose variables from crsp_msf to convert into matrices
    varNames_crsp_msf = ['shrcd', 'exchcd', 'siccd', 'prc', 'bid', 'ask', 'bidlo', 'askhi', 'vol_x_adj',
                         'shrout', 'cfacpr', 'cfacshr', 'spread', 'retx', 'ret_x_dl']

    if not params.num_cpus > 1:
        # Create DataFrames for other variables and align them with the reference DataFrame
        for i, var in enumerate(varNames_crsp_msf):
            # Create DataFrame for current variable
            temp_df = pd.pivot_table(crsp_msf, index='dates', columns='permno', values=var)

            # Align columns and rows
            temp_df = temp_df.reindex(index=dates, columns=permno, fill_value=np.nan)

            # # Align columns
            # for col in permno:
            #     if col not in temp_df.columns:
            #         temp_df[col] = np.nan
            #
            # # Align rows
            # for row in dates:
            #     if row not in temp_df.index:
            #         temp_df.loc[row] = np.nan
            #
            # # Sort index and columns to match reference DataFrame
            # temp_df = temp_df.sort_index(axis=0).sort_index(axis=1)
            print(f"{var}: {i+1}/{len(varNames_crsp_msf)} shape is {temp_df.shape}")
            # Save the aligned DataFrame
            temp_df.to_csv(crsp_folder + var + '.csv')
    else:
        def process_and_save_var(permno, dates, crsp_folder, var):
            """
            Process a single variable and save the result to a CSV file.
            """
            print(f"Processing {var}")
            temp_df = pd.pivot_table(crsp_msf, index='dates', columns='permno', values=var)

            # Align columns and rows
            temp_df = temp_df.reindex(index=dates, columns=permno, fill_value=np.nan)

            # # Align columns
            # for col in permno_list:
            #     if col not in temp_df.columns:
            #         temp_df[col] = np.nan
            #
            # # Align rows
            # for row in dates_list:
            #     if row not in temp_df.index:
            #         temp_df.loc[row] = np.nan
            #
            # # Sort index and columns to match reference DataFrame
            # temp_df = temp_df.sort_index(axis=0).sort_index(axis=1)

            # Save the aligned DataFrame
            temp_df.to_csv(crsp_folder + var + '.csv')
            print(f"Finished processing {var} with shape {temp_df.shape}")

        with ThreadPoolExecutor(max_workers=params.num_cpus) as executor:
            # Submit tasks to the thread pool
            futures = [executor.submit(process_and_save_var, permno, dates, crsp_folder, var) for var in varNames_crsp_msf]

            # wait for each task to complete and print any errors if they exist.
            for future in futures:
                future.result()  # Waits for the individual task to complete

    # Timekeeping
    print(f"\nFinished making CRSP monthly data. Run ended at {datetime.now()}.\n")

    return


# makeCRSPMonthlyData(params)


