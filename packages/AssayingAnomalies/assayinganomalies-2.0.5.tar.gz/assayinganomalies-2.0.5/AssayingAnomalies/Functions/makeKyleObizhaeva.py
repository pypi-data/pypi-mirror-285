import numpy as np
import pandas as pd
import os
import glob
import AssayingAnomalies
from datetime import datetime
from AssayingAnomalies.Functions.getFredData import getFredData


def makeKyleObizhaeva():
    """
    Calculate the monthly Volume over Volatility (VoV) measure for stocks.

    This function computes the VoV based on daily volume and return data.
    It also adjusts the volume data using Consumer Price Index (CPI) for inflation.
    The function filters out the stocks that do not meet the criteria of having
    at least 11 days with non-zero returns and 5 days with positive volume in a month.

    Parameters:
    params (object): An object containing various parameters including paths to
                     the CRSP data folder and other required data.

    Returns:
    pd.DataFrame: A DataFrame containing the monthly VoV measures for each stock.
                  The rows represent months, and the columns represent stocks.
                  Stocks that do not meet the criteria within a month are replaced with NaN.

    Note:
    The function requires the following data files in the specified paths:
    - Daily volume ('dvol.csv')
    - Daily returns ('dret.csv')
    - Daily dates ('ddates.csv')
    - Monthly dates ('dates.csv')
    - Daily prices ('dprc.csv')
    Additionally, it pulls the CPI data from the FRED database for inflation adjustment.
    """

    print(f"Started making Kyle Obizhaeva volume over volatility measure of trading costs. Run began at {datetime.now()}")

    cwd = os.getcwd()
    search_pattern = os.path.join(cwd, '**', 'config.json')
    params_path = glob.glob(search_pattern, recursive=True)[0]
    # print(params_path)
    params = AssayingAnomalies.Config.load_params(params_path)

    crsp_path = params.crspFolder + os.sep
    daily_crsp_path = params.daily_crsp_folder + os.sep

    # Load the necessary variables
    # dvol = pd.read_csv(daily_crsp_path + 'dvol.csv', index_col=0).astype(float)
    # dret = pd.read_csv(daily_crsp_path + 'dret.csv', index_col=0).astype(float)
    dvol = pd.read_parquet(daily_crsp_path + 'dvol.parquet').astype(float)
    dret = pd.read_parquet(daily_crsp_path + 'dret.parquet').astype(float)
    dates = pd.read_csv(crsp_path + 'dates.csv', index_col=0).astype(int)
    # dprc = pd.read_csv(daily_crsp_path + 'dprc.csv', index_col=0).astype(float)
    dprc = pd.read_parquet(daily_crsp_path + 'dprc.parquet').astype(float)

    # Store the constants
    a = 8
    b = 2 / 3
    c = 1 / 3

    # Get dollar volume
    dvol = np.multiply(dvol, np.abs(dprc))

    # Convert 'dvol' and 'dret' indices to datetime
    dret.index = pd.to_datetime(dret.index, format='%Y-%m-%d')
    dvol.index = pd.to_datetime(dvol.index, format='%Y-%m-%d')

    # Pull the inflation series from FRED
    # Get the end date
    finalYear = dates.values.flatten()[-1] // 100
    endDate = str(finalYear) + '-12-31'

    # Pull the CPIAUCNS series from FRED
    fredStruct = getFredData('CPIAUCNS', observation_end=endDate, units='lin', frequency='m', aggregation_method='eop')

    # Use FHT's (2018) normailization
    cpi = pd.DataFrame(fredStruct['value'])
    cpi = cpi / cpi.loc['2000-01-01']

    # Match the dates
    match_dates = pd.to_datetime(dates.values.flatten(), format="%Y%m")
    cpi = cpi.reindex(index=match_dates, fill_value=np.nan)

    # Group by month and calculate standard deviation of daily returns
    monthly_std_dev = dret.resample('M').std()

    # Group by month and calculate the average volume but deflate it according to cpi
    monthly_avg = dvol.resample('M').mean() / np.tile(cpi, len(dret.columns))

    # Create the numerator and denominator
    num = a * monthly_std_dev**b
    den = monthly_avg**c

    # Calculate VoV and set the datetime index
    vov = num / den
    vov.index = cpi.index

    # Create a helper function to check for at least 11 days with non-zero returns and 5 days with positive volume
    def check_applicable_days(group):
        # Criteria for valid days
        valid_volume_days = (group['dvol'] > 0).sum() >= 5
        valid_return_days = (group['dret'].abs() > 0).sum() >= 11

        # Check if each stock meets both criteria
        valid_stocks = valid_volume_days & valid_return_days
        return valid_stocks

    # Combine dvol and dret into a single DataFrame for easy processing
    combined_data = pd.concat([dvol, dret], keys=['dvol', 'dret'], axis=1)
    combined_data.index = dvol.index

    # Group by month and apply the function
    monthly_valid_stocks = combined_data.groupby(pd.Grouper(freq='M')).apply(check_applicable_days)

    # Ensure the indices and columns are aligned with vov
    monthly_valid_stocks.index = vov.index

    # Apply Boolean dataframe to the VoV matrix to remove observations that do not meet the criteria
    vov = vov[monthly_valid_stocks]

    print(f"Finished making Kyle Obizhaeva volume over volatility measure of trading costs at {datetime.now()}")

    return vov

