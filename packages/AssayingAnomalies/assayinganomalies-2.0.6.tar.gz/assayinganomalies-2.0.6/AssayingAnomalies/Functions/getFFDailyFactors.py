import numpy as np
import pandas as pd
import requests
from io import BytesIO
import os
import zipfile


def getFFDailyFactors(params):
    """

    :return:
    """

    # URL to Ken French's daily FF3
    url = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_Factors_daily_CSV.zip'

    # Set path to CRSP DailyFolder
    daily_crsp_folder = params.daily_crsp_folder + os.sep

    # Set path to FF Data folder
    FFDataFolder = params.ff_data_folder + os.sep

    # Load dates
    ddates = pd.read_csv(daily_crsp_folder + 'ddates.csv', index_col=0)

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # saving the zip file as an object
    zf = zipfile.ZipFile(BytesIO(response.content))
    # extracting and saving the contents
    zf.extractall(FFDataFolder)
    # loading the csv file that was extracted. the first three rows are useless text so we will skip them
    # :TODO:F Sometimes the file is saved as .csv and other times as .CSV.
    FF3factors = pd.read_csv(FFDataFolder + 'F-F_Research_Data_Factors_daily.CSV', skiprows=3)

    # the final row is also useless so we will remove it
    FF3factors = FF3factors.iloc[:-1, :]

    # Note: The raw data does not have a column for "MKT" factor, instead it is is MKT-RF, but since we didn't add it
    # back in the monthly data I will not add it back now. But the line below that is commented out will correct for
    # this if desired.
    FF3factors.columns = ['dates', 'MKT', 'SMB', 'HML', 'RF']
    # FF3factors['MKT'] = FF3factors['MKT'] + FF3factors['RF']
    # Save the FF daily dates
    FF3factors['dates'].to_csv(FFDataFolder + 'ffdates_daily.csv')

    # Intersect our dates with the ones from Ken French Website; ia is index of elements in dates array in common with those
    # in FF.dates and vica versa.
    _, ia, ib = np.intersect1d(np.array(ddates).astype(int), FF3factors['dates'].values.astype(int), return_indices=True)

    #create the variables
    dmkt = np.full(len(ddates), np.nan)
    dsmb = np.full(len(ddates), np.nan)
    dhml = np.full(len(ddates), np.nan)
    drf = np.full(len(ddates), np.nan)

    # first need to change the datatypes from string to float
    FF3factors = FF3factors.astype(float)
    dmkt[ia] = FF3factors.loc[ib, 'MKT'] / 100
    dsmb[ia] = FF3factors.loc[ib, 'SMB'] / 100
    dhml[ia] = FF3factors.loc[ib, 'HML'] / 100
    drf[ia] = FF3factors.loc[ib, 'RF'] / 100

    "Now repeat the steps for UMD factor"
    # URL to Ken French's daily momentum data
    url = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_daily_CSV.zip'

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # saving the zip file as an object
    zf = zipfile.ZipFile(BytesIO(response.content))
    # extracting and saving the contents
    zf.extractall(FFDataFolder)
    # loading the csv file that was extracted. the first 12 rows are useless text so we will skip them and the last row
    # is also text so we will remove it
    UMDFactor = pd.read_csv(FFDataFolder + 'F-F_Momentum_Factor_daily.CSV', skiprows=12)
    UMDFactor = UMDFactor.iloc[:-1, :]

    # rename the columns
    UMDFactor.columns = ['dates', 'UMD']

    # Intersect our dates with the ones from Ken French Website; ia is index of elements in dates array in common with those
    # in FF.dates and vica versa.
    _, ia, ib = np.intersect1d(np.array(ddates).astype(int), UMDFactor['dates'].values.astype(int), return_indices=True)

    #create the variables
    dumd = np.full(len(ddates), np.nan)

    # first need to change the datatypes from string to float
    UMDFactor = UMDFactor.astype(float)
    dumd[ia] = UMDFactor.loc[ib, 'UMD'] / 100

    "Now repeat the steps for 5 factors"
    url = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_daily_CSV.zip'

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # saving the zip file as an object
    zf = zipfile.ZipFile(BytesIO(response.content))
    # extracting and saving the contents
    zf.extractall(FFDataFolder)
    # loading the csv file that was extracted. the first 3 rows are useless text so we will skip them
    FF5factors = pd.read_csv(FFDataFolder + 'F-F_Research_Data_5_Factors_2x3_daily.CSV', skiprows=3)
    FF5factors.columns = ['dates', 'MKT', 'SMB', 'HML', 'RMW', 'CMA', 'RF']

    # Intersect our dates with the ones from Ken French Website; ia is index of elements in dates array in common with those
    # in FF.dates and vica versa.
    _, ia, ib = np.intersect1d(np.array(ddates).astype(int), FF5factors['dates'].values.astype(int), return_indices=True)

    #create the variables
    dsmb2 = np.full(len(ddates), np.nan)
    drmw = np.full(len(ddates), np.nan)
    dcma = np.full(len(ddates), np.nan)

    # first need to change the datatypes from string to float
    FF5factors = FF5factors.astype(float)
    dsmb2[ia] = FF5factors.loc[ib, 'SMB'] / 100
    drmw[ia] = FF5factors.loc[ib, 'RMW'] / 100
    dcma[ia] = FF5factors.loc[ib, 'CMA'] / 100

    "Create and save useful dataframes"
    const = np.full(len(drf), 0.01)
    const = pd.Series(const)
    dmkt = pd.Series(dmkt)
    dsmb = pd.Series(dsmb)
    dhml = pd.Series(dhml)
    drf = pd.Series(drf)
    dumd = pd.Series(dumd)
    dsmb2 = pd.Series(dsmb2)
    drmw = pd.Series(drmw)
    dcma = pd.Series(dcma)

    # factors = ['const', 'dmkt', 'dsmb', 'dhml', 'drf', 'dumd', 'dsmb2', 'drmw', 'dcma']

    # :TODO Save ['ffdates', 'const', 'rf', 'mkt', 'smb', 'smb2', 'hml', 'umd', 'rmw', 'cma', 'ff3', 'ff4', 'ff5', 'ff6'] in a giant matrix called ff.csv
    ff = pd.concat([ddates, const, dmkt, dsmb, dhml, drf, dumd, dsmb2, drmw, dcma], axis=1)
    ff.columns = ['dates', 'const', 'mkt', 'smb', 'hml', 'rf', 'umd', 'smb2', 'rmw', 'cma']
    ff.to_csv(FFDataFolder + 'dff.csv')

    ff3 = pd.concat([ddates, const, dmkt, dsmb, dhml], axis=1)
    ff3.columns = ['dates', 'const', 'mkt', 'smb', 'hml']
    ff3.to_csv(FFDataFolder + 'dff3.csv')

    ff4 = pd.concat([ff3, dumd], axis=1)
    ff4.columns = ['ddates', 'const', 'dmkt', 'dsmb', 'dhml', 'dumd']
    ff4.to_csv(FFDataFolder + 'dff4.csv')

    ff5 = pd.concat([ddates, const, dmkt, dsmb2, dhml, drmw, dcma], axis=1)
    ff5.columns = ['dates', 'const', 'mkt', 'smb2', 'hml', 'rmw', 'cma']
    ff5.to_csv(FFDataFolder + 'dff5.csv')

    ff6 = pd.concat([ff5, dumd], axis=1)
    ff6.columns = ['dates', 'const', 'mkt', 'smb2', 'hml', 'rmw', 'cma', 'umd']
    ff6.to_csv(FFDataFolder + 'dff6.csv')

    return

# getFFDailyFactors(params)