from AssayingAnomalies.wrds_utilities.utilities import ssh_login, start_qrsh, start_python_wrds, exit_sessions,\
    execute_commands, transfer_files, delete_files, create_virtual_environment
from datetime import datetime
import numpy as np


def remote_get_daily_crsp(params, **kwargs):
    # Create a virtual environment for pyarrow and parquet
    print(f"First we need to create a virtual environment.")
    create_virtual_environment(params)

    # Timekeeping
    print(f"Now downloading daily CRSP stock file. Run began at {datetime.now()}.")

    # Default keyword arguments
    p = {
        "delete_files_ok": True
    }

    # Update keyword arguments with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Define the columns to pull from WRDS
    columns_to_pull = ['permno', 'date', 'cfacpr', 'cfacshr', 'bidlo', 'askhi', 'prc', 'vol', 'ret', 'bid',
                       'ask', 'shrout', 'openprc', 'numtrd']

    # Set the beginning and ending year
    start = params.sample_start
    end = params.sample_end

    # Manually select years before 2000 based on your intervals
    years_before_2000 = [start, 2000 - 55, 2000 - 25, 2000 - 10]  # 1925, 1970, 1985, 1990

    # Ensure years_before_2000 are within the range and unique
    years_before_2000 = [year for year in years_before_2000 if start <= year < 2000]
    years_before_2000 = sorted(set(years_before_2000))

    # Years from 2000 to end, split into three periods
    if end >= 2000:
        years_2000_to_end = np.linspace(max(start, 2000), end, 3, endpoint=True).astype(int)
    else:
        years_2000_to_end = []

    # Combine and sort the lists
    years = sorted(set(years_before_2000 + years_2000_to_end.tolist()))

    # Create commands for custom sql query and saving files
    commands = []
    file_locations = []
    for start, end in zip(years, years[1:]):
        # dsf_file_name = f"crsp_dsf_{end}.csv"
        dsf_file_name = f"crsp_dsf_{end}.parquet"
        file_location_dsf = f'/scratch/rochester/{dsf_file_name}'
        file_locations.append(file_location_dsf)
        dsf_sql_string = "SELECT " + ", ".join(columns_to_pull) + f" FROM CRSP.DSF " \
                f"WHERE date>='01-01-{start}' " \
                f"and date<'01-01-{end+1}' "
        command1 = f"testing = db.raw_sql(\"{dsf_sql_string}\")"
        command2 = f"testing.to_parquet(\"/scratch/rochester/{dsf_file_name}\")"
        commands.extend([command1, command2])

    # Create the delist file names, location, and commands
    delist_file_name = "crsp_dsedelist.csv"
    file_location_delist = f'/scratch/rochester/{delist_file_name}'
    file_locations.append(file_location_delist)
    delist_sql_string = "SELECT * FROM CRSP.DSEDELIST"
    command3 = f"testing = db.raw_sql(\"{delist_sql_string}\")"
    command4 = f"testing.to_csv(\"/scratch/rochester/{delist_file_name}\")"
    commands.extend([command3, command4])

    # Start a new child process, and connect to the SSH server
    child = ssh_login(params)

    # Start a qrsh session
    start_qrsh(params, child)

    # Start Python session
    start_python_wrds(child, venv=True)

    # Execute python commands on wrds cloud
    execute_commands(child, commands)

    # Exit all sessions
    exit_sessions(child)

    # Transfer the files and return a list of files that did not transfer
    print("Using SFTP to transfer files.")
    save_folder = params.daily_crsp_folder
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

    return

# from AssayingAnomalies import Config
# import AssayingAnomalies.Functions as AA
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
# get_daily_crsp(params)
