import pandas as pd
import os


def makeGibbs(params, file_path):
    """
    This function processes and manipulates financial data to create a 'Gibbs' matrix. It reads in stored estimates from
     a given file path, cleans the data, and computes yearly averages for each 'permno' and 'year' combination. The
     function also merges this data with a CRSP link table, reshapes it, and then performs a final transformation by
     multiplying the values by 2.

    Parameters:
    ----------
    params : object
        An object containing attributes related to data paths:
        - crspFolder: str
            The file path to the CRSP data folder.
    file_path : str
        The file path to the CSV file containing the estimates to be processed.

    Process:
    --------
    1. Read and clean the input data from 'file_path'.
    2. Calculate yearly averages for each 'permno' and 'year'.
    3. Merge with the CRSP link table.
    4. Reshape the merged data into a Gibbs matrix.
    5. Multiply the matrix by 2.

    Returns:
    -------
    gibbs : numpy.ndarray
        A numpy array representing the Gibbs matrix, which contains the processed and transformed data.

    Notes:
    ------
    - The input file should contain columns 'permno', 'year', and 'c'.
    - The Gibbs matrix is derived by merging CRSP link data and averaging over years, then reshaping and scaling.
    """

    # set path to crsp folder
    crsp_path = params.crspFolder + os.sep

    # read in the stored estimates
    # data = pd.read_csv(crsp_path + filename, index_col=0)
    # data = data[['permno', 'year', 'c']]
    data = pd.read_csv(file_path, usecols=['permno', 'year', 'c'])

    # Clean them up:
    data = data.dropna(subset=['c'])

    # The Gibbs file is monthly so in some years there is more than one estimate. We will take the yearly average.
    # First group by 'permno' and 'year' and if there are multiple entries then take the average of them. The
    # 'reset_index()' call is used to convert the indices created by 'groupby() back into columns, which makes the
    # DataFrame look more like a regular table.'
    data = data.groupby(['permno', 'year']).mean().reset_index()
    data[['permno', 'year']] = data[['permno', 'year']].astype(int)

    # Load the CRSP link table
    crsp_link = pd.read_csv(crsp_path + 'crsp_link.csv', index_col=0)

    # Create a year variable
    crsp_link['date'] = crsp_link['date'].str.replace('-', '').astype(int)
    crsp_link['year'] = crsp_link['date'].astype(int) // 10000
    crsp_link['year'] = crsp_link['year'].astype('int64')  # this solved ValueError: Buffer dtype mismatch, expected
    # 'const int64_t' but got 'int'

    # Merge the data
    # Ensure the key columns ('permno', 'year' in this case) are of the same data type in both DataFrames
    mergedData = pd.merge(crsp_link, data, how='left', on=['permno', 'year'])

    # Reshape the data using unstack
    # This step might need adjustment based on the structure of your 'mergedData' and what you want to achieve with 'unstack'
    gibbs = mergedData.pivot(index='date', columns='permno', values='c')

    # Convert the DataFrame to a numpy array and transpose it if necessary
    gibbs = gibbs.to_numpy()

    # Multiply by 2
    gibbs *= 2

    return pd.DataFrame(gibbs)
