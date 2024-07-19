from datetime import datetime
import numpy as np
import pandas as pd
import os
import math
from scipy.stats import truncnorm, multivariate_normal
from scipy.linalg import sqrtm
from multiprocessing import Pool
from .remote_get_dsi import remote_get_dsi
from .Gibbs import *


def process_permno(permno, price, trade_direction, pm, group_mask, n_sweeps_test, reg_draw_test, varu_draw_test,
                   q_draw_test, varu_start_test, c_start_test, beta_start_test, nDrop):
    results_for_permno = []
    first_year = price[permno].dropna().index.year.unique()[0]
    last_year = price[permno].dropna().index.year.unique()[-1]

    for year in range(first_year, last_year + 1):
        try:
            mask_ffill_filtered = group_mask.loc[group_mask.index.year == year, permno]
            # print(permno, str(year))

            # Filter the data for the current permno and year
            p_data = price.loc[price.index.year == year, permno]
            pm_data = pm[pm.index.year == year]
            q_data = trade_direction.loc[trade_direction.index.year == year, permno]
            # print(len(p_data))
            if np.sum(~np.isnan(p_data.to_numpy())) >= 60:
                p_data_0 = p_data[mask_ffill_filtered == 0].to_numpy()
                p_data_1 = p_data[mask_ffill_filtered == 1].to_numpy()
                p_data_2 = p_data[mask_ffill_filtered == 2].to_numpy()
                pm_data_0 = pm_data[mask_ffill_filtered == 0].values.flatten()
                pm_data_1 = pm_data[mask_ffill_filtered == 1].values.flatten()
                pm_data_2 = pm_data[mask_ffill_filtered == 2].values.flatten()
                q_data_0 = q_data[mask_ffill_filtered == 0].to_numpy()
                q_data_1 = q_data[mask_ffill_filtered == 1].to_numpy()
                q_data_2 = q_data[mask_ffill_filtered == 2].to_numpy()

                group = 0
                if np.sum(~np.isnan(p_data_0)) >= 60:
                    # print(f"group {group}")
                    # Apply RollGibbsBeta function
                    parmOut_0 = roll_gibbs_beta(p_data_0, pm_data_0, q_data_0, n_sweeps_test, reg_draw_test,
                                                varu_draw_test, q_draw_test, varu_start_test, c_start_test,
                                                beta_start_test)
                    # Process the output from RollGibbsBeta
                    p2 = parmOut_0[nDrop:]  # Drop the initial iterations (burn-in)
                    # p2 = parmOut  # Don't drop the initial iterations (burn-in)
                    # avg_results = pd.DataFrame(p2.mean(axis=0)).T  # Compute the average
                    avg_results = p2.mean(axis=0)  # Compute the average
                    # df_cost.loc[(year, group), permno] = avg_results[0]
                    # df_beta.loc[(year, group), permno] = avg_results[1]
                    # df_varu.loc[(year, group), permno] = avg_results[2]
                    result = (year, group, permno, avg_results[0], avg_results[1], avg_results[2])

                else:
                    # df_cost.loc[(year, group), permno] = np.nan
                    # df_beta.loc[(year, group), permno] = np.nan
                    # df_varu.loc[(year, group), permno] = np.nan
                    result = (year, group, permno, np.nan, np.nan, np.nan)

                results_for_permno.append(result)
                # Apply RollGibbsBeta function
                group = 1
                if np.sum(~np.isnan(p_data_1)) >= 60:
                    # print(f"group {group}")
                    # Apply RollGibbsBeta function
                    parmOut_1 = roll_gibbs_beta(p_data_1, pm_data_1, q_data_1, n_sweeps_test, reg_draw_test,
                                                varu_draw_test,
                                                q_draw_test, varu_start_test, c_start_test, beta_start_test)
                    # Process the output from RollGibbsBeta
                    p2 = parmOut_1[nDrop:]  # Drop the initial iterations (burn-in)
                    # p2 = parmOut  # Don't drop the initial iterations (burn-in)
                    # avg_results = pd.DataFrame(p2.mean(axis=0)).T  # Compute the average
                    avg_results = p2.mean(axis=0)  # Compute the average
                    # df_cost.loc[(year, group), permno] = avg_results[0]
                    # df_beta.loc[(year, group), permno] = avg_results[1]
                    # df_varu.loc[(year, group), permno] = avg_results[2]
                    result = (year, group, permno, avg_results[0], avg_results[1], avg_results[2])

                else:
                    # df_cost.loc[(year, group), permno] = np.nan
                    # df_beta.loc[(year, group), permno] = np.nan
                    # df_varu.loc[(year, group), permno] = np.nan
                    result = (year, group, permno, np.nan, np.nan, np.nan)

                results_for_permno.append(result)
                # Apply RollGibbsBeta function
                group = 2
                if np.sum(~np.isnan(p_data_2)) >= 60:
                    # print(f"group {group}")
                    parmOut_2 = roll_gibbs_beta(p_data_2, pm_data_2, q_data_2, n_sweeps_test, reg_draw_test,
                                                varu_draw_test, q_draw_test, varu_start_test, c_start_test,
                                                beta_start_test)
                    p2 = parmOut_2[nDrop:]
                    avg_results = p2.mean(axis=0)  # Compute the average
                    # df_cost.loc[(year, group), permno] = avg_results[0]
                    # df_beta.loc[(year, group), permno] = avg_results[1]
                    # df_varu.loc[(year, group), permno] = avg_results[2]
                    result = (year, group, permno, avg_results[0], avg_results[1], avg_results[2])

                else:
                    # df_cost.loc[(year, group), permno] = np.nan
                    # df_beta.loc[(year, group), permno] = np.nan
                    # df_varu.loc[(year, group), permno] = np.nan
                    result = (year, group, permno, np.nan, np.nan, np.nan)

                results_for_permno.append(result)

            else:
                # print(f"Permno {permno} in year {year} has less than 60 observations.")
                continue

        except Exception as e:
            print(f"Error processing permno {permno} in year {year}: {e}")
            results_for_permno.append((year, np.nan, permno, np.nan, np.nan, np.nan))
            continue
    # print(f"Completed permno {permno} which is {price.columns.get_loc(permno) + 1}/{len(permno.columns)}")
    print(f"Completed permno {permno}")
    return results_for_permno


