import pandas as pd
import numpy as np
import os
from .rank_with_nan import rank_with_nan


# def fill_missing_tcosts(params, tcosts):
#
#     # Set path
#     crsp_path = params.crspFolder + os.sep
#
#     # Load variabled we need
#     me = pd.read_csv(crsp_path + 'me.csv', index_col=0).astype(float)
#     rme = rank_with_nan(me)
#
#     IffVOL3 = pd.read_parquet(crsp_path + 'IffVOL3.parquet')
#     rIVOL = rank_with_nan(IffVOL3)
#
#     # Iterate over each date
#     for date in range(rme.shape[0]):
#         # Get the ranks for me and IVOL for this date
#         rme_row = rme[date]
#         rIVOL_row = rIVOL[date]
#
#         # Calculate the differences in ranks for each pair of stocks
#         # The result is a DataFrame where each cell [i, j] is the difference in rank between stock i and stock j
#         rme_diff = rme_row[:, np.newaxis] - rme_row
#         rIVOL_diff = rIVOL_row[:, np.newaxis] - rIVOL_row
#
#         # Calculate Euclidean distance
#         euclidean_distance = np.sqrt(rme_diff ** 2 + rIVOL_diff ** 2)
#
#         # Fill diagonals with np.inf to avoid self-matching
#         np.fill_diagonal(euclidean_distance, np.inf)
#
#         # Replace nan values with np.inf in the euclidean_distance array
#         euclidean_distance[np.isnan(euclidean_distance)] = np.inf
#
#         # Closes matches
#         min_indices = np.argmin(euclidean_distance, axis=1)
#
#         # Select NaN values in tcosts_raw for this date
#         mask = tcosts.iloc[date].isna()
#
#         # Update NaN values using values from the closest match
#         tcosts.iloc[date, mask] = tcosts.iloc[date, min_indices[mask]].values
#
#     return tcosts

def fill_missing_tcosts(raw_tcosts, rIVOL, rme):
    """
    Fills missing transaction costs ('tcosts') for stocks on each date by assigning
    the 'tcosts' from their closest match based on Euclidean distances calculated
    from market equity ('rme') and idiosyncratic volatility ('rIVOL').

    This function iterates over each date, identifies stocks with valid 'rme' and
    'rIVOL' values, computes Euclidean distances among these stocks, and updates
    'tcosts' for stocks with missing values using the 'tcosts' of their closest
    valid match.

    Parameters:
    - raw_tcosts (pd.DataFrame): A DataFrame containing transaction costs ('tcosts')
      for stocks across different dates. Rows represent dates, and columns represent
      individual stocks.
    - rIVOL (np.ndarray): A NumPy array containing idiosyncratic volatility values
      for stocks, structured similarly to 'raw_tcosts'.
    - rme (np.ndarray): A NumPy array containing market equity ('rme') values for
      stocks, structured similarly to 'raw_tcosts'.

    Returns:
    - pd.DataFrame: The updated DataFrame with missing 'tcosts' filled in for
      eligible stocks based on their closest matches.

    The function prints updates being made for debugging purposes and includes
    exception handling to report any errors encountered during processing.
    """
    # Iterate over each date
    # for date in range(rme.shape[0])[12:24]:
    for date in range(rme.shape[0]):
        try:
            print(f"Month {date}")

            # Step 1: Filter for valid 'rme' and 'rIVOL' values
            valid_mask = ~np.isnan(rme[date]) & ~np.isnan(rIVOL[date])
            valid_indices = np.where(valid_mask)[0]

            # Step 2: Compute Euclidean distances among valid stocks
            rme_valid = rme[date][valid_mask]
            rIVOL_valid = rIVOL[date][valid_mask]
            rIVOL_diff = rIVOL_valid[:, np.newaxis] - rIVOL_valid
            rme_diff = rme_valid[:, np.newaxis] - rme_valid
            euclidean_distance = np.sqrt(rIVOL_diff ** 2 + rme_diff ** 2)
            np.fill_diagonal(euclidean_distance, np.inf)

            # Step 3: Identify indices to update in 'tcosts'
            # These are indices that are both in 'valid_indices' and have 'NaN' in 'tcosts'
            nan_mask = np.isnan(raw_tcosts.iloc[date].to_numpy())
            indices_to_update = valid_indices[nan_mask[valid_indices]]

            # Step 4: Find closest matches for stocks eligible for update
            min_indices = np.argmin(euclidean_distance, axis=1)
            closest_indices = valid_indices[min_indices]

            # Step 5: Update 'tcosts' for eligible stocks with their closest match's 'tcosts'
            for idx in indices_to_update:
                pos_in_valid_indices = np.where(valid_indices == idx)[0][0]
                closest_idx = closest_indices[pos_in_valid_indices]
                old_value = raw_tcosts.iloc[date, idx]
                update_value = raw_tcosts.iloc[date, closest_idx]
                if not np.isnan(update_value):
                    print(f"Updating {idx}:{old_value} with {closest_idx}:{update_value}")
                    raw_tcosts.iloc[date, idx] = update_value

        except Exception as e:
            print(f"Error processing: {e}")

    return raw_tcosts
