import pandas as pd
import os
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
from AssayingAnomalies import Config


def calculate_ivol_for_permno(permno: str, window_size: int, model: str):
    print(f"\nNow calculating ivol for {permno}.")

    # Load stored parameters
    params = Config()
    params = params.load_params()

    # Set the minimum number of observations in a period to 1/10 of total trading days.
    min_obs = int(window_size * 0.9 // 1)

    # Load the daily returns for the given permno
    dret = pd.read_parquet(os.path.join(params.daily_crsp_folder, 'dret.parquet'),
                           columns=[permno]).sort_index().astype(float)
    dret.index = pd.to_datetime(dret.index, format='%Y%m%d')

    # Load the daily FF data we will need.
    if model.strip().lower() == 'ff3':
        dff = pd.read_csv(os.path.join(params.ff_data_folder, 'dff.csv'), index_col=0,
                          usecols=['dates', 'rf', 'mkt', 'smb', 'hml']).sort_values(by='dates').astype(float)
    else:
        dff = pd.read_csv(os.path.join(params.ff_data_folder, 'dff.csv'), index_col=0,
                          usecols=['dates', 'rf', 'mkt']).sort_values(by='dates').astype(float)
    # Set index to datetime for easier handling.
    dff.index = pd.to_datetime(dff.index, format='%Y%m%d')

    # Extract the individual series we will need and calculate market risk premium.
    dxret = pd.Series(dret.values.flatten(), index=dret.index) - dff['rf']

    # Create the "endogeneous" variable by dropping any missing values.
    endogeneous = dxret.dropna(how='any')

    if model.strip().lower() == 'ff3':
        exogeneous = dff[['mkt', 'smb', 'hml']].loc[endogeneous.index]
    else:
        exogeneous = dff['mkt'].loc[endogeneous.index]

    exogeneous = sm.add_constant(exogeneous)  # Add a constant

    # Estimate the model
    results = RollingOLS(endogeneous, exogeneous, window=window_size, min_nobs=min_obs).fit()

    # Calculate IVOL
    # Mse_total is the total sum of squares divided by the number of observations. Then ivol for month i is calculated
    # as the average of the sum of daily squared residuals in month i.
    ivol = results.mse_total.resample('ME').mean()

    print(f"\nFinished calculating ivol for {permno}.")
    return ivol
