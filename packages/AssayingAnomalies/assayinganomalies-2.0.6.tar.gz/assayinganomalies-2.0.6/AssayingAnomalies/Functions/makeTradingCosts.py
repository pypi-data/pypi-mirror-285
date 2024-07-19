from glob import glob
from scipy.stats.mstats import winsorize
from multiprocessing import Pool
from AssayingAnomalies.Functions.makeGibbs import makeGibbs
from AssayingAnomalies.Functions.makeCorwinSchultz import makeCorwinSchultz
from AssayingAnomalies.Functions.makeAbdiRanaldi import makeAbdiRanaldi
from AssayingAnomalies.Functions.makeKyleObizhaeva import makeKyleObizhaeva
from AssayingAnomalies.Functions.make_hf_effective_spreads import *
from AssayingAnomalies.Functions.rank_with_nan import rank_with_nan
from AssayingAnomalies.Functions.fill_missing_tcosts import fill_missing_tcosts


def parallel_make_trading_costs(function_name):
    if function_name == 'hl':
        return 'hl', makeCorwinSchultz()
    elif function_name == 'chl':
        return 'chl', makeAbdiRanaldi()
    elif function_name == 'vov':
        return 'vov', makeKyleObizhaeva()
    else:
        raise ValueError("Invalid function name")


