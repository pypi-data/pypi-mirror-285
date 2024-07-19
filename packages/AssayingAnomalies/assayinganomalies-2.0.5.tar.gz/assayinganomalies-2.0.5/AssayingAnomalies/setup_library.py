"""
Things to note:
            - The script creates a subdirectory titled 'AA_Data' to store all the created variables.
            - Sometimes the script asks the user to enter their WRDS username and password twice.
            - Sometimes a 'FutureWarning' is returned while making CRSP monthly data, just ignore this, it doesn't hurt
            anything and will be fixed later.
            - For now, make sure sample dates includes 2012.
            - In the matlab version, data is stored in the same directory as the code. In this version, the user can
            specify where they want the data to live, since they might be using cloud storage/computing.
"""
from AssayingAnomalies import Config
import AssayingAnomalies.Functions as aa


def download_and_process_data(params):
    "Download & store all the CRSP data we'll need"
    if params.remote_or_not:
        aa.remote_get_crsp_data(params=params)
    else:
        aa.getCRSPData(params=params)

    "Make CRSP data"
    aa.makeCRSPMonthlyData(params=params)

    "Make additional CRSP variables"
    aa.makeCRSPDerivedVariables(params=params)

    "Download & store all the COMPUSTAT data we'll need (annual and quarterly)"
    if params.remote_or_not:
        aa.remote_get_compustat_data(params=params)
    else:
        aa.getCOMPUSTATData(params=params)

    "Merge CRSP and COMPUSTAT, store all variables"
    aa.mergeCRSPCOMP(params=params)

    "Make additional COMPUSTAT variables"
    aa.makeCOMPUSTATDerivedVariables(params=params)

    "Download & store all the daily CRSP data we'll need"
    if params.remote_or_not:
        aa.remote_get_daily_crsp(params=params)
    else:
        aa.get_crsp_daily_data(params=params)

    "Make the daily variables"
    aa.makeCRSPDailyData(params=params)

    "Make the daily derived variablres"
    aa.makeCRSPDailyDerivedVariables(params=params)

    "Make transaction costs"
    aa.makeTradingCosts(params=params)

    "Make anomalies"
    aa.makeNovyMarxVelikovAnomalies(params=params)

    "Make beta"
    aa.makeBetas(params=params)

    print("Data download and processing is now complete. Check out the file, use_library.py for examples of how to use "
          "the toolkit.")


def initial_setup():
    print("Welcome to the AssayingAnomalies toolkit. Let's get you started.")
    params = Config()
    params.set_up()
    params.save_params()

    # Ask the user if they want to proceed with data download and processing
    proceed = input("Configuration saved. Would you like to proceed with downloading data and making variables? "
                    "(yes/no): ").strip().lower()
    if proceed == 'yes':
        download_and_process_data(params)
    else:
        print("Setup complete. You can run the data download and processing later.")


if __name__ == "__main__":
    initial_setup()


