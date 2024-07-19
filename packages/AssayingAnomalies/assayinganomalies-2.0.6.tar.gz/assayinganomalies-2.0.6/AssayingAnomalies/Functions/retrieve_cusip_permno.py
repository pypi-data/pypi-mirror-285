import os
import pandas as pd

def retrieve_cusip_permno(cusip_or_permno, params):

    path_crsp = params.crspFolder
    df = pd.read_csv(os.path.join(path_crsp, 'crsp_msfhdr.csv'), usecols=['permno', 'cusip'])

    # First transform entry to a string to do len comparison.
    if isinstance(cusip_or_permno, int):
        cusip_or_permno = str(cusip_or_permno)

    # See if the user entered a PERMNO or a CUSIP and then perform the search
    if len(cusip_or_permno) < 8:
        permno = int(float(cusip_or_permno))
        search_column = 'permno'
        # Perform the search
        result = df[df[search_column] == permno]
    else:
        cusip = cusip_or_permno
        search_column = 'cusip'
        # Perform the search
        result = df[df[search_column] == cusip]

    if result.empty:
        return f"No records found for {search_column}: {cusip_or_permno}"
    else:
        # Returning the first matching record if multiple entries exist
        return result[['permno', 'cusip']].iloc[0].to_dict()
