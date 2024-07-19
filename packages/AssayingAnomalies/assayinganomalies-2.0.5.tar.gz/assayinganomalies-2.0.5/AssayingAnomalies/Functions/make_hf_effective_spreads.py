import pandas as pd
import numpy as np
import os
from datetime import datetime

from AssayingAnomalies.wrds_utilities.utilities import ssh_login, start_qrsh, start_python_wrds, exit_sessions,\
    execute_commands, transfer_files, delete_files


def get_hf_spreads_data(params, **kwargs):
    print(f"Now retrieving HF effective spreads data. Run started at {datetime.now()}")

    # Default keyword arguments
    p = {
        "delete_files_ok": True
    }

    # Update keyword arguments with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Define the columns to pull from WRDS columns_to_pull = ['SYM_ROOT', 'SYM_SUFFIX', 'symbol', 'DATE',
    # 'quotedspread_percent_tw', 'effectivespread_percent_dw']  # The Chen-Velikov SAS code pulls these measures (and
    # others) but the Assaying anomalies package only uses the effective spreads, not quoted spreads.
    columns_to_pull = ['SYM_ROOT', 'SYM_SUFFIX', 'symbol', 'DATE', 'effectivespread_percent_dw']

    # Start a new child process, and connect to the SSH server
    child = ssh_login(params)

    # Start a qrsh session
    start_qrsh(params, child)

    # Start Python session
    start_python_wrds(child)

    # Create the save_file names and execute commands.
    date_range = np.unique(np.linspace(max(params.sample_start, 2003), params.sample_end, max(params.sample_end, 2003) - params.sample_start + 1).astype(int))
    commands = []
    file_locations = []
    for year in date_range:
        save_name = 'spreads_'
        sql_string = "SELECT " + ", ".join(columns_to_pull) + f" FROM taqmsec.wrds_iid_{year}"
        command1 = f"testing = db.raw_sql(\"{sql_string}\")"
        file_name = f"{save_name}{year}.csv"
        command2 = f"testing.to_csv(\"/scratch/rochester/{file_name}\")"
        commands.extend([command1, command2])
        file_location = f'/scratch/rochester/{file_name}'
        file_locations.append(file_location)

    # Execute python commands on wrds cloud
    execute_commands(child, commands)

    # Exit all sessions
    exit_sessions(child)

    # Transfer the files and return a list of files that did not transfer
    print("Using SFTP to transfer files.")
    save_folder = params.hf_effective_spreads_folder
    problem_files = transfer_files(params, file_locations, save_folder)

    # Delete the files
    if p['delete_files_ok']:
        delete_files(params, file_locations, problem_files)

    # Print statement indicating if all files were completely transferred or not.
    if problem_files:
        print("The following files did not transfer: ")
        for file in problem_files:
            print(file)
    else:
        print("All files were successfully transferred and deleted from WRDS storage.")

    print(f"Finished retrieving HF effective spreads data. Run ended at {datetime.now()}")
    return


