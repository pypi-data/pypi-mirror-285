import pandas as pd
import os
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import dask.dataframe as dd


def makeCRSPDailyData(params):

    # Timekeeping
    print(f"\nNow working on making CRSP daily data. Run started at {datetime.now()}.\n")

    # Store the daily CRSP data path
    daily_crsp_path = params.daily_crsp_folder + os.sep

    # Load the permnos and create ddates
    permno = pd.read_csv(params.crspFolder + os.sep + 'permno.csv', index_col=0).astype(str)  # Assuming permno is in a CSV file
    ddates = dd.read_parquet(daily_crsp_path + 'crsp_dsf*.parquet', columns='date').unique()
    ddates = ddates.compute()

    # Load the var_names for individual dataframes. The first 2 col names are unnamed, date, and permno, so we
    # exclude them.
    var_names = pd.read_parquet(daily_crsp_path + 'crsp_dsf_' + str(params.sample_end) + '.parquet').columns.values[2:].flatten()

    # Instead of using pd.read_csv, use dd.read_parquet to load the Parquet files
    # Dask will handle these files as a single DataFrame, but under the hood,
    # it will process them in parallel, in small chunks
    if not params.num_cpus > 1:
        for i, var in enumerate(var_names):
            # for i, var in enumerate(['ret']):
            crsp_dsf = dd.read_parquet(daily_crsp_path + 'crsp_dsf*.parquet', columns=['date', 'permno', var])
            crsp_dsf = crsp_dsf[crsp_dsf['permno'].astype(str).isin(permno.values.flatten())]
            # When working with parquet files, it uses None type for missing objects values and nan for missing numeric
            # values. When we try and pivot, the None values are causing errors for some of the permnos.
            replace_dict = {None: np.nan}
            crsp_dsf[var] = crsp_dsf[var].replace(replace_dict)
            crsp_dsf = crsp_dsf.compute()
            temp_df = crsp_dsf.pivot_table(index='date', columns='permno', values=var)
            temp_df.columns = temp_df.columns.values.astype(int).astype(str)
            temp_df = temp_df.reindex(index=ddates, columns=permno.values.flatten(), fill_value=np.nan)
            temp_df.columns = temp_df.columns.astype(str)

            if var in ['ret', 'vol']:
                temp_df.to_parquet(daily_crsp_path + f'd{var}_x_adj.parquet')
                print(f"Finished processing {var}: Variable {i+1}/{len(var_names)} with shape {temp_df.shape}")
            else:
                temp_df.to_parquet(daily_crsp_path + f'd{var}.parquet')
                print(f"Finished processing {var}: Variable {i+1}/{len(var_names)} with shape {temp_df.shape}")

    else:
        def process_and_save_var(permno, ddates, daily_crsp_path, var):
            """
            Process a single variable and save the result to a CSV file.
            """
            try:
                print(f"Processing {var}")
                crsp_dsf = dd.read_parquet(daily_crsp_path + 'crsp_dsf*.parquet', columns=['date', 'permno', var])
                crsp_dsf = crsp_dsf[crsp_dsf['permno'].astype(str).isin(permno.values.flatten())]
                # When working with parquet files, it uses None type for missing objects values and nan for missing numeric
                # values. When we try and pivot, the None values are causing errors for some of the permnos.
                replace_dict = {None: np.nan}
                crsp_dsf[var] = crsp_dsf[var].replace(replace_dict)
                crsp_dsf = crsp_dsf.compute()
                temp_df = crsp_dsf.pivot_table(index='date', columns='permno', values=var)
                temp_df.columns = temp_df.columns.values.astype(int).astype(str)
                temp_df = temp_df.reindex(index=ddates, columns=permno.values.flatten(), fill_value=np.nan)
                temp_df.columns = temp_df.columns.astype(str)

                if var in ['ret', 'vol']:
                    temp_df.to_parquet(daily_crsp_path + f'd{var}_x_adj.parquet')
                    print(f"Finished processing {var} with shape {temp_df.shape}")
                else:
                    temp_df.to_parquet(daily_crsp_path + f'd{var}.parquet')
                    print(f"Finished processing {var} with shape {temp_df.shape}")
            except Exception as e:
                print(f"Error processing {var}: {e}")

        with ThreadPoolExecutor(max_workers=2) as executor:
            # Submit tasks to the thread pool
            futures = [executor.submit(process_and_save_var, permno, ddates, daily_crsp_path, var)
                       for var in var_names]
            # futures = [executor.submit(process_and_save_var, permno, ddates, daily_crsp_path, var)
            # for var in ['ret', 'vol']]  # Uncomment to debug.

            # wait for each task to complete and print any errors if they exist.
            for future in futures:
                future.result()  # Waits for the individual task to complete

    # Create ddates in YYYYMMDD format
    ddates = dd.read_parquet(daily_crsp_path + 'crsp_dsf*.parquet', columns='date').unique()
    ddates = dd.to_datetime(ddates)
    ddates = ddates.dt.strftime('%Y%m%d').astype(int).values.flatten()
    ddates = ddates.compute()

    # Create the end of month flag and store ddates
    yyyy_mm = np.floor(ddates / 100).astype(int)
    eomflag = yyyy_mm != np.roll(yyyy_mm, -1)
    eomflag[-1] = True

    ddates_csv = pd.DataFrame(ddates)
    ddates_csv.to_csv(daily_crsp_path + 'ddates.csv')

    eomflag_csv = pd.DataFrame(eomflag)
    eomflag_csv.to_csv(daily_crsp_path + 'eomflag.csv')

    print(f"Daily data processing completed at {datetime.now()}.\n")

    return


if __name__ == "__main__":
    from AssayingAnomalies import Config
    configure = Config()
    params = configure.load_params()
    makeCRSPDailyData(params)

