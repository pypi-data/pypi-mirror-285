import pandas as pd
import numpy as np
import os
from datetime import datetime
import statsmodels.api as sm
from statsmodels.regression.rolling import RollingOLS
from multiprocessing import Pool


def calculate_beta_for_column(permno, dxret_slice, dxret_winsorized_slice, x1, x2):
    print(f"Processing permno {permno}")
    # i = dxret_slice.name  # Assuming you pass the Series with its original name
    if dxret_slice.count() >= 120:
        first_numeric = dxret_slice.first_valid_index()
        last_numeric = dxret_slice.last_valid_index()
        y1 = dxret_slice[first_numeric:last_numeric]

        # Using min() because occasionally the window is smaller than 252 but has 120 observations.
        res = RollingOLS(y1, x1.loc[first_numeric:last_numeric], window=min(y1.shape[0], 252), min_nobs=120).fit()
        ols_beta = res.params.iloc[:, 1]
        ols_error = res.bse.iloc[:, 1]

        res = RollingOLS(y1, x2.loc[first_numeric:last_numeric], window=min(y1.shape[0], 252), min_nobs=120).fit(
            params_only=True).params
        dim_beta = res.iloc[:, 1] + res.iloc[:, 2]

        y2 = dxret_winsorized_slice[first_numeric:last_numeric]
        sw_beta = RollingOLS(y2, x1.loc[first_numeric:last_numeric], window=min(y1.shape[0], 252),
                             min_nobs=120).fit(params_only=True).params.iloc[:, 1]

        return (permno, first_numeric, last_numeric, ols_beta, ols_error, dim_beta, sw_beta)
    else:
        return (permno, None, None, np.nan, np.nan, np.nan, np.nan)


