from datetime import datetime
import requests
from io import BytesIO
import os
import numpy as np
import pandas as pd
from AssayingAnomalies.wrds_utilities import *

def remote_get_compustat_data(params, **kwargs):
    "Timekeeping"
    print(f"\nNow working on collecting data from COMPUSTAT. Run started at {datetime.now()}.\n")

    # Default parameter values
    p = {
        "delete_files_ok": True
    }

    # Update parameters with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Define the start and end parameters
    start = params.sample_start
    end = params.sample_end

    # Set the path to store compustat data.
    compFolder = params.compFolder + os.sep

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

    # 'div' and 'xssd' columns are not found in funda so I am removing them
    COMPUSTAT_Variable_names_annual.remove('div')
    COMPUSTAT_Variable_names_annual.remove('xssd')


    # Create commands for custom sql queries and saving files
    commands = []
    file_locations = []
    sql_annual = "SELECT " + ", ".join(COMPUSTAT_Variable_names_annual) + " FROM comp.funda " \
                                                                          f"WHERE datadate>='01-01-{start}' " \
                                                                          f"and datadate<='12-31-{end}' "
    file_name_annual = "comp_funda.csv"
    file_location_annual = f"/scratch/rochester/{file_name_annual}"
    file_locations.append(file_location_annual)

    sql_quarterly = "SELECT " + ", ".join(COMPUSTAT_Variable_names_quarterly) + " FROM comp.fundq " \
                                                                                f"WHERE datadate>='01-01-{start}' " \
                                                                                f"and datadate<='12-31-{end}' "
    file_name_quarterly = "comp_fundq.csv"
    file_location_quarterly = f"/scratch/rochester/{file_name_quarterly}"
    file_locations.append(file_location_quarterly)

    command1 = f"testing = db.raw_sql(\"{sql_annual}\")"
    command2 = f"testing.to_csv(\"/scratch/rochester/{file_name_annual}\")"
    command3 = f"testing = db.raw_sql(\"{sql_quarterly}\")"
    command4 = f"testing.to_csv(\"/scratch/rochester/{file_name_quarterly}\")"

    commands.extend([command1, command2, command3, command4])

    # Start a new child process, and connect to the SSH server
    child = ssh_login(params)

    # Start a qrsh session
    start_qrsh(params, child)

    # Start Python session
    start_python_wrds(child)

    # Execute python commands on wrds cloud
    execute_commands(child, commands)

    # Exit all sessions
    exit_sessions(child)

    # Transfer the files and return a list of files that did not transfer
    print("Using SFTP to transfer files.")
    save_folder = params.compFolder
    problem_files = transfer_files(params, file_locations, save_folder)

    # Delete the files
    if p['delete_files_ok']:
        delete_files(params, file_locations, problem_files)

    # Print statement indicating if all files were completely transferred or not.
    if problem_files:
        print("The following files did not transfer: ")
        for file in problem_files:
            print(file)
    else:
        print("All files were successfully transferred and deleted from WRDS storage.")

    "Timekeeping"
    print(f"\nFinished collecting data from COMPUSTAT. Run ended at {datetime.now()}.\n")

    return


# from AssayingAnomalies import Config
# import AssayingAnomalies.Functions as aa
#
#
# "Create an instance of class 'Config' "
# params = Config()
#
# "Prompt the user to enter their parameters"
# params.prompt_user()
#
# "Create folders to store the downloaded data and created variables"
# params.make_folders()
#
# remote_get_compustat_data(params)
