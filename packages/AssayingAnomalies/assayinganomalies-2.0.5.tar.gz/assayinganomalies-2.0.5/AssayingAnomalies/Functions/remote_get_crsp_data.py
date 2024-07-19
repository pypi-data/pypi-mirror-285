from AssayingAnomalies.wrds_utilities.utilities import *
from datetime import datetime


def remote_get_crsp_data(params, **kwargs):
    "Timekeeping"
    print(f"\nNow working on collecting data from CRSP. Run started at {datetime.now()}.\n")

    # Default parameter values
    p = {
        "delete_files_ok": True
    }

    # Update parameters with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Define the start and end dates.
    start = params.sample_start
    end = params.sample_end

    """Want to download and save the following tables from CRSP:
     MSFHDR, MSF, MSEDELIST, MSEEXCHDATES, CCMXPF_LNKHIST, STOCKNAMES"""
    # Create commands for custom sql queries and saving files
    commands = []
    file_locations = []

    sql_string_msfhdr = "select * from CRSP.MSFHDR"
    file_name_msfhdr = "crsp_msfhdr.csv"
    file_location_msfhdr = f'/scratch/rochester/{file_name_msfhdr}'
    file_locations.append(file_location_msfhdr)

    sql_string_msf = f"select * from CRSP.MSF " \
                     f"where date>='01-01-{start}' " \
                     f"and date<'01-01-{end+1}' "
    file_name_msf = "crsp_msf.csv"
    file_location_msf = f'/scratch/rochester/{file_name_msf}'
    file_locations.append(file_location_msf)

    sql_string_msedelist = "select * from CRSP.MSEDELIST"
    file_name_msedelist = "crsp_msedelist.csv"
    file_location_msedelist = f'/scratch/rochester/{file_name_msedelist}'
    file_locations.append(file_location_msedelist)

    sql_string_exchdates = "select * from CRSP.MSEEXCHDATES"
    file_name_exchdates = "crsp_mseexchdates.csv"
    file_location_exchdates = f'/scratch/rochester/{file_name_exchdates}'
    file_locations.append(file_location_exchdates)

    sql_string_lnkhist = "select * from CRSP.CCMXPF_LNKHIST"
    file_name_lnkhist = "crsp_ccmxpf_lnkhist.csv"
    file_location_lnkhist = f'/scratch/rochester/{file_name_lnkhist}'
    file_locations.append(file_location_lnkhist)

    sql_string_stocknames = "select * from CRSP.STOCKNAMES"
    file_name_stocknames = "crsp_stocknames.csv"
    file_location_stocknames = f'/scratch/rochester/{file_name_stocknames}'
    file_locations.append(file_location_stocknames)

    command1 = f"testing = db.raw_sql(\"{sql_string_msfhdr}\")"
    command2 = f"testing.to_csv(\"/scratch/rochester/{file_name_msfhdr}\")"
    command3 = f"testing = db.raw_sql(\"{sql_string_msf}\")"
    command4 = f"testing.to_csv(\"/scratch/rochester/{file_name_msf}\")"
    command5 = f"testing = db.raw_sql(\"{sql_string_msedelist}\")"
    command6 = f"testing.to_csv(\"/scratch/rochester/{file_name_msedelist}\")"
    command7 = f"testing = db.raw_sql(\"{sql_string_exchdates}\")"
    command8 = f"testing.to_csv(\"/scratch/rochester/{file_name_exchdates}\")"
    command9 = f"testing = db.raw_sql(\"{sql_string_lnkhist}\")"
    command10 = f"testing.to_csv(\"/scratch/rochester/{file_name_lnkhist}\")"
    command11 = f"testing = db.raw_sql(\"{sql_string_stocknames}\")"
    command12 = f"testing.to_csv(\"/scratch/rochester/{file_name_stocknames}\")"

    commands.extend([command1, command2, command3, command4, command5, command6, command7, command8, command9,
                     command10, command11, command12])

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
    save_folder = params.crspFolder
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
    print(f"\nFinished collecting data from CRSP. Run ended at {datetime.now()}.\n")

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
# remote_get_crsp_data(params)