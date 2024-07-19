import numpy as np
import pandas as pd
import os
import statsmodels.api as sm


def estFactorRegs(params, pret, dates, factorModel=4, **kwargs):
    """
    This function performs factor model regressions on input portfolio returns
    and returns the results in the form of a dictionary containing various
    statistics, such as excess returns, t-stats, Sharpe ratios, information
    ratios, and other relevant metrics.

    Parameters:
    ----------
    pret : array-like
        A matrix of portfolio returns.
    dates : array-like
        A vector of dates corresponding to the portfolio returns.
    factorModel : int, optional (default=4)
        Factor model code (1: CAPM, 3: FF3 factor, 4: FF4 factor,
        5: FF5 factor, 6: FF6 factor).
    **kwargs : keyword arguments, optional
        - 'addLongShort': int (default=1)
            Flag equal to 0 or 1 indicating whether to add a long/short portfolio.

        - 'inputIsExcessReturn': int (default=0)
            Flag equal to 1 or 0 indicating whether the input is excess return.

    Returns:
    -------
    res : dict
        A dictionary containing the following results:
            - 'xret': array-like
                A vector of portfolio excess returns.

            - 'txret': array-like
                A vector of t-stats on the portfolio excess returns.

            - 'alpha': array-like
                A vector of alphas.

            - 'talpha': array-like
                A vector of t-stats of the alphas.

            - 'sharpe': array-like
                A vector of Sharpe ratios.

            - 'info': array-like
                A vector of information ratios.

            - 'pret': array-like
                A matrix containing the time-series of portfolio RAW returns.

            - 'factorModel': int
                A scalar indicating the factor model used.

            - 'nFactors': int
                A scalar indicating the number of factors.

            - 'loadings': array-like
                A matrix with factor loadings.

            - 'r2': array-like
                A vector of adjusted R-squared's from factor model regressions.

            - 'resid': array-like
                A matrix of residuals from factor model regressions (reduced size).
    """

    # Set dataPaths
    crspFolder = params.crspFolder + os.sep
    crspFolderDaily = params.daily_crsp_folder + os.sep

    # Default parameter values for **kwargs
    p = {
        'addLongShort': 1,
        'inputIsExcessReturn': 0,
    }

    # Update parameters with user-specified values (if provided).
    for key, value in kwargs.items():
        if key in p:
            p[key] = value

    # Check if the factor model code is correct
    if factorModel not in {1, 2, 3, 4, 5, 6}:
        raise ValueError("Factor model must be 1, 3, 4, 5, 6, or a user-defined matrix.")

    # Store the number of portfolios
    numDates, numPtfs = pret.shape

    # Make sure dates are integers
    dates = dates.astype(int)

    # Check if daily dates
    if len(dates[0].astype(str)) == 6: # in this case, we are dealing with monthly data
        ff = pd.read_csv(crspFolder + 'ff.csv', index_col='dates')
        ff = ff.loc[dates] # align the factor model data with the portfolio return dates

    elif len(dates[0].astype(str)) == 8: # in this case we are dealing with daily data
        dff = pd.read_csv(crspFolderDaily + 'dff.csv', index_col='dates')
        dff = dff.loc[dates] # align the factor model data with the portfolio return dates
        rf = dff.drf
        ffdates = dff.dffdates
        mkt = dff.dmkt
        smb = dff.dsmb
        smb2 = dff.smb2
        hml = dff.dhml
        umd = dff.dumd
        cma = dff.dcma
        rmw = dff.drmw

    else:
        raise ValueError("Unknown dates format for factor regressions")

    # Calculate excess returns if needed, i.e., unless the portfolio return has already had the rf subtracted out.
    if p['inputIsExcessReturn'] == 0:
        pret = pret - ff['rf'].values[:, np.newaxis]

    # Check if we need to add the long/short portfolio
    if p['addLongShort'] != 0:
        long_short_ptf = pret[:, -1] - pret[:, 0]
        pret = np.column_stack((pret, long_short_ptf))
        numPtfs = numPtfs + 1

    # Set up the factor models
    if isinstance(factorModel, int):
        if factorModel == 1:
            x = sm.add_constant(ff['mkt'])
            labels = ['mkt']
        elif factorModel == 2:
            x = sm.add_constant(ff['mkt', 'smb'])
            labels = ['mkt', 'smb']
        elif factorModel == 3:
            x = sm.add_constant(ff[['mkt', 'smb', 'hml']])
            labels = ['mkt', 'smb', 'hml']
        elif factorModel == 4:
            x = sm.add_constant(ff[['mkt', 'smb', 'hml', 'umd']])
            labels = ['mkt', 'smb', 'hml', 'umd']
        elif factorModel == 5:
            x = sm.add_constant(ff[['mkt', 'smb', 'hml', 'rmw', 'cma']])
            labels = ['mkt', 'smb', 'hml', 'rmw', 'cma']
        elif factorModel == 6:
            x = sm.add_constant(ff[['mkt', 'smb', 'hml', 'umd', 'rmw', 'cma']])
            labels = ['mkt', 'smb', 'hml', 'umd', 'rmw', 'cma']
        else:
            raise ValueError("Invalid factor model. Must be 1, 3, 4, 5, or 6.")

    else: # user-defined factor model
        x = sm.add_constant(factorModel)

    # Run factor model regressions
    nFactors = x.shape[1] - 1
    alpha = np.zeros((numPtfs,))
    t_alpha = np.zeros((numPtfs,))
    t_factors = np.zeros((numPtfs, nFactors))
    r2 = np.zeros((numPtfs,))
    resid = np.zeros_like(pret)
    loadings = np.zeros((numPtfs, nFactors))

    for i in range(numPtfs):
        y = pret[:, i]
        # print(y.shape)
        model = sm.OLS(y, x, missing='drop').fit()
        # print("HERE")
        for j in range(nFactors):
            t_factors[i, j] = model.tvalues.iloc[j+1] # j+1 because the first t-stat is for the constant that we added above.
        alpha[i] = model.params.iloc[0]  # The matlab code multiplies alpha and xret (see below) by 100 to put it into
        # percent terms, but then this creates a lot of unnecessary dividing and multiplying by 100 throughout other
        # functions.
        t_alpha[i] = model.tvalues.iloc[0]
        r2[i] = model.rsquared_adj
        resid[:len(model.resid), i] = model.resid # TODO:Note Because we have to drop the missing values we end up with a mismatch between the sizes of pret and resid. This is a temporary workaround but should be investigated further.
        loadings[i, :] = model.params.iloc[1:]

    # Calculate mean excess returns, t-stats, and annualized Sharpe ratios, and information ratios
    xret = np.nanmean(pret, axis=0)
    txret = xret / (np.nanstd(pret, axis=0) / np.sqrt(numDates))
    sharpe = xret / np.nanstd(pret, axis=0) * np.sqrt(12)  # Annualized
    info = alpha / np.nanstd(resid, axis=0) * np.sqrt(12)  # Annualized

    # Store the results in the output dictionary
    res = {
        'xret': xret,
        'txret': txret,
        'alpha': alpha,
        'talpha': t_alpha,
        'sharpe': sharpe,
        'info': info,
        'pret': pret,
        'factorModel': factorModel,
        'factorLabels': labels,
        'factors': np.array(x.iloc[:, 1:]),
        'nFactors': nFactors,
        'factorLoadings': loadings,
        'tfactors': t_factors,
        'r2': r2,
        'resid': resid
    }

    return res

