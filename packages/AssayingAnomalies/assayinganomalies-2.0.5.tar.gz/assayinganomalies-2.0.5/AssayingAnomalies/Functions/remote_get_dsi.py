from AssayingAnomalies.wrds_utilities.utilities import ssh_login, start_qrsh, start_python_wrds, exit_sessions,\
    execute_commands, transfer_files, delete_files


def remote_get_dsi(params, **kwargs):

    # Default keyword arguments
    p = {
        "delete_files_ok": True
    }

    # Update keyword arguments with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Define the columns to pull from WRDS
    columns_to_pull = ['vwretd']

    # Start a new child process, and connect to the SSH server
    child = ssh_login(params)

    # Start a qrsh session
    start_qrsh(params, child)

    # Start Python session
    start_python_wrds(params, child)

    # Create commands for custom sql query and saving files
    commands = []
    file_locations = []
    dsi_file_name = "crsp_dsi.csv"
    file_location_dsi = f'/scratch/rochester/{dsi_file_name}'
    file_locations.append(file_location_dsi)

    dsi_sql_string = "SELECT " + ", ".join(columns_to_pull) + f" FROM crsp.dsi " \
            f"WHERE date>='01-01-{params.sample_start}' " \
            f"and date<='12-31-{params.sample_end}' "


    command1 = f"testing = db.raw_sql(\"{dsi_sql_string}\")"
    command2 = f"testing.to_csv(\"/scratch/rochester/{dsi_file_name}\")"
    commands.extend([command1, command2])

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

# # from AssayingAnomalies import Config
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
# remote_get_dsi(params)
