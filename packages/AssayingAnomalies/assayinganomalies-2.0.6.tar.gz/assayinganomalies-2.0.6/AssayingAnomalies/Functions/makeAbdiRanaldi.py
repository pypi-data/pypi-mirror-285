import numpy as np
import pandas as pd
import os
import glob
import AssayingAnomalies
from datetime import datetime

def makeAbdiRanaldi():
    print(f"Making Abdi Ranaldi trading costs. Run began at {datetime.now()}")
    cwd = os.getcwd()
    search_pattern = os.path.join(cwd, '**', 'config.json')
    params_path = glob.glob(search_pattern, recursive=True)[0]
    # print(params_path)
    params = AssayingAnomalies.Config.load_params(params_path)
    crsp_path = params.crspFolder + os.sep
    daily_crsp_path = params.daily_crsp_folder + os.sep

    # Load the necessary variables
    # dbidlo = pd.read_csv(daily_crsp_path + 'dbidlo.csv', index_col=0).astype(float)
    # daskhi = pd.read_csv(daily_crsp_path + 'daskhi.csv', index_col=0).astype(float)
    ddates = pd.read_csv(daily_crsp_path + 'ddates.csv', index_col=0).astype(int)
    # dprc = pd.read_csv(daily_crsp_path + 'dprc.csv', index_col=0).astype(float)
    dbidlo = pd.read_parquet(daily_crsp_path + 'dbidlo.parquet').astype(float)
    daskhi = pd.read_parquet(daily_crsp_path + 'daskhi.parquet').astype(float)
    dprc = pd.read_parquet(daily_crsp_path + 'dprc.parquet').astype(float)
    dcfacpr = pd.read_parquet(daily_crsp_path + 'dcfacpr.parquet').astype(float)
    ret = pd.read_csv(crsp_path + 'ret.csv', index_col=0).astype(float)
    permno = pd.read_csv(crsp_path + 'permno.csv', index_col=0).astype(float)

    # Check for missing data
    # Check for missing columns (permnos) and add them with NaN values
    for df in [dcfacpr, dbidlo, daskhi, dprc, dcfacpr]:
        missing_columns = set(permno.values.flatten()) - set(df.columns.astype(float))

        # Iterate over the list of missing columns
        for missing_column_label in missing_columns:
            # Find the correct position to insert the new column
            column_labels = df.columns.astype(float).tolist()
            insert_position = 0
            for i, label in enumerate(column_labels):
                if label > missing_column_label:
                    insert_position = i
                    break

            # Insert the new column with NaN values at the determined position
            new_column = pd.Series(np.nan, index=df.index)
            df.insert(insert_position, missing_column_label, new_column)

    # Create a copy of raw daily price matrix
    dprc_raw = dprc.copy()
    dhigh = dbidlo.copy()
    dlow = daskhi.copy()

    # Set the daily high and low for days when a stock does not trade to np.nan
    dhigh[dprc < 0 | np.isnan(dprc)] = np.nan
    dlow[dprc < 0 | np.isnan(dprc)] = np.nan

    # Mask where the stock didn't trade (dprc < 0 or NaN)
    mask = (dprc_raw < 0) | dprc_raw.isna()

    # Carry over the previous days daily high, low, and close on days when a stock doesn't trade. To achieve this, I
    # forward fill the masked data for dprc, dhigh, and dlow
    dprc.mask(mask).fillna(method='ffill', inplace=True)
    dhigh.mask(mask).fillna(method='ffill', inplace=True)
    dlow.mask(mask).fillna(method='ffill', inplace=True)

    # Take the absolute value of the daily price
    dprc = dprc.abs()

    # Store the midpoints of the low and high for t and tp1 (= t plus one)
    midpoint = (np.log(dlow) + np.log(dhigh)) / 2
    midpoint_tp1 = midpoint.shift(-1)

    # Set the days where the stock does not trade to nan
    dbidlo[dprc_raw < 0 | np.isnan(dprc_raw)] = np.nan
    daskhi[dprc_raw < 0 | np.isnan(dprc_raw)] = np.nan

    # Initiate the close-high-low effective spread measure
    chl = pd.DataFrame(np.nan, index=ddates.values.flatten(), columns=ret.columns)
    chl.index = pd.to_datetime(chl.index, format='%Y%m%d')

    # Calculate the spread
    c_t = np.log(dprc)
    s_hat_t = np.sqrt(np.maximum(4 * (c_t - midpoint) * (c_t - midpoint_tp1), 0))
    s_hat_t[s_hat_t < 0] = 0  # Set negative spreads to 0

    # Set s_hat_t index to datetime
    s_hat_t.index = ddates.values.flatten()
    s_hat_t.index = pd.to_datetime(s_hat_t.index, format='%Y%m%d')

    # Resample and calculate the mean spread for each month
    chl = s_hat_t.resample('M').mean()

    # Define a function to apply to each monthly group
    def check_applicable_days(group):
        criteria = (group['dprc_raw'] > 0) & \
                   group['dprc_raw'].notna() & \
                   group['dbidlo'].notna() & \
                   group['daskhi'].notna() & \
                   (group['daskhi'] - group['dbidlo'] != 0)

        # Count the number of days that meet the criteria for each stock
        valid_days_count = criteria.sum()

        # Check if each stock has at least 12 applicable days
        valid_stocks = valid_days_count >= 12
        return valid_stocks

    # Combine data into a single DataFrame for easy processing
    combined_data = pd.concat([dprc_raw, dbidlo, daskhi], keys=['dprc_raw', 'dbidlo', 'daskhi'], axis=1)
    combined_data.index = s_hat_t.index

    # Group by month and apply the function
    monthly_valid_stocks = combined_data.groupby(pd.Grouper(freq='M')).apply(check_applicable_days)

    chl = chl[monthly_valid_stocks]

    print(f"Finished making Abdi Ranaldi trading costs at {datetime.now()}")

    return chl

# chl = makeAbdiRanaldi(params)