def make_hf_effective_spreads(params):
    print(f"Now making HF effective spreads. Run started at {datetime.now()}")

    hf_path = params.hf_effective_spreads_folder + os.sep
    crsp_path = params.crspFolder + os.sep

    # Initialize dataframes
    hf_spreads_ave = pd.DataFrame()
    hf_spreads_last = pd.DataFrame()

    # Load some variables
    msenames = pd.read_csv(crsp_path + 'crsp_stocknames.csv', index_col=0)
    ret = pd.read_csv(params.crspFolder + os.sep + 'ret.csv', index_col=0).astype(float)

    date_range = [i for i in range(max(params.sample_start, 2003), params.sample_end+1)]
    for year in date_range:
        data = pd.read_csv(hf_path + f'spreads_{year}.csv', index_col=0)
        # q_spread = pd.pivot(data, columns='symbol', index='date', values='quotedspread_percent_tw')
        e_spread = pd.pivot(data, columns='symbol', index='date', values='effectivespread_percent_dw')
        e_spread.index = pd.to_datetime(e_spread.index, format='%Y-%m-%d')

        # Setting index to datetime
        e_spread_ave = e_spread.resample('M').mean()
        e_spread_last = e_spread.resample('M').last()

        # Create a mapping from tickers to permno.
        ticker_to_permno = msenames.set_index('ticker')['permno'].to_dict()

        # Identify columns in e_spread that have a corresponding mapping in msenames
        mapped_columns = [col for col in e_spread_ave.columns if col in ticker_to_permno]

        # Restrict e_spread to these columns
        e_spread_ave = e_spread_ave[mapped_columns]
        e_spread_last = e_spread_last[mapped_columns]

        # Map the column names to permno if needed
        e_spread_ave.columns = [ticker_to_permno[col] for col in e_spread_ave.columns]
        e_spread_last.columns = [ticker_to_permno[col] for col in e_spread_last.columns]

        # Convert the columns of e_spread to float
        e_spread_ave.columns = e_spread_ave.columns.astype(str)
        e_spread_last.columns = e_spread_last.columns.astype(str)
        # TODO: change the below portion to .reindex, it is much faster
        # Add NaN columns to e_spread for any columns in ret that are not in e_spread
        for col in ret.columns:
            if col not in e_spread_ave.columns:
                e_spread_ave[col] = np.nan
            if col not in e_spread_last:
                e_spread_last[col] = np.nan

        # Remove duplicates by keepiing the first occurence. Copying Zhen and Velikov here
        e_spread_ave = e_spread_ave.iloc[:, ~e_spread_ave.columns.duplicated(keep='first')]
        e_spread_last = e_spread_last.iloc[:, ~e_spread_last.columns.duplicated(keep='first')]
        e_spread_ave = e_spread_ave[np.intersect1d(ret.columns, e_spread_ave.columns)]
        e_spread_last = e_spread_last[np.intersect1d(ret.columns, e_spread_last.columns)]

        # Append
        hf_spreads_ave = hf_spreads_ave.append(e_spread_ave)
        hf_spreads_last = hf_spreads_last.append(e_spread_last)

    # Save dataframes
    hf_spreads_ave.to_csv(hf_path + 'hf_spreads_ave_post_2003.csv')
    hf_spreads_last.to_csv(hf_path + 'hf_spreads_last_post_2003.csv')

    print(f"Finished making HF effective spreads. Run ended at {datetime.now()}")

    return


def extend_hf_effective_spreads(params):
    print(f"Extending HF effective spreads to pre-2003. Run started at {datetime.now()}")
    hf_path = params.hf_effective_spreads_folder + os.sep
    if params.sample_start <= 2003:
        # Extend using the csv created after running the HF Effective Spreads SAS code.
        pre_2003 = pd.read_csv(hf_path + 'hf_monthly_pre_2003.csv', low_memory=False)
        pre_2003 = pd.pivot(pre_2003, columns='permno', values='espread_pct_mean', index='yearm')
        pre_2003.columns = pre_2003.columns.astype(str)
        pre_2003.index = pd.to_datetime(pre_2003.index, format='%Y%m')
        pre_2003.index = pre_2003.index.to_period('M')

        # Load and filter data from make_hf_effective_spreads
        post_2003 = pd.read_csv(hf_path + 'hf_spreads_ave_post_2003.csv', index_col=0)
        post_2003.index = pd.to_datetime(post_2003.index)
        post_2003.index = post_2003.index.to_period('M')
        post_2003 = post_2003[post_2003.index >= pd.Period('2004-01')]

        # Make sure the pre_2003 data has the same columns as the post_2003 df
        pre_2003 = pre_2003.reindex(columns=post_2003.columns, fill_value=np.nan)
        pre_2003 = pre_2003 / 100

        # Select rows before 2003
        start_date = pd.Period(str(params.sample_start) + '-01')
        end_date = pd.Period(str(min(2003, params.sample_end)) + '-12')
        pre_2003 = pre_2003.loc[(start_date <= pre_2003.index) & (pre_2003.index <= end_date)]

        # Combine the dataframes.
        combined_df = pd.concat([pre_2003, post_2003])

        # Save the dataframe
        combined_df.to_csv(hf_path + 'hf_monthly.csv')

        print(f"Finished extending hf-effective spreads to pre-2003. Run ended at {datetime.now()}")

        return combined_df

    else:
        # Load and filter data from make_hf_effective_spreads
        post_2003 = pd.read_csv(hf_path + 'hf_spreads_ave_post_2003.csv', index_col=0)
        post_2003.index = pd.to_datetime(post_2003.index)
        post_2003.index = post_2003.index.to_period('M')
        post_2003 = post_2003[post_2003.index >= pd.Period('2004-01')]

        print(f"Finished extending hf-effective spreads to pre-2003. Run ended at {datetime.now()}")

        return post_2003


# get_hf_spreads_data(params)
# make_hf_effective_spreads(params)
# extend_hf_effective_spreads(params)
