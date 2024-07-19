import numpy as np
import pandas as pd
import requests
from io import BytesIO
import os
import zipfile

# crspFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'

def getFFFactors(params):
    """

    :return:
    """
    url = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_data_Factors_CSV.zip'

    # Set path to CRSP Folder
    crspFolder = params.crspFolder + os.sep

    # Load dates
    dates = pd.read_csv(crspFolder + 'dates.csv', index_col=0)

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # saving the zip file as an object
    zf = zipfile.ZipFile(BytesIO(response.content))
    # extracting and saving the contents
    zf.extractall(crspFolder)
    # loading the csv file that was extracted. the first three rows are useless text so we will skip them
    # :TODO:F Sometimes the file is saved as .csv and other times as .CSV.
    FF3factors = pd.read_csv(crspFolder + 'F-F_Research_Data_Factors.CSV', skiprows=3)
    FF3factors.columns = ['dates', 'MKT', 'SMB', 'HML', 'RF']
    # The dataframe has the annual factors appended to the bottom of the dataframe, separated by a row of text. We need to
    # find where this occurs and then slice the dataframe to keep everything before it.
    # Uses the isnull function to create a boolean mask that is True where the 'MKT' column is NaN and False
    # otherwise. The idxmax function is then used to return the index label of the first occurrence of the maximum value,
    # i.e. the firt time a 1 occors, representing the first time NaN occurs. Note, I'm using MKT instead of dates because
    # the dates column has useless text followed by NaN in the next column.
    e = FF3factors['MKT'].isnull().idxmax()
    # Next we want to slice the dataframe
    FF3factors = FF3factors.iloc[:e, :]
    # Save the FF dates TODO:Q Matlab code saves ffdates as just a copy of the preexisting dates file. But ffdates start at 192607 instead of 192512.
    FF3factors.dates.to_csv(crspFolder + 'ffdates.csv')
    # Intersect our dates with the ones from Ken French Website; ia is index of elements in dates array in common with those
    # in FF.dates and vica versa.
    _, ia, ib = np.intersect1d(np.array(dates).astype(int), FF3factors['dates'].values.astype(int), return_indices=True)

    #create the variables
    mkt = np.full(len(dates), np.nan)
    smb = np.full(len(dates), np.nan)
    hml = np.full(len(dates), np.nan)
    rf = np.full(len(dates), np.nan)

    # first need to change the datatypes from string to float
    FF3factors = FF3factors.astype(float)
    mkt[ia] = FF3factors.loc[ib, 'MKT'] / 100
    smb[ia] = FF3factors.loc[ib, 'SMB'] / 100
    hml[ia] = FF3factors.loc[ib, 'HML'] / 100
    rf[ia] = FF3factors.loc[ib, 'RF'] / 100

    "Now repeat the steps for UMD factor"
    url = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Momentum_Factor_CSV.zip'

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # saving the zip file as an object
    zf = zipfile.ZipFile(BytesIO(response.content))
    # extracting and saving the contents
    zf.extractall(crspFolder)
    # loading the csv file that was extracted. the first 13 rows are useless text so we will skip them
    UMDFactor = pd.read_csv(crspFolder + 'F-F_Momentum_Factor.CSV', skiprows=13)
    UMDFactor.columns = ['dates', 'UMD']
    # The dataframe has the annual factors appended to the bottom of the dataframe, separated by a row of text. We need to
    # find where this occurs and then slice the dataframe to keep everything before it.
    # Uses the isnull function to create a boolean mask that is True where the 'MKT' column is NaN and False
    # otherwise. The idxmax function is then used to return the index label of the first occurrence of the maximum value,
    # i.e. the firt time a 1 occurs, representing the first time NaN occurs. Note, I'm using MKT instead of dates because
    # the dates column has useless text followed by NaN in the next column.
    e = UMDFactor['UMD'].isnull().idxmax()
    # Next we want to slice the dataframe
    UMDFactor = UMDFactor.iloc[:e, :]

    # Intersect our dates with the ones from Ken French Website; ia is index of elements in dates array in common with those
    # in FF.dates and vica versa.
    _, ia, ib = np.intersect1d(np.array(dates).astype(int), UMDFactor['dates'].values.astype(int), return_indices=True)

    #create the variables
    umd = np.full(len(dates), np.nan)

    # first need to change the datatypes from string to float
    UMDFactor = UMDFactor.astype(float)
    umd[ia] = UMDFactor.loc[ib, 'UMD'] / 100

    "Now repeat the steps for 5 factors"
    url = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_CSV.zip'

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # saving the zip file as an object
    zf = zipfile.ZipFile(BytesIO(response.content))
    # extracting and saving the contents
    zf.extractall(crspFolder)
    # loading the csv file that was extracted. the first 3 rows are useless text so we will skip them
    FF5factors = pd.read_csv(crspFolder + 'F-F_Research_Data_5_Factors_2x3.csv', skiprows=3)
    FF5factors.columns = ['dates', 'MKT', 'SMB', 'HML', 'RMW', 'CMA', 'RF']
    # The dataframe has the annual factors appended to the bottom of the dataframe, seperated by a row of text. We need to
    # find where this occurs and then slice the dataframe to keep everything before it.
    # Uses the isnull function to create a boolean mask that is True where the 'MKT' column is NaN and False
    # otherwise. The idxmax function is then used to return the index label of the first occurrence of the maximum value,
    # i.e. the firt time a 1 occors, representing the first time NaN occurs. Note, I'm using MKT instead of dates because
    # the dates column has useless text followed by NaN in the next column.
    e = FF5factors['MKT'].isnull().idxmax()
    # Next we want to slice the dataframe
    FF5factors = FF5factors.iloc[:e, :]

    # Intersect our dates with the ones from Ken French Website; ia is index of elements in dates array in common with those
    # in FF.dates and vica versa.
    _, ia, ib = np.intersect1d(np.array(dates).astype(int), FF5factors['dates'].values.astype(int), return_indices=True)

    #create the variables
    smb2 = np.full(len(dates), np.nan)
    rmw = np.full(len(dates), np.nan)
    cma = np.full(len(dates), np.nan)

    # first need to change the datatypes from string to float
    FF5factors = FF5factors.astype(float)
    smb2[ia] = FF5factors.loc[ib, 'SMB'] / 100
    rmw[ia] = FF5factors.loc[ib, 'RMW'] / 100
    cma[ia] = FF5factors.loc[ib, 'CMA'] / 100

    # Create and save useful dataframes
    const = np.full(len(rf), 0.01)
    const = pd.Series(const)
    mkt = pd.Series(mkt)
    smb = pd.Series(smb)
    hml = pd.Series(hml)
    rf = pd.Series(rf)
    umd = pd.Series(umd)
    smb2 = pd.Series(smb2)
    rmw = pd.Series(rmw)
    cma = pd.Series(cma)

    factors = ['const', 'mkt', 'smb', 'hml', 'rf', 'umd', 'smb2', 'rmw', 'cma']

    # :TODO Save ['ffdates', 'const', 'rf', 'mkt', 'smb', 'smb2', 'hml', 'umd', 'rmw', 'cma', 'ff3', 'ff4', 'ff5', 'ff6'] in a giant matrix called ff.csv
    ff = pd.concat([dates, const, mkt, smb, hml, rf, umd, smb2, rmw, cma], axis=1)
    ff.columns = ['dates', 'const', 'mkt', 'smb', 'hml', 'rf', 'umd', 'smb2', 'rmw', 'cma']
    ff.to_csv(crspFolder + 'ff.csv')

    ff3 = pd.concat([dates, const, mkt, smb, hml], axis=1)
    ff3.columns = ['dates', 'const', 'mkt', 'smb', 'hml']
    ff3.to_csv(crspFolder + 'ff3.csv')

    ff4 = pd.concat([ff3, umd], axis=1)
    ff4.columns = ['dates', 'const', 'mkt', 'smb', 'hml', 'umd']
    ff4.to_csv(crspFolder + 'ff4.csv')

    ff5 = pd.concat([dates, const, mkt, smb2, hml, rmw, cma], axis=1)
    ff5.columns = ['dates', 'const', 'mkt', 'smb2', 'hml', 'rmw', 'cma']
    ff5.to_csv(crspFolder + 'ff5.csv')

    ff6 = pd.concat([ff5, umd], axis=1)
    ff6.columns = ['dates', 'const', 'mkt', 'smb2', 'hml', 'rmw', 'cma', 'umd']
    ff6.to_csv(crspFolder + 'ff6.csv')

    return

