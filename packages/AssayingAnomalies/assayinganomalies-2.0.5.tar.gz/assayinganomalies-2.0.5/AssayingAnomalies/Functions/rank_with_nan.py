import pandas as pd
import numpy as np
from scipy.stats import rankdata

def rank_with_nan(data):
    if isinstance(data, pd.DataFrame):
        data = data.to_numpy()

    # Create a copy of the data to avoid modifying the original array
    data_copy = np.array(data, copy=True)

    # Find the NaN elements
    nan_mask = np.isnan(data_copy)

    # Temporarily replace NaNs with a placeholder (max value + 1)
    max_val = np.nanmax(data_copy)
    data_copy[nan_mask] = max_val + 1

    # Rank the data
    ranks = rankdata(data_copy, axis=1)

    # Replace the placeholder ranks with NaN
    ranks[nan_mask] = np.nan

    return ranks