def makeTradingCosts(params):
    # Timekeeping
    print(f"\nNow working on creating the transaction costs. Run started at {datetime.now()}\n")

    # Store the general and daily CRSP data path
    crsp_path = params.crspFolder + os.sep

    # Store the tcost types
    # tcostsType = params.tcostsType
    tcostsType = 'full'

    # Check if correct tcosts input selected
    if tcostsType not in ['full', 'lf_combo', 'gibbs']:
        print(f"params.tcostsType is {tcostsType} but should be one of the folowing: \"full\", \"lf_combo\", \"gibbs\"")

    # Initialize dictionary to hold trading costs. CorwinSchultz = hl, AbdiRanaldi = chl, KyleObizhaeva = vov
    effSpreadStruct = {'gibbs': None,
                       'hl': None,
                       'chl': None,
                       'vov': None,
                       'hf_spreads_ave': None
                       }

    "Check for Gibbs file"
    # Construct the file search pattern
    search_pattern = os.path.join(params.data_folder, '**', 'crspgibbs.csv')

    # Find all files matching the pattern
    gibbs_file_list = glob(search_pattern, recursive=True)  # recursive=True searches the subdirectories as well

    # Check if any files were found
    if not gibbs_file_list:
        raise FileNotFoundError('Gibbs input file does not exist. Gibbs trading cost estimate cannot be constructed.')
    else:
        file_path = gibbs_file_list[0]

    "Create Gibbs spreads"
    # path to file with Hasbrouck effective spread estimates
    effSpreadStruct['gibbs'] = makeGibbs(params, file_path)

    if tcostsType in ['lf_combo', 'full']:
        if not params.num_cpus > 1:
            effSpreadStruct['hl'] = makeCorwinSchultz()
            effSpreadStruct['chl'] = makeAbdiRanaldi()
            effSpreadStruct['vov'] = makeKyleObizhaeva()

        else:
            functions_to_run = ['hl', 'chl', 'vov']

            # Create a pool of workers and run the functions in parallel
            with Pool(processes=min(3, os.cpu_count())) as pool:
                results = pool.map(parallel_make_trading_costs, functions_to_run)

            # Update effSpreadStruct with the results
            for key, value in results:
                effSpreadStruct[key] = value

    if tcostsType == 'full':
        search_pattern = os.path.join(params.data_folder, '**', 'hf_monthly_pre_2003.csv')
        hf_file_list = glob(search_pattern, recursive=True)
        if not hf_file_list:
            raise FileNotFoundError('High-frequency trading cost input file does not exist. High-frequency trading '
                                    'cost estimate cannot be constructed prior to 2003.')
        else:
            if params.remote_or_not:
                get_hf_spreads_data(params)
                make_hf_effective_spreads(params)
                effSpreadStruct['hf_spreads_ave'] = extend_hf_effective_spreads(params)
            else:
                effSpreadStruct['hf_spreads_ave'] = pd.DataFrame(np.nan, index=effSpreadStruct['chl'].index,
                                                                 columns=effSpreadStruct['chl'].columns)
                print("The toolkit does not currently support retrieving HF effective spreads data unless you are working"
                      "on a Unix based system."
                      )

    # Winsorize by keeping anything between 0 and 99.9th percentiles.
    for key in effSpreadStruct.keys():
        flat_values = effSpreadStruct[f'{key}'].to_numpy().flatten()
        winsorized_values = winsorize(flat_values, limits=[0, 0.001], nan_policy='omit')
        effSpreadStruct[f'{key}'] = pd.DataFrame(winsorized_values.reshape(effSpreadStruct[f'{key}'].shape))

    # Check if we need to adjust some of the tcost measures
    if tcostsType.lower() == 'gibbs':
        # No need to worry about the rest
        tcosts_raw = effSpreadStruct['gibbs'] / 2
        # tcosts_raw.to_csv(crsp_path + 'tcosts_raw.csv')
        tcosts_raw.columns = tcosts_raw.columns.astype(str)
        tcosts_raw.to_parquet(crsp_path + 'tcosts_raw.parquet')
    else:
        exchcd = pd.read_csv(crsp_path + 'exchcd.csv', index_col=0).astype(float)
        exchcd.index = pd.to_datetime(exchcd.index.astype(int), format='%Y%m')

        # Excluding NASDAQ stocks prior to 1983 for Gibbs and VoV
        # Create a mask for dates before 1983 and exchange code being 3
        years = np.tile(exchcd.index.year, (len(exchcd.columns), 1)).T
        mask = (exchcd == 3) & (years < 1983)
        temp = effSpreadStruct['gibbs'].to_numpy()
        temp[mask] = np.nan
        effSpreadStruct['gibbs'] = temp
        temp = effSpreadStruct['vov'].to_numpy()
        temp[mask] = np.nan
        effSpreadStruct['vov'] = temp

        # Excluding Nasdaq stocks prior to 1993 for HL and CHL
        mask = (exchcd == 3) & (years < 1993)
        temp = effSpreadStruct['hl'].to_numpy()
        temp[mask] = np.nan
        effSpreadStruct['hl'] = temp
        temp = effSpreadStruct['chl'].to_numpy()
        temp[mask] = np.nan
        effSpreadStruct['chl'] = temp

        # Excluding AMEX stocks prior to 1962 for all
        mask = (exchcd == 3) & (years < 1962)
        for key in ['gibbs', 'hl', 'chl', 'vov']:
            temp = effSpreadStruct[key]
            temp[mask] = np.nan
            effSpreadStruct[key] = pd.DataFrame(temp)

        # In the matlab code, reshapedEffSpreadRaw is a long vector containing the average trading cost for each
        # permno for each month across the 4 lf measures. However, this is then reshaped back to a matrix. I
        EffSpreadRaw = pd.concat([effSpreadStruct['gibbs'], effSpreadStruct['hl'], effSpreadStruct['chl'],
                                  effSpreadStruct['vov']], axis=0).groupby(level=0).mean()

        # Update the average trading costs with the high frequency estimates where available.
        mask = np.isfinite(effSpreadStruct['hf_spreads_ave'])
        EffSpreadRaw[mask] = effSpreadStruct['hf_spreads_ave']

        # Need to divide the effective spreads by 2, because this is the tcost measure (half-spread!)
        tcosts_raw = EffSpreadRaw / 2

        # Store the raw tcosts
        # tcosts_raw.to_csv(crsp_path + 'tcosts_raw.csv')
        tcosts_raw.columns = tcosts_raw.columns.astype(str)
        tcosts_raw.to_parquet(crsp_path + 'tcosts_raw.parquet')

    # Fill in missing trading costs
    # Load variables we need
    me = pd.read_csv(crsp_path + 'me.csv', index_col=0).astype(float)
    rme = rank_with_nan(me)

    # Load IffVOL3 and rIVOL outside the function
    IffVOL3 = pd.read_parquet(crsp_path + 'IffVOL3.parquet')
    rIVOL = rank_with_nan(IffVOL3)
    if not params.num_cpus > 1:
        tcosts = fill_missing_tcosts(tcosts_raw, rIVOL, rme)

    else:
        # Split tcosts, rme, and rIVOL into chunks
        tcosts_chunks = np.array_split(tcosts_raw, os.cpu_count())
        rme_chunks = np.array_split(rme, os.cpu_count())
        rIVOL_chunks = np.array_split(rIVOL, os.cpu_count())
        chunks = zip(tcosts_chunks, rme_chunks, rIVOL_chunks)

        with Pool(os.cpu_count()) as pool:
            results = pool.starmap(fill_missing_tcosts, chunks)

        tcosts = pd.concat(results)

    # tcosts.to_csv(crsp_path + 'tcosts.csv')
    tcosts.columns = tcosts.columns.astype(str)
    tcosts.to_parquet(crsp_path + 'tcosts.parquet')

    # Do the FF trading costs calculation here too # :TODO Make the makeFFTcosts function.
    # makeFFTcosts()

    # Timekeeping
    print(f"Trading costs construction run ended at {datetime.now()}")


if __name__ == '__main__':
    import AssayingAnomalies
    cwd = os.getcwd()
    search_pattern = os.path.join(cwd, '**', 'config.json')
    params_path = glob(search_pattern, recursive=True)[0]
    # print(params_path)
    params = AssayingAnomalies.Config.load_params(params_path)
    makeTradingCosts(params)
