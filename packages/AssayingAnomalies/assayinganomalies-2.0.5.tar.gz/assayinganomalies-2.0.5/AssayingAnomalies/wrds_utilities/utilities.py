import os
import sys
import pexpect
import paramiko


def ssh_login(params):
    host = 'wrds-cloud.wharton.upenn.edu'

    ssh_command = f"ssh {params.username}@{host}"
    child = pexpect.spawn(ssh_command, encoding='utf-8')
    child.expect('Password:', timeout=30)
    child.sendline(params.password)
    child.expect('\[.*@.*\]\$')
    child.sendline('1')
    print("Connected to WRDS.")
    return child


def start_qrsh(params, child):
    child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('qrsh')
    child.expect('password:', timeout=30)
    child.sendline(params.password)
    print("Started interactive wrds-cloud session")
    return child


def start_python_wrds(child, venv=False):
    child.expect('\[.*@.*\]\$', timeout=30)
    if venv:
        child.sendline('source virtualenvs/daily_environment/bin/activate')
        child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('python3')
    child.expect('>>>', timeout=30)
    child.sendline('import wrds')
    child.expect('>>>', timeout=30)
    child.sendline('db = wrds.Connection()')
    print("Started interactive python session.")
    return child


def execute_commands(child, commands, timeout=2400):
    child.logfile_read = sys.stdout
    for command in commands:
        child.expect('>>>', timeout=timeout)
        child.sendline(command)
    return child


def exit_sessions(child):
    child.expect('>>>', timeout=300)
    child.sendline('exit()')
    child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('exit')
    child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('exit')
    child.close()
    print("Exited all sessions.")


def transfer_files(params, file_locations, save_folder):
    host = 'wrds-cloud.wharton.upenn.edu'
    problem_files = []

    # Create a new SSH client
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the server
        ssh.connect(host, username=params.username, password=params.password)

        # Open an SFTP session
        sftp = ssh.open_sftp()

        # Transfer each file
        for file_location in file_locations:
            try:
                destination = f"{save_folder}" + os.sep + f"{file_location.split('/')[-1]}"
                print(destination)
                sftp.get(file_location, destination)
            except Exception as e:
                print(f"Error occurred while transferring {file_location}: {e}")
                problem_files.append(file_location)

        # Close the SFTP session
        sftp.close()

    except Exception as e:
        print(f"Error occurred while connecting: {e}")

    finally:
        # Close the SSH connection
        ssh.close()

    if problem_files:
        print("The following files did not transfer: ")
        for file in problem_files:
            print(file)

    return problem_files


def delete_files(params, file_locations, problem_files):
    host = 'wrds-cloud.wharton.upenn.edu'

    # Exclude problem files
    files_to_delete = [file for file in file_locations if file not in problem_files]

    # Generate command to delete multiple files at once instead of spawning new ssh session each time.
    command = f'ssh {params.username}@{host} rm ' + ' '.join(files_to_delete)

    # Delete all the files
    try:
        child = pexpect.spawn(command, encoding='utf-8')
        child.expect('Password: ')
        child.sendline(params.password)
        child.expect(pexpect.EOF)
        print("File deletion completed for: ", ', '.join(files_to_delete))
        child.close()
    except pexpect.exceptions.EOF:
        print("Connection reset while trying to delete files")


def create_virtual_environment(params):
    print("Creating virtual python environment.")

    # Start a new child process, and connect to the SSH server
    child = ssh_login(params)

    # Create virtual environment
    child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('python -m venv --system-site-packages ~/virtualenvs/daily_environment')
    child.logfile_read = sys.stdout

    # Activate environment
    child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('source virtualenvs/daily_environment/bin/activate')
    child.logfile_read = sys.stdout

    # pip install packages
    child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('pip install parquet pyarrow')
    child.logfile_read = sys.stdout

    # Deactivate environment
    child.expect('\[.*@.*\]\$', timeout=30)
    child.sendline('deactivate')
    child.logfile_read = sys.stdout

    child.close()
    print("\n\nCompleted virtual environment setup.\n")


