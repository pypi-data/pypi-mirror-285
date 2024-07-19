import wrds
import numpy as np
import pandas as pd
import requests
import os
from io import BytesIO
from datetime import datetime
# import zipfile

def getCOMPUSTATData(params):
    # Timekeeping
    print(f"Began collecing COMPUSTAT data at {datetime.now()}")

    compFolder = params.compFolder + os.sep

    "Store the sample start and end dates"
    start = params.sample_start
    end = params.sample_end

    " First download the csv of necessary variable names"
    # location of csv file on velikov's github account
    url = 'https://raw.githubusercontent.com/velikov-mihail/AssayingAnomalies/main/Library%20Update/Inputs/COMPUSTAT%20Variable%20Names.csv'

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    # store the bytes object as dataframe
    COMPUSTAT_Variable_names = pd.read_csv(BytesIO(response.content))
    # save the dataframe
    COMPUSTAT_Variable_names.to_csv(compFolder + 'COMPUSTAT_Variable_names.csv')

    # create dataframes of annual and quarterly variable names
    COMPUSTAT_Variable_names_annual = np.array(COMPUSTAT_Variable_names.iloc[:, 0])
    # change the column names to lower case
    COMPUSTAT_Variable_names_annual = [i.lower() for i in COMPUSTAT_Variable_names_annual]
    # Adding additional columns that are needed in mergeCRSCOMP :TODO Note: Why is gvkey and datadate not included in the .csv file for annual variable names? Why is neither gvkey nor rdq included for quarterly?
    COMPUSTAT_Variable_names_annual.append('gvkey')
    COMPUSTAT_Variable_names_annual.append('datadate')

    # the entries after index 33 are NaN
    COMPUSTAT_Variable_names_quarterly = np.array(COMPUSTAT_Variable_names.iloc[:34, 1])
    # change the column names to lower case
    COMPUSTAT_Variable_names_quarterly = [i.lower() for i in COMPUSTAT_Variable_names_quarterly]
    # Adding additional columns that are needed in mergeCRSCOMP
    COMPUSTAT_Variable_names_quarterly.append('gvkey')
    COMPUSTAT_Variable_names_quarterly.append('rdq')

    "Establish connection to WRDS"
    db = wrds.Connection(wrds_username=params.username)

    # TODO:NOTE 'div' and 'xxsd' are not found in comp.funda so I am temporarily removing them"
    # for i in range(len(COMPUSTAT_Variable_names_annual)):
    #     print(i)
    #     db.get_table(library='comp', table='funda', columns=[COMPUSTAT_Variable_names_annual[i]], obs=10)
    COMPUSTAT_Variable_names_annual.remove('div')
    COMPUSTAT_Variable_names_annual.remove('xssd')

    "Create sql query to pass to db.raw_sql()"
    annual_sql = "SELECT " + ", ".join(COMPUSTAT_Variable_names_annual) + " FROM comp.funda " \
                                                                   f"WHERE datadate>='01-01-{start}' " \
                                                                   f"and datadate<='12-31-{end}' "

    quarterly_sql = "SELECT " + ", ".join(COMPUSTAT_Variable_names_quarterly) + " FROM comp.fundq " \
                                                                                f"WHERE datadate>='01-01-{start}' " \
                                                                                f"and datadate<='12-31-{end}' "

    "Get compustat annual data"
    # COMPUSTATQuery_annual = db.get_table(library='comp', table='funda', columns=COMPUSTAT_Variable_names_annual)
    COMPUSTATQuery_annual = db.raw_sql(annual_sql)
    # Save the file
    COMPUSTATQuery_annual.to_csv(compFolder + 'comp_funda.csv')

    "Get compustat quarterly data"
    # loop below tests if each column exists
    # for i in range(len(COMPUSTAT_Variable_names_quarterly)):
    #     print(i)
    #     db.get_table(library='comp', table='fundq', columns=[COMPUSTAT_Variable_names_quarterly[i]], obs=10)
    # COMPUSTAT_Variable_names_quarterly.remove('adjex')
    # COMPUSTATQuery_quarterly = db.get_table(library='comp', table='fundq', columns=COMPUSTAT_Variable_names_quarterly)
    COMPUSTATQuery_quarterly = db.raw_sql(quarterly_sql)
    COMPUSTATQuery_quarterly.to_csv(compFolder + 'comp_fundq.csv')

    db.close()

    print(f"Finished collecing COMPUSTAT data at {datetime.now()}")