def parallel_processing(params, price, trade_direction, pm, group_mask, n_sweeps_test, reg_draw_test, varu_draw_test,
                        q_draw_test, varu_start_test, c_start_test, beta_start_test, nDrop):
    permnos = price.columns.tolist()
    all_results = []

    # Create a pool of workers
    with Pool(params.num_cpus) as p:
        all_results = p.starmap(process_permno, [(permno, price, trade_direction, pm, group_mask, n_sweeps_test,
                                                  reg_draw_test, varu_draw_test, q_draw_test, varu_start_test,
                                                  c_start_test, beta_start_test, nDrop) for permno in permnos])

    # Flatten the list of results
    flat_results = [item for sublist in all_results for item in sublist]

    return flat_results


def crspGibbsBuildv01(params):
    # Store the daily CRSP data path
    daily_crsp_path = params.daily_crsp_folder + os.sep
    crsp_path = params.crspFolder + os.sep
    gibbs_path = params.gibbs_data_folder + os.sep

    # Load exchange codes
    dexchcd = pd.read_csv(daily_crsp_path + 'dexchcd.csv', index_col=0)

    # Find when permnos changed exchanges
    exch_change = dexchcd - dexchcd.shift(1)
    exch_change_mask = exch_change.notna() & (exch_change != 0)

    # Find when permnos issued shares
    dcfacpr = pd.read_csv(daily_crsp_path + 'dcfacpr.csv', index_col=0).astype(float)
    dcfacpr_change = (dcfacpr - dcfacpr.shift(1)) / dcfacpr
    dcfacpr_change_mask = (np.abs(dcfacpr_change) >= 0.2)


    # Calculate trade direction, q = sign of price_1 - price_0.
    dret = pd.read_csv(daily_crsp_path + 'dret.csv', index_col=0).astype(float)
    dprc = pd.read_csv(daily_crsp_path + 'dprc.csv', index_col=0).astype(float)
    price = np.log(1 + dret).cumsum()
    dp = np.abs(dprc) - np.abs(dprc.shift(1))
    trade_direction = np.sign(dp)
    trade_direction[dprc < 0] = 0
    trade_direction[(dp.isna()) | (dp == 0)] = 1

    # Download the daily stock index file and import it
    # remote_get_dsi(params=params)
    crsp_dsi = pd.read_csv(daily_crsp_path + 'crsp_dsi.csv', index_col=0).astype(float)
    pm = np.log(1 + crsp_dsi).cumsum()

    # Mask to put each permno in groups 0-2
    mask1 = exch_change_mask * 1
    mask2 = dcfacpr_change_mask * 2
    mask = mask1.values + mask2
    mask.index = pd.to_datetime(mask.index, format='%Y%m%d')
    mask.columns = price.columns
    mask[mask >= 2] = 2

    def custom_ffill(group):
        # Replace 0 with NaN, but keep the first 0 in a sequence of 0s
        group = group.replace(to_replace=0, method='ffill', limit=1).replace(to_replace=0, value=np.nan)
        # Forward fill NaN values
        return group.ffill()

    # Group by year and apply the custom forward fill within each year.
    group_mask = mask.groupby(mask.index.year).apply(lambda x: custom_ffill(x))

    # Now each day is 0, 1, 2 depending on which group.
    # Replace remaining NaNs with 0 if needed
    group_mask.fillna(0, inplace=True)

    "Calculated rolling gibbs beta"
    # First change indices to datetime
    trade_direction.index = pd.to_datetime(trade_direction.index, format='%Y%m%d')
    price.index = pd.to_datetime(price.index, format='%Y%m%d')
    pm.index = trade_direction.index

    n_sweeps_test = 1000
    reg_draw_test = True
    varu_draw_test = True
    q_draw_test = True
    varu_start_test = 0
    c_start_test = 0
    beta_start_test = 1

    # Number of results to throw away
    nDrop = 200

    # Create the multi-index
    groups = [0, 1, 2]
    years = mask.index.year.unique()
    multi_index = pd.MultiIndex.from_product([years, groups], names=['year', 'group'])

    # Initialize the dataframes with the multi-index
    df_cost = pd.DataFrame(index=multi_index, columns=price.columns)
    df_beta = pd.DataFrame(index=multi_index, columns=price.columns)
    df_varu = pd.DataFrame(index=multi_index, columns=price.columns)

    if not params.num_cpus > 1:
        # Iterate over each permno and year
        for permno in dret.columns:
        # for permno in dret.columns[:5]:
            # print(permno)
            first_year = price[permno].dropna().index.year.unique()[0]
            last_year = price[permno].dropna().index.year.unique()[-1]
            for year in range(first_year, last_year+1):
                mask_ffill_filtered = group_mask.loc[group_mask.index.year == year, permno]
                print(permno, str(year))
                # Filter the data for the current permno and year
                p_data = price.loc[price.index.year == year, permno]
                pm_data = pm[pm.index.year == year]
                q_data = trade_direction.loc[trade_direction.index.year == year, permno]
                # print(len(p_data))
                if np.sum(~np.isnan(p_data.to_numpy())) >= 60:
                    p_data_0 = p_data[mask_ffill_filtered == 0].to_numpy()
                    p_data_1 = p_data[mask_ffill_filtered == 1].to_numpy()
                    p_data_2 = p_data[mask_ffill_filtered == 2].to_numpy()
                    pm_data_0 = pm_data[mask_ffill_filtered == 0].values.flatten()
                    pm_data_1 = pm_data[mask_ffill_filtered == 1].values.flatten()
                    pm_data_2 = pm_data[mask_ffill_filtered == 2].values.flatten()
                    q_data_0 = q_data[mask_ffill_filtered == 0].to_numpy()
                    q_data_1 = q_data[mask_ffill_filtered == 1].to_numpy()
                    q_data_2 = q_data[mask_ffill_filtered == 2].to_numpy()

                    group = 0
                    if np.sum(~np.isnan(p_data_0)) >= 60:
                        # print(f"group {group}")
                        # Apply RollGibbsBeta function
                        parmOut_0 = roll_gibbs_beta(p_data_0, pm_data_0, q_data_0, n_sweeps_test, reg_draw_test, varu_draw_test, q_draw_test, varu_start_test, c_start_test, beta_start_test)
                        # Process the output from RollGibbsBeta
                        p2 = parmOut_0[nDrop:]  # Drop the initial iterations (burn-in)
                        # p2 = parmOut  # Don't drop the initial iterations (burn-in)
                        # avg_results = pd.DataFrame(p2.mean(axis=0)).T  # Compute the average
                        avg_results = p2.mean(axis=0)  # Compute the average
                        df_cost.loc[(year, group), permno] = avg_results[0]
                        df_beta.loc[(year, group), permno] = avg_results[1]
                        df_varu.loc[(year, group), permno] = avg_results[2]
                    else:
                        df_cost.loc[(year, group), permno] = np.nan
                        df_beta.loc[(year, group), permno] = np.nan
                        df_varu.loc[(year, group), permno] = np.nan

                        # Apply RollGibbsBeta function
                    group = 1
                    if np.sum(~np.isnan(p_data_1)) >= 60:
                        # print(f"group {group}")
                        # Apply RollGibbsBeta function
                        parmOut_1 = roll_gibbs_beta(p_data_1, pm_data_1, q_data_1, n_sweeps_test, reg_draw_test, varu_draw_test,
                                                    q_draw_test, varu_start_test, c_start_test, beta_start_test)
                        # Process the output from RollGibbsBeta
                        p2 = parmOut_1[nDrop:]  # Drop the initial iterations (burn-in)
                        # p2 = parmOut  # Don't drop the initial iterations (burn-in)
                        # avg_results = pd.DataFrame(p2.mean(axis=0)).T  # Compute the average
                        avg_results = p2.mean(axis=0)  # Compute the average
                        df_cost.loc[(year, group), permno] = avg_results[0]
                        df_beta.loc[(year, group), permno] = avg_results[1]
                        df_varu.loc[(year, group), permno] = avg_results[2]
                    else:
                        df_cost.loc[(year, group), permno] = np.nan
                        df_beta.loc[(year, group), permno] = np.nan
                        df_varu.loc[(year, group), permno] = np.nan

                        # Apply RollGibbsBeta function
                    group = 2
                    if np.sum(~np.isnan(p_data_2)) >= 60:
                        # print(f"group {group}")
                        parmOut_2 = roll_gibbs_beta(p_data_2, pm_data_2, q_data_2, n_sweeps_test, reg_draw_test, varu_draw_test, q_draw_test, varu_start_test, c_start_test, beta_start_test)
                        p2 = parmOut_2[nDrop:]
                        avg_results = p2.mean(axis=0)  # Compute the average
                        df_cost.loc[(year, group), permno] = avg_results[0]
                        df_beta.loc[(year, group), permno] = avg_results[1]
                        df_varu.loc[(year, group), permno] = avg_results[2]
                    else:
                        df_cost.loc[(year, group), permno] = np.nan
                        df_beta.loc[(year, group), permno] = np.nan
                        df_varu.loc[(year, group), permno] = np.nan

        # Save Dataframes
        df_cost.to_csv(gibbs_path + 'gibbs_cost.csv')
        df_beta.to_csv(gibbs_path + 'gibbs_beta.csv')
        df_varu.to_csv(gibbs_path + 'gibbs_varu.csv')

        print(f"Completed Hasbrouck's (2009) Gibbs construction at {datetime.now()}")
        return

    else:
        # Call the parallel process function
        results = parallel_processing(params, price, trade_direction, pm, group_mask, n_sweeps_test, reg_draw_test, varu_draw_test, q_draw_test, varu_start_test, c_start_test, beta_start_test, nDrop)
        print(f"Completed Hasbrouck's (2009) Gibbs construction at {datetime.now()}")
        for i, (year, group, permno, cost, beta, varu) in enumerate(results):
            if isinstance(group, float) and math.isnan(group):
                # print(f"NaN found in group at index {i}: (year: {year}, group: {group}, permno: {permno}, cost: {cost}, beta: {beta}, varu: {varu})")
                continue
            else:
                df_cost.loc[(year, group), permno] = cost
                df_beta.loc[(year, group), permno] = beta
                df_varu.loc[(year, group), permno] = varu
        df_cost.to_csv(gibbs_path + 'gibbs_cost.csv')
        df_beta.to_csv(gibbs_path + 'gibbs_beta.csv')
        df_varu.to_csv(gibbs_path + 'gibbs_varu.csv')

        return


