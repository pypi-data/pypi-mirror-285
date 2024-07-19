import requests
import pandas as pd
from datetime import datetime


def getFredData(series_id, observation_start=None, observation_end=None, units=None,
                frequency=None, aggregation_method=None, ondate=None, realtime_end=None):
    """
    Fetches and returns economic data from the FRED (Federal Reserve Economic Data) API.

    This function queries the FRED API to obtain time series data for a specified economic data series.
    It allows for various optional parameters to refine the data query, such as observation start and end dates,
    units, frequency, and aggregation methods. The function returns a pandas DataFrame with the requested data.

    Parameters:
    series_id (str): The FRED series ID for which data is requested.
    observation_start (str, optional): The start date for the data observations (format: 'YYYY-MM-DD').
    observation_end (str, optional): The end date for the data observations (format: 'YYYY-MM-DD').
    units (str, optional): The data value transformations (e.g., 'lin', 'chg', 'ch1', 'pch', 'pc1', 'pca').
    frequency (str, optional): Data frequency ('d', 'w', 'bw', 'm', 'q', 'sa', 'a', 'wef', 'weth', 'wew', 'wetu', 'wem', 'wesu', 'semi', 'wew', 'weq', 'ag').
    aggregation_method (str, optional): Aggregation method used for frequency aggregation ('avg', 'sum', 'eop').
    ondate (str, optional): The date for which the real-time period begins (format: 'YYYY-MM-DD').
    realtime_end (str, optional): The date for which the real-time period ends (format: 'YYYY-MM-DD'). If not provided, 'ondate' will be used.

    Returns:
    pandas.DataFrame: A DataFrame containing the requested time series data. The DataFrame is indexed by date, and
                      contains columns for the date, observation value, and other metadata related to each observation.

    Raises:
    HTTPError: An error is raised if the API request fails.

    Example:
    series_id = 'CPIAUCNS'
    df = getFredData(series_id, observation_start='2000-01-01', observation_end='2020-01-01')
    """

    api_key = '54fa5832fc9d049bff2f59e7f1b4064e'
    api_key_mish = '625723b3573b7c847f626c6df4254c03'
    base_url = 'https://api.stlouisfed.org/fred/series/observations'

    # Construct the query parameters
    query_params = {
        'series_id': series_id,
        'api_key': api_key,
        'file_type': 'json'  # Get data in JSON format
    }
    # Add optional parameters if provided
    if observation_start:
        query_params['observation_start'] = observation_start
    if observation_end:
        query_params['observation_end'] = observation_end
    if units:
        query_params['units'] = units
    if frequency:
        query_params['frequency'] = frequency
    if aggregation_method:
        query_params['aggregation_method'] = aggregation_method
    if ondate:
        query_params['realtime_start'] = ondate
        query_params['realtime_end'] = ondate if not realtime_end else realtime_end

    # Make the API request
    response = requests.get(base_url, params=query_params)
    response.raise_for_status()  # Raise an exception for HTTP errors

    # Parse the response data
    data = response.json()['observations']
    df = pd.DataFrame(data)

    # Convert date strings to datetime objects and set as index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Convert value strings to numeric, handling missing values
    df['value'] = pd.to_numeric(df['value'], errors='coerce')

    return df

# testing = getFredData('CPIAUCNS', observation_start='2003-01-01', observation_end='2023-01-01')

