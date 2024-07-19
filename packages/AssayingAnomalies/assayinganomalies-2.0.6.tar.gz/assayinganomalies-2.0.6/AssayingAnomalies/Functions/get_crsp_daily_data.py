import wrds
import os
from datetime import datetime
import numpy as np


def get_crsp_daily_data(params):

    username = params.username
    crsp_csv_file_path = params.daily_crsp_folder + os.sep

    "Timekeeping"
    print(f"\nNow working on collecting data from CRSP. Run started at {datetime.now()}.\n")

    # Define the columns to pull from WRDS
    columns_to_pull = ['permno', 'date', 'cfacpr', 'cfacshr', 'bidlo', 'askhi', 'prc', 'vol', 'ret', 'bid',
                       'ask', 'shrout', 'openprc', 'numtrd']

    # Set the beginning and ending year
    start = params.sample_start
    end = params.sample_end

    # Manually select years before 2000 based on your intervals
    years_before_2000 = [start, 2000 - 55, 2000 - 25, 2000 - 10]  # 1925, 1970, 1985, 1990

    # Ensure years_before_2000 are within the range and unique
    years_before_2000 = [year for year in years_before_2000 if start <= year < 2000]
    years_before_2000 = sorted(set(years_before_2000))

    # Years from 2000 to end, split into three periods
    if end >= 2000:
        years_2000_to_end = np.linspace(2000, end, 3, endpoint=True).astype(int)
    else:
        years_2000_to_end = []

    # Combine and sort the lists
    years = sorted(set(years_before_2000 + years_2000_to_end.tolist()))
    years[0] = max(years[0], params.sample_start)

    "Establish connection to WRDS"
    db = wrds.Connection(wrds_username=username)
    # Create commands for custom sql query and saving files

    for start, end in zip(years, years[1:]):
        # dsf_file_name = f"crsp_dsf_{end}.csv"
        dsf_file_name = f"crsp_dsf_{end}.parquet"
        dsf_sql_string = "SELECT " + ", ".join(columns_to_pull) + f" FROM CRSP.DSF " \
                f"WHERE date>='01-01-{start}' " \
                f"and date<'01-01-{end+1}' "
        temp = db.raw_sql(dsf_sql_string)
        temp.to_parquet(crsp_csv_file_path + dsf_file_name)

    # Create the delist file names, location, and commands
    delist_file_name = "crsp_dsedelist.csv"
    delist_sql_string = "SELECT * FROM CRSP.DSEDELIST"
    temp = db.raw_sql(delist_sql_string)
    temp.to_csv(crsp_csv_file_path + delist_file_name)

    "Timekeeping"
    print(f"\nFinished collecting daily data from CRSP. Run ended at {datetime.now()}.\n")

    db.close()

    return