def makeBetas(params):
    # Timekeeping
    print(f"\nMaking betas. Run started at {datetime.now()}\n")

    crsp_path = params.crspFolder + os.sep
    daily_crsp_path = params.daily_crsp_folder + os.sep
    ff_path = params.ff_data_folder + os.sep

    "Start with the Frazzini - Pedersen betas"
    print(f"\nMaking Frazzini-Pedersen (2014) betas first.\n")

    # load necessary inputs
    dret = pd.read_parquet(daily_crsp_path + 'dret.parquet').sort_index().astype(float)
    ff = pd.read_csv(crsp_path + 'ff.csv', index_col=0).astype(float)
    dff = pd.read_csv(ff_path + 'dff.csv', index_col=0).astype(float)
    ret = pd.read_csv(crsp_path + 'ret.csv', index_col=0).astype(float)

    # Convert to datetime indices
    dret.index = pd.to_datetime(dret.index, format='%Y-%m-%d')
    dff.index = pd.to_datetime(dff['dates'], format='%Y%m%d')
    ret.index = pd.to_datetime(ret.index.astype(int), format='%Y%m')

    # Store the excess stock returns
    rptdRf = np.tile(dff['rf'], (ret.shape[1], 1)).T
    dxret = dret - rptdRf

    # Store the 3-day excess returns and market returns
    # dret3 = (1 + dxret).rolling(window=3).cumprod() - 1
    dret3 = (1 + dxret).shift(1) * (1 + dxret).shift(2) * (1 + dxret).shift(3) - 1
    dmkt3 = (1 + dff['mkt']).shift(1) * (1 + dff['mkt']).shift(2) * (1 + dff['mkt']).shift(3) - 1

    # Compute rolling 1-year standard deviations
    stock_std = np.log(1 + dxret).rolling(window=252, min_periods=120).std()
    mkt_std = np.log(1 + dff['mkt']).rolling(window=252, min_periods=120).std()

    # Compute rolling 5-year correlations of 3-day excess returns with 3-day market returns
    corr = np.log(1 + dret3).rolling(window=252 * 5, min_periods=750).corr(np.log(1 + dmkt3))

    # Calculate beta = rho * (sigma_i / sigma_m)
    betas = corr * stock_std / np.tile(mkt_std, (dret.shape[1], 1)).T

    # Apply the shrinkage towards 1; Reduce the impact of extreme values.
    bfp = 0.6 * betas + 0.4

    bfp.columns = bfp.columns.astype(str)
    bfp.to_parquet(crsp_path + 'bfp.parquet')

    print("\nNow making Ivo's OLS, Dimson Correction, Vasicek shrinkage, 'standard', and Ivo Welch betas.\n")

    """
    Ivo's OLS benchmark - 1 year of daily data, 1 mkt lag, no shrinkage.
    Dimson correction - add one more lag of mkt.
    Vasicek shrinkage - similar to what LSY use.
    Standard - 1 market lag, shrinkage to 1.
    Ivo Welch's betas
    """
    # Calculate lagged market returns
    lagged_dmkt = pd.DataFrame(dff['mkt'], index=dff.index).shift(1)

    # Calculate the Ivo Welch winsorized excess returns
    lower_bound = np.multiply(-2, dff['mkt'])
    upper_bound = np.multiply(4, dff['mkt'])
    lower_bound.index = dxret.index
    upper_bound.index = dxret.index

    # Winsorize the excess returns data
    # Note: `clip` method is used for winsorization
    dxret_winsorized = dxret.clip(lower=lower_bound, upper=upper_bound, axis=0)

    # Create empty arrays to store the betas and ols errors
    betas_ols = pd.DataFrame(index=dxret.index, columns=dxret.columns)
    betas_ols_errors = pd.DataFrame(index=dxret.index, columns=dxret.columns)
    betas_dim = pd.DataFrame(index=dxret.index, columns=dxret.columns)
    betas_sw = pd.DataFrame(index=dxret.index, columns=dxret.columns)
    betas_vck = pd.DataFrame(index=dxret.index, columns=dxret.columns)

    # Create lagged excess return matrix
    # x1 = pd.DataFrame(sm.add_constant(dff['mkt']), index=dret.index)
    x1 = pd.DataFrame(sm.add_constant(dff['mkt']))
    x1.index = dret.index
    x2 = x1.merge(lagged_dmkt, how='outer', on=x1.index).iloc[:, 1:]
    x2.index = dret.index

    # Calculate OLS, Dimson , and Ivo Welch betas
    if not params.num_cpus > 1:
        for i, permno in enumerate(dret.columns):
            print(i, permno)
            if dxret.iloc[:, i].count() >= 120:
                # Benchmark OLS betas
                # betas_ols[:, i] = RollingOLS(dxret.iloc[:, i], x1, window=252, min_nobs=120).fit(params_only=True).params.iloc[:, 1]
                first_numeric = dxret.iloc[:, i].first_valid_index()
                last_numeric = dxret.iloc[:, i].last_valid_index()
                y1 = dxret.iloc[:, i][first_numeric:last_numeric]
                res = RollingOLS(y1, x1[first_numeric:last_numeric], window=min(y1.shape[0], 252), min_nobs=120).fit()
                betas_ols.loc[first_numeric:last_numeric, permno] = res.params.iloc[:, 1]
                betas_ols_errors.loc[:, i] = res.bse.iloc[:, 1]

                # Dimson correction - add 1 lag of mkt
                res = RollingOLS(y1, x2[first_numeric:last_numeric], window=min(y1.shape[0], 252), min_nobs=120).fit(params_only=True).params
                betas_dim.loc[first_numeric:last_numeric, i] = res.iloc[:, 1] + res.iloc[:, 2]

                # Ivo's betas - use the winsorized returns (dxretw)
                y2 = dxret_winsorized.iloc[:, i][first_numeric:last_numeric]
                betas_sw.loc[first_numeric:last_numeric, i] = RollingOLS(y2, x1[first_numeric:last_numeric], window=min(y1.shape[0], 252), min_nobs=120).fit(params_only=True).params.iloc[:, 1]
            else:
                continue

    else:
        args = []
        for permno in dret.columns:
            dxret_slice = dxret[permno]
            dxret_winsorized_slice = dxret_winsorized[permno]
            args.append((permno, dxret_slice, dxret_winsorized_slice, x1, x2))

        with Pool(os.cpu_count()) as pool:
            results = pool.starmap(calculate_beta_for_column, args)

        # Process the results to update the DataFrames

        for i in range(len(results)):
            print(i)
            permno, first_numeric, last_numeric, ols_beta, ols_error, dim_beta, sw_beta = results[i]
            if first_numeric is not None:
                betas_ols.loc[first_numeric:last_numeric, permno] = ols_beta
                betas_ols_errors.loc[first_numeric:last_numeric, permno] = ols_error
                betas_dim.loc[first_numeric:last_numeric, permno] = dim_beta
                betas_sw.loc[first_numeric:last_numeric, permno] = sw_beta


    betas_ols = betas_ols.astype(float)
    betas_ols_errors = betas_ols_errors.astype(float)

    # Calculate the Vasicek shrinkage betas
    for i in range(betas_ols.shape[0]):  # Loop over time periods
        errors = betas_ols_errors.iloc[i, :].values
        betas = betas_ols.iloc[i, :].values
        # print(np.count_nonzero(~np.isnan(betas)))
        if np.count_nonzero(~np.isnan(betas)) > 2:
            sigmaSqI = errors ** 2
            sigmaSqT = np.nanvar(betas)
            wvck = sigmaSqT / (sigmaSqI + sigmaSqT)
            mean_beta = np.nanmean(betas)
            betas_vck.iloc[i, :] = wvck * betas + (1 - wvck) * mean_beta

    # Calculate standard betas
    betas_std = 0.6*betas_dim + 0.4

    # pd.DataFrame(betas_std, index=dret.index, columns=dret.columns).to_csv(crsp_path + 'betas_std.csv')
    # pd.DataFrame(betas_ols, index=dret.index, columns=dret.columns).to_csv(crsp_path + 'betas_ols.csv')
    # pd.DataFrame(betas_sw, index=dret.index, columns=dret.columns).to_csv(crsp_path + 'betas_sw.csv')
    # pd.DataFrame(betas_vck, index=dret.index, columns=dret.columns).to_csv(crsp_path + 'betas_vck.csv')
    # pd.DataFrame(betas_dim, index=dret.index, columns=dret.columns).to_csv(crsp_path + 'betas_dim.csv')

    betas_std.to_parquet(crsp_path + 'betas_std.parquet')
    betas_ols.to_parquet(crsp_path + 'betas_ols.parquet')
    betas_sw.to_parquet(crsp_path + 'betas_sw.parquet')
    betas_vck.to_parquet(crsp_path + 'betas_vck.parquet')
    betas_dim.to_parquet(crsp_path + 'betas_dim.parquet')

    print(f"Set-up is complete. Run ended at {datetime.now()}")


if __name__ == "__main__":
    from AssayingAnomalies import Config
    params = Config().load_params()
    makeBetas(params)
