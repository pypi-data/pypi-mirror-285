import pandas as pd
import numpy as np
import os
import glob
from datetime import datetime
import AssayingAnomalies

def makeCorwinSchultz():
    """
    This function estimates bid-ask spreads using the Corwin-Schultz estimator, a methodology that infers the bid-ask
    spread from daily high and low prices. It applies adjustments for negative prices and overnight price changes and
    computes variables such as lclose, pchg, lhi, llo, beta, gamma, alpha, and the final spread estimate 's'. It sets
    negative spread estimates to zero and computes monthly averages of the high-low spread estimate.

    Parameters:
    ----------
    params : object
        An object containing the following attributes:
        - crspFolder: str
            The file path to the CRSP data folder.
        - daily_crsp_folder: str
            The file path to the daily CRSP data folder.

    Returns:
    -------
    res : pd.DataFrame
        A DataFrame containing the monthly average of the high-low spread estimate for each stock.

    References:
    -----------
    1. Corwin, S. and P. Schultz, 2012, A simple way to estimate bid-ask spreads from daily high and low prices,
    Journal of Finance.
    2. Chen, A. and M. Velikov, 2021, Zeroing in on the expected return on anomalies, Journal of Financial and
    Quantitative Analysis (JFQA).
    3. Novy-Marx, R. and M. Velikov, 2023, Assaying Anomalies, working paper.
    """
    print(f"Making Corwin Schultz (2012) bid-ask spread estimates. Run started at {datetime.now()}")

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
    # dcfacpr = pd.read_csv(daily_crsp_path + 'dcfacpr.csv', index_col=0).astype(float)
    # ret = pd.read_csv(crsp_path + 'ret.csv', index_col=0).astype(float)
    dates = pd.read_csv(crsp_path + 'dates.csv', index_col=0).astype(int)
    dbidlo = pd.read_parquet(daily_crsp_path + 'dbidlo.parquet').astype(float)
    daskhi = pd.read_parquet(daily_crsp_path + 'daskhi.parquet').astype(float)
    dprc = pd.read_parquet(daily_crsp_path + 'dprc.parquet').astype(float)
    dcfacpr = pd.read_parquet(daily_crsp_path + 'dcfacpr.parquet').astype(float)
    permno = pd.read_csv(crsp_path + 'permno.csv', index_col=0).astype(float)

    # If the price was ever negative, replace the hi and low values with np.nan
    daskhi[dprc < 0] = np.nan
    dbidlo[dprc < 0] = np.nan

    # Take the absolute value of daily prices
    dprc = dprc.abs()

    # Compute lclose
    lclose = np.divide(np.multiply(dprc.shift(1).fillna(np.nan), dcfacpr), dcfacpr.shift(1).fillna(np.nan))
    # Page 726: "If the day t+1 low is above the day t close, we assume that the price rose overnight from the close to
    # the day t + 1 low and decrease both the high and low for day t + 1 by the amount of the overnight change when
    # calculating spreads. Similarly, if the day t+1 high is below the day t close, we assume the price fell overnight
    # from the close to the day t + 1 high and increase the day t + 1 high and low prices by the amount of this
    # overnight decrease."

    # Initialize pchg as a DataFrame of zeros with the same size as dprc
    pchg = pd.DataFrame(np.zeros_like(dprc.values), index=dprc.index, columns=dprc.columns)

    # Calculate overnight change
    condition_dbidlo = (dbidlo > lclose).values
    condition_daskhi = (daskhi < lclose).values
    pchg.values[condition_dbidlo] = (dbidlo - lclose).values[condition_dbidlo]
    pchg.values[condition_daskhi] = (daskhi - lclose).values[condition_daskhi]

    # Adjust hi and lo
    dbidlo -= pchg
    daskhi -= pchg

    # Compute lhi and llo
    lhi = np.divide(np.multiply(daskhi.shift(1).fillna(np.nan), dcfacpr), dcfacpr.shift(1).fillna(np.nan))
    llo = np.divide(np.multiply(dbidlo.shift(1).fillna(np.nan), dcfacpr), dcfacpr.shift(1).fillna(np.nan))

    #=================================================================================================================#
    #============================================== Acual spread estimation ==========================================#
    #=================================================================================================================#

    # Calculate beta
    beta = (np.log(daskhi / dbidlo)) ** 2 + (np.log(lhi / llo)) ** 2

    # NaN assignment for beta
    beta[(daskhi <= 0) | (dbidlo <= 0)] = np.nan

    # Calculate gamma
    gamma = (np.log(np.maximum(daskhi, lhi) / np.minimum(dbidlo, llo))) ** 2

    # NaN assignment for gamma
    gamma[np.minimum(dbidlo, llo) <= 0] = np.nan

    # Define the constant
    const = 3 - 2 * np.sqrt(2)

    # Calculate alpha according to Equation (18)
    alpha = (np.sqrt(2 * beta) - np.sqrt(beta)) / const - np.sqrt(gamma / const)

    # Calculate s according to Equation (14)
    s = 2 * (np.exp(alpha) - 1) / (1 + np.exp(alpha))
    #==================================================================================================================
    # Section II.C
    #==================================================================================================================
    # Page 727: "The high-low estimator assumes that the expectation of a stock's true variance over a 2-day period is
    # twice as large as the expectation of the variance over a single day. Even if this is true in expectation, the
    # observed 2-day variance may be more than twice as large as the single-day variance during volatile periods, in
    # cases with a large overnight price change, or when the total return over the 2-day period is large relative to the
    # intraday volatility. If the observed 2-day variance is large enough, the high-low spread estimate will be
    # negative. For most of the analysis to follow, we set all negative 2-day spreads to zero before calculating monthly
    # averages.

    # Set negative values in s to 0
    s[s < 0] = 0

    # Initialize hl with NaNs and determine the number of months
    # hl = pd.DataFrame(np.nan, index=dates.values.flatten(), columns=s.columns)
    # nMonths = len(dates)
    "The commented out section below closely follows the Matlab procedure but is very slow. The .resample() method is" \
    "MUCH faster."
    #
    # # Loop through the months
    # for i in range(nMonths):
    #     print(i)
    #     # Find indices for the current month
    #     ind = (ddates // 100 == dates.iloc[i])
    #     print('a')
    #     # Determine columns with at least 12 finite values
    #     hor_index = s[ind].count() >= 12
    #     print('b')
    #     # Calculate mean for these columns
    #     hl.iloc[i, hor_index] = s[ind].mean()
    #     print('c')
    # # Remove any imaginary numbers (if any)
    # hl = hl.apply(np.real)
    #
    # # Convert ddatest to a monthly format for grouping
    # ddates_monthly = ddates // 100
    #
    # # Perform operations for each month
    # for count, date in enumerate(hl.index):
    #     print(count)
    #     # Filter data for the current month
    #     monthly_data = s[ddates_monthly == date]
    #
    #     # Check if there are at least 12 finite values in each column
    #     valid_columns = monthly_data.count() >= 12
    #
    #     # Calculate mean for valid columns
    #     hl.loc[date, valid_columns] = monthly_data.mean()
    s.index = ddates.values.flatten()
    s.index = pd.to_datetime(s.index, format='%Y%m%d')
    hl = s.resample('M').mean()

    print(f"Finished making Corwin Schultz (2012) bid-ask spread estimates at {datetime.now()}")

    return hl
