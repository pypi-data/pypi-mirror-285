import numpy as np
from scipy.stats import f

"""
GRS Statistic vs. F-Statistic
-GRS Statistic: This is a specific test statistic used to test the null hypothesis that all alphas (excess returns not 
explained by the factors) across a group of portfolios are simultaneously zero. The GRS statistic is designed to account
for the estimation risk inherent in using estimated factors and residuals rather than known quantities.
-F-Statistic: In the context of the GRS test, the GRS statistic is structured to follow an F-distribution under the null
 hypothesis. This allows you to use the properties of the F-distribution to determine the p-value associated with the 
 observed GRS statistic. The calculation of the GRS statistic involves a formula that inherently adjusts for multiple 
 portfolios and the multiple factors used, allowing it to fit an F-distribution.
 In the context of the calculation, GRS statistics == F-statistics
"""
def grs_test_p(results):
    # Initialize array to hold degrees of freedom, f-stats (GRS stats), and p-values
    dfs = []
    f_stats = []
    p_values = []

    # Store key variables
    nPtfs = results['nPorts']  # Number of portfolios
    nMonths = np.sum(np.isfinite(results['pret'][:, 0]))  # Number of non-NaN months
    nFactors = results['nFactors']  # Number of factors

    # Extract factor returns and compute means
    factor_returns = np.array(results['factors'])
    mean_factors = np.mean(factor_returns, axis=0)

    # Handle the factor covariance matrix
    if nFactors == 1:
        cov_factors = np.array([[np.var(factor_returns, ddof=1)]])
    else:
        cov_factors = np.cov(factor_returns, rowvar=False)

    # Calculate the inverse of the covariance matrix
    cov_factors_inv = np.linalg.inv(cov_factors)

    # Compute residuals and alphas
    alpha = np.array(results['alpha'])[:nPtfs]
    resid = np.array(results['resid'])[:, :nPtfs]
    cov_resid = np.cov(resid, rowvar=False)
    cov_resid_inv = np.linalg.inv(cov_resid)

    # Numerator of the GRS statistic
    numer = alpha.T @ cov_resid_inv @ alpha  # Note: The matlab code divides
    # by 100^2 because they multiply alpha and xret by 100 in the estFactorRegs function to put it into percent
    # terms. I did not do that, so no need to correct back here.

    # Denominator of the GRS statistic
    denom = 1 + mean_factors.T @ cov_factors_inv @ mean_factors

    # Calculate GRS statistic
    df = (nPtfs, nMonths - nPtfs - nFactors)
    dfs.append(df)
    Fstats = (dfs[0][1] / dfs[0][0]) * (numer / denom)  # The GRS statistic rescaled so that it follows an
    # F-distribution
    f_stats.append(Fstats)
    pvals = 1 - f.cdf(Fstats, dfs[0][0], dfs[0][1])
    p_values.append(pvals)

    # Reconstruct returns from the factor loadings, factors, and residuals and the re-calculate the GRS stat.
    factor_loadings = results['factorLoadings'][:nPtfs]
    a = np.tile(alpha.T, (nMonths, 1))
    resxret = factor_returns @ factor_loadings.T + a + resid

    # Get the covariance and its inverse
    cov_resxret = np.cov(resxret, rowvar=False)
    cov_resxret_inv = np.linalg.inv(cov_resxret)

    # Calculate the numerator. The denominator is set to 1.
    numer = results['xret'][:nPtfs].T @ cov_resxret_inv @ results['xret'][:nPtfs]

    # Calculate the GRS statistic, degrees of freedom, and p-values of f-stats
    df = (nPtfs, nMonths - nPtfs)
    dfs.append(df)
    Fstats = (dfs[1][1] / dfs[1][0]) * numer
    f_stats.append(Fstats)
    pvals = 1 - f.cdf(Fstats, dfs[1][0], dfs[1][1])
    p_values.append(pvals)

    return p_values, f_stats, dfs


# # Test the function
# import scipy.io
# import os
# from AssayingAnomalies import Config
# from AssayingAnomalies.Functions.makeBivSortInd import makeBivSortInd
#
# params = Config()
# params.prompt_user()
# params.make_folders()
# path = r"C:\Users\josh\OneDrive - University at Buffalo\Desktop\Spring_2023\AssayingAnomalies-main\AssayingAnomalies-main\Data" + os.sep
# R = scipy.io.loadmat(path + 'R.mat')['R']
# # R = pd.read_csv(path + 'R.csv', index_col=0)
# me = scipy.io.loadmat(path + 'me.mat')['me']
# NYSE = scipy.io.loadmat(path + 'NYSE.mat')['NYSE']
# ind1 = makeBivSortInd(me, 5, R, 5)
# ret = scipy.io.loadmat(path + 'ret.mat')['ret']
# dates = scipy.io.loadmat(path + os.sep + 'CRSP' + os.sep + 'dates.mat')['dates']
# dates = dates.flatten()
#
# # Run a univariate sort to get the underlying portfolios
# res = runUnivSort(params=params, ret=ret, ind=ind1, mcap=me, dates=dates)
