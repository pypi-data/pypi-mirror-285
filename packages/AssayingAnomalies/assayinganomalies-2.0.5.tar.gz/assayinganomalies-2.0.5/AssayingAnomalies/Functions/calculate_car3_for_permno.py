import pandas as pd
import os
from AssayingAnomalies import Config


def calculate_car3_for_permno(permno: str):
    # Load stored parameters
    params = Config()
    params = params.load_params()

    # load variables
    dff = pd.read_csv(os.path.join(params.ff_data_folder, 'dff.csv'), index_col=0,
                      usecols=['dates', 'rf', 'mkt']).sort_values(by='dates').astype(float)
    # Set index to datetime for easier handling.
    dff.index = pd.to_datetime(dff.index, format='%Y%m%d')

    # Load the daily returns for the given permno
    dret = pd.read_parquet(os.path.join(params.daily_crsp_folder, 'dret.parquet'),
                           columns=[permno]).sort_index().astype(float)
    dret.index = pd.to_datetime(dret.index, format='%Y%m%d')

    # Calculate the abnormal return.
    d_abnormal_ret = pd.Series(dret.values.flatten(), index=dret.index) - dff['rf'] - dff['mkt']

    # Load the monthly dataframe that contains the announcement date and for a given permno.
    rdq = pd.read_csv(params.compFolder + os.sep + 'RDQ.csv', index_col=0, usecols=['dates', permno]).dropna()
    rdq.index = pd.to_datetime(rdq.index, format='%Y%m')

    car3_results = pd.Series(index=dret.index)
    for date in rdq[permno]:
        # Convert float date to datetime object
        announcement_date = pd.to_datetime(str(int(date)), format='%Y%m%d')
        day_2 = d_abnormal_ret.index.get_loc(announcement_date)
        returns = d_abnormal_ret.iloc[day_2-1:day_2+2]
        car3 = (returns + 1).cumprod() - 1
        car3_results.loc[car3.index[0]] = car3.iloc[-1]

    # Identify last active date for the permno
    last_active_date = dret.last_valid_index()

    # Limit forward fill to last active date
    car3_results = car3_results.ffill().loc[:last_active_date]

    # Resample to monthly data
    car3_monthly = car3_results.resample('ME').last()

    return car3_monthly