# "To test against sample data:"
# df_cost = pd.read_csv(daily_crsp_path + 'gibbs_cost.csv', index_col=0).astype(float)
# df_beta = pd.read_csv(daily_crsp_path + 'gibbs_beta.csv', index_col=0).astype(float)
# df_varu = pd.read_csv(daily_crsp_path + 'gibbs_varu.csv', index_col=0).astype(float)
#
# # Create Gibbs
# # Reset the index to turn the multi-index into columns. Group by 'year' and calculate the mean for each 'permno'
# gibbs_cost = df_cost.astype(float).groupby(level=0).mean()
# gibbs_beta = df_beta.astype(float).groupby(level=0).mean()
# gibbs_varu = df_varu.astype(float).groupby(level=0).mean()
#
#
# # Load test data
# crspgibbs = pd.read_csv('/scratch/jlaws13/AA_Data/Gibbs/crspgibbs.csv', low_memory=False)
# # Keeping the first occurrence
# no_duplicates = crspgibbs.groupby(['year', 'permno']).mean().reset_index()
# test_cost = pd.pivot(no_duplicates, index='year', columns='permno', values='c')
# test_beta = pd.pivot(no_duplicates, index='year', columns='permno', values='beta')
# test_varu = pd.pivot(no_duplicates, index='year', columns='permno', values='varu')
#
#
# # Aligning with my dataframe
# test_cost = test_cost.loc[params.sample_start:params.sample_end]
# test_beta = test_beta.loc[params.sample_start:params.sample_end]
# test_varu = test_varu.loc[params.sample_start:params.sample_end]
# test_cost.columns = test_cost.columns.astype(str)
# test_beta.columns = test_beta.columns.astype(str)
# test_varu.columns = test_varu.columns.astype(str)
# # This adds any missing columns from df_cost into test_cost with NaN values
# test_cost = test_cost.reindex(columns=df_cost.columns, fill_value=np.nan)
# test_beta = test_beta.reindex(columns=df_cost.columns, fill_value=np.nan)
# test_varu = test_varu.reindex(columns=df_cost.columns, fill_value=np.nan)
#
#
# correlation_cost = {}
# correlation_beta = {}
# correlation_varu = {}
# for col in df_cost.columns:
#     if len(gibbs_beta[col].dropna()) > 4:
#         correlation_cost[col] = gibbs_cost[col].dropna().corr(test_cost[col].dropna())
#         correlation_beta[col] = gibbs_beta[col].dropna().corr(test_beta[col].dropna())
#         correlation_varu[col] = gibbs_varu[col].dropna().corr(test_varu[col].dropna())
#     else:
#         correlation_cost[col] = np.nan
#         correlation_beta[col] = np.nan
#         correlation_varu[col] = np.nan
#
# correlation_cost = pd.DataFrame(list(correlation_cost.items()), columns=['permno', 'correlation'])
# correlation_beta = pd.DataFrame(list(correlation_beta.items()), columns=['permno', 'correlation'])
# correlation_varu = pd.DataFrame(list(correlation_varu.items()), columns=['permno', 'correlation'])
# print(f"Cost correlation = {correlation_cost['correlation'].mean()}")
# print(f"Beta correlation = {correlation_beta['correlation'].mean()}")
# print(f"Varu correlation = {correlation_varu['correlation'].mean()}")
#
#
