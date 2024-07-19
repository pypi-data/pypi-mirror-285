import numpy
import pandas as pd
import numpy as np


def fill_months(data, annual_or_quarterly='quarterly'):

    if annual_or_quarterly.lower() == 'annual':
        persist = 11
    else:
        persist = 2

    if isinstance(data, np.ndarray):
        data = pd.DataFrame(data)

    filled_data = data.copy()
    n_dates = len(data)

    # Create a boolean mask for the data
    mask = data.notna()

    # Forward fill the data, limited by the persistence period
    for shift in range(1, persist + 1):
        shifted_mask = mask.shift(shift, fill_value=False)
        filled_data[shifted_mask] = filled_data.ffill(limit=shift)

    return filled_data


# # Sample Data
# data = pd.DataFrame({
#     'Q1': [1, np.nan, np.nan, np.nan, 5, np.nan, np.nan, np.nan, 9, np.nan, np.nan, np.nan],
#     'Q2': [np.nan, 2, np.nan, np.nan, np.nan, 6, np.nan, np.nan, np.nan, 10, np.nan, np.nan],
# })
#
# filled_data = fill_months(data)
