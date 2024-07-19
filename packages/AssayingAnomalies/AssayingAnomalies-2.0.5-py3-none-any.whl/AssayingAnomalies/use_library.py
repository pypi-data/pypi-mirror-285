import numpy as np
import pandas as pd
import os
from AssayingAnomalies import Config
import AssayingAnomalies.Functions as aa
import statsmodels.api as sm
import requests
from io import BytesIO
from zipfile import ZipFile
import matplotlib.pyplot as plt


"""
This file contains a tutorial on how to implement various basic asset pricing techniques using the Toolkit. These
include univariate sorts, bivariate sorts, Fama-MacBeth regressions, and accounting for transaction costs.
"""

# First load in your parameters
params = Config()
params = params.load_params()

# Load all variables we will need
ret = pd.read_csv(params.crspFolder + os.sep + 'ret.csv', index_col=0).astype(float)
me = pd.read_csv(params.crspFolder + os.sep + 'me.csv', index_col=0).astype(float)
dates = pd.read_csv(params.crspFolder + os.sep + 'dates.csv', index_col=0).astype(float)
NYSE = pd.read_csv(params.crspFolder + os.sep + 'NYSE.csv', index_col=0).astype(float)  # Load the NYSE indicator mat.
exchcd = pd.read_csv(os.path.join(params.crspFolder, 'exchcd.csv'), index_col=0)  # Load the exchcode matrix
tcosts = pd.read_parquet(os.path.join(params.crspFolder, 'tcosts.parquet'))
bm = pd.read_csv(os.path.join(params.compFolder, 'bm.csv'), index_col=0)


"Let's perform a number of univariate sorts and project these portfolio returns onto market, size, prof, "
"and mom factors"
# Quintile sort on size. The smallest fifth according to market cap go in portfolio 1, the next
# 5th in portfolio 2, and so on.
ind = aa.makeUnivSortInd(var=-me, ptfNumThresh=5)
results_1 = aa.runUnivSort(params=params, ret=ret, ind=ind, mcap=me, dates=dates, plotFigure=0)

# Quintile sort, market-capitalization breaks ensure that each portfolio has roughly the same total market cap. The
# function calculates breakpoints that account for the cumulative distribution of market equity. For example,
# it determines where the cumulative market equity of the sorted assets reaches approximately 20%, 40%, 60%, 80%,
# and 100% of the total market equity. These points are used as breakpoints for forming the portfolios.
ind = aa.makeUnivSortInd(var=-me, ptfNumThresh=5, portfolioMassInd=me.copy())
results_2 = aa.runUnivSort(params=params, ret=ret, ind=ind, mcap=me, dates=dates, plotFigure=0)

# Tertile Fama-French-style sort
ind = aa.makeUnivSortInd(var=-me, ptfNumThresh=[30, 70])
results_3 = aa.runUnivSort(params=params, ret=ret, ind=ind, mcap=me, dates=dates, plotFigure=0)

# Decile sort, NYSE market cap breaks
ind = aa.makeUnivSortInd(var=-me, ptfNumThresh=10, breaksFilterInd=NYSE)
results_4 = aa.runUnivSort(params=params, ret=ret, ind=ind, mcap=me, dates=dates, plotFigure=0)

# Decile sort, NASDAQ cap breaks. Note that NASDAQ starts in 1973.
nasdaq = exchcd[exchcd==3].fillna(0)/3
ind = aa.makeUnivSortInd(var=-me, ptfNumThresh=10, breaksFilterInd=nasdaq)
results_5 = aa.runUnivSort(params=params, ret=ret, ind=ind, mcap=me, dates=dates, plotFigure=0)

"Now let's keep the same 5 portfolios but play around with different holding periods, factor models, and weightings"
ind = aa.makeUnivSortInd(var=-me, ptfNumThresh=5)
results_1 = aa.runUnivSort(params, ret, ind, me, dates, plotFigure=0)

# Equal-weighted portfolios instead of value weighted.
results_6 = aa.runUnivSort(params, ret, ind, me, dates, plotFigure=0, weigting='e')

# Default holding period is 1 month, but what if we re-balance every other month instead?
results_7 = aa.runUnivSort(params, ret, ind, me, dates, plotFigure=0, holdingPeriod=2)

# 6-factor model (default is 4)
results_8 = aa.runUnivSort(params, ret, ind, me, dates, factorModel=6)

# Use a custom date range instead of full sample. Need to pass timePeriod = [YYYYMM, YYYYMM] or [YYYYMM]
start = 196307
end = 202107
results_9 = aa.runUnivSort(params, ret, ind, me, dates, timePeriod=[start, end])
results_10 = aa.runUnivSort(params, ret, ind, me, dates, timePeriod=[200901])

# Estimate factor loadings but incorporating trading costs
results_11 = aa.runUnivSort(params, ret, ind, me, dates, tcosts=tcosts)

"We can also do bivariate sorts"
R = pd.read_csv(os.path.join(params.crspFolder, 'R.csv'), index_col=0)  # First let's load the momentum dataframe.

# 5x5 sort on size and momentum
ind = aa.makeBivSortInd(var1=me, ptfNumThresh1=5, var2=R, ptfNumThresh2=5)
res1, cond_res1 = aa.runBivSort(params, ret, ind, 5, 5, me, dates)

# 5x5 sort on size and momentum, using NYSE breakpoints.
ind = aa.makeBivSortInd(var1=me, ptfNumThresh1=5, var2=R, ptfNumThresh2=5, breaksFilterInd=NYSE)
res2, cond_res2 = aa.runBivSort(params, ret, ind, 5, 5, me, dates)

# 5x5 sort on size and momentum, ensure each portfolio has roughly the same market cap.
ind = aa.makeBivSortInd(var1=me, ptfNumThresh1=5, var2=R, ptfNumThresh2=5, portfolioMassInd=me)
res3, cond_res3 = aa.runBivSort(params, ret, ind, 5, 5, me, dates)

# 2x3 (FF style) sorts on size and momentum
ind = aa.makeBivSortInd(var1=me, ptfNumThresh1=2, var2=R, ptfNumThresh2=[30, 70])
res4, cond_res4 = aa.runBivSort(params, ret, ind, 2, 3, me, dates)


"The runBivSort function has a built in GRS test. We can use a univariate indicator to replicate "
"Campbell-Lo-MacKinlay Table 5.3 (Gibbons, Ross, Shanken (89) Wald test results)"
me_clm = me[exchcd.isin([1, 2])]  # CLM only use NYSE and AMEX stocks, i.e. exchange code 1 or 2.
ind_clm = aa.makeUnivSortInd(me, 10)
res_clm, _ = aa.runBivSort(params, ret, ind_clm, 5, 2, me_clm, dates, timePeriod=[196412, 199412],
                           factorModel=1)


"Examples of Fama-MacBeth Regressions"
# Load the book to market ratios and estimate returns on book to market and momentum.
res_fm_1 = aa.run_Fama_MacBeth(100*ret, [bm, R], dates, labels=['Value', 'Momentum'])

# Change the number of minimum observations (thereby kicking out more stocks)
res_fm_2 = aa.run_Fama_MacBeth(100*ret, [np.log(me), R], dates, minobs=1000)

# Use weighted least squares
res_fm_3 = aa.run_Fama_MacBeth(100*ret, [np.log(me), R], dates, weightMatrix=me)

# Use Newey-West standard errors
res_fm_4 = aa.run_Fama_MacBeth(100*ret, [np.log(me), R], dates, neweyWestLags=12)

# Use sub-sample
res_fm_5 = aa.run_Fama_MacBeth(100*ret, [np.log(me), R], dates, timePeriod=[196307, 202107])

# Trim or winsorize
res_fm_6 = aa.run_Fama_MacBeth(100*ret, [np.log(me), R], dates, trimIndicator=1)
res_fm_7 = aa.run_Fama_MacBeth(100*ret, [np.log(me), R], dates, winsorTrimPctg=5)


"""
Fama French (1993)
"""
start = 196306
end = 199112
bm_ff93 = bm[bm > 0]
ind_ff93 = aa.makeBivSortInd(me, 5, bm_ff93, 5, sort_type='unconditional',
                             breaksFilterInd=NYSE)
res_ff93, cond_res_ff93 = aa.runBivSort(params, ret, ind_ff93, 5, 5, me, dates, timePeriod=[start, end])

# Download the 25 portfolios from Ken French's data library
file_url = 'https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/25_Portfolios_5x5_CSV.zip'
response = requests.get(file_url)
with ZipFile(BytesIO(response.content)) as z:
    # Debugging: List all files in the zip archive
    file_list = z.namelist()
    print("Files in the zip archive:", file_list)

    # Check if there are any CSV files (case-insensitive)
    csv_files = [name for name in file_list if name.lower().endswith('.csv')]
    if not csv_files:
        raise ValueError("No CSV files found in the zip archive")

    # Extract the first CSV file found
    ff25_file_name = csv_files[0]
    z.extract(ff25_file_name)

# Read in the 25 portfolios, skip the first 15 rows of useless text.
FF25factors = pd.read_csv(f'{ff25_file_name}', skiprows=15, index_col=0)

# The daily returns are appended to the bottom of the dataframe, we want to remove those plus align the dates with the
# desired date range. Finally, divide by 100 to put back in decimal format.
e = FF25factors[FF25factors.isna().any(axis=1)].index[0]
ff25 = FF25factors.loc[:e, :].iloc[:-1, :]
ff25 = ff25.loc[str(start):str(end), :]
ff25 = ff25.astype(float)
ff25 = ff25 / 100

# Plot a scatter plot with the average returns against ours
plt.figure()
avg_rep = np.nanmean(res_ff93['pret'], axis=0)[:-1]  # Remove the long/short portfolio
avg_ff_lib = np.nanmean(ff25, axis=0)
plt.scatter(avg_rep, avg_ff_lib, alpha=0.5)
plt.xlabel('Replicating Portfolios')
plt.ylabel('Ken French Data Library')
plt.title('Average Returns to 25 size/btm portfolios')
plt.axline((0, 0), slope=1, color='r', linestyle='--')
plt.show()

"""
Fama MacBeth (1973)
The testing procedure is as follows:
 1. For a given period (e.g. 1926 - 1929), the estimate betas for each stock and form 20 portfolios.
 2. Over the next period (1930 - 1934), they re-estimate the betas and average within portfolio to get the portfolio 
 betas. 
 3. To control for delisting, they re-calculate the portfolio betas each month then re-estimate stock betas at the end
  of each year in the testing period (1935-38). This results in 48 cross-sectional estimations of the SML from:
  R_pt = gamma_{0,t} + gamma_{1,t}beta_{p,t-1} + eta_{p,t}
 4. Repeat 1-3 beginning with a different starting period to arrive at 390 estimates for SML.
"""
# FM use returns not adjusted for delisting
ret_x_dl = pd.read_csv(os.path.join(params.crspFolder, 'ret_x_dl.csv'), index_col=0)
ret_x_dl = ret_x_dl[exchcd == 1]  # keep only NYSE firms.

# Make datetime dates
datetime_dates = pd.to_datetime(ret_x_dl.index)

# Load the ff factors
ff = pd.read_csv(os.path.join(params.crspFolder, 'ff.csv'), index_col=0)
rf = ff['rf']
rf.index = ret_x_dl.index  # match indices

# Get the equal-weighted market excess return vector
ew_NYSE = ret_x_dl.mean(axis=1, skipna=True) - rf

# Constants
nMonths, nStocks = ret_x_dl.shape
nPtf = 20

# Define time periods
startInd = datetime_dates.get_loc('192912')
endInd = datetime_dates.get_loc('196112')

# Initialize the portfolio indicator and individual firm betas
ind = pd.DataFrame(0, index=ret_x_dl.index, columns=ret_x_dl.columns)
ibetas = pd.DataFrame(np.nan, index=ret_x_dl.index, columns=ret_x_dl.columns)

for i in range(startInd, endInd, 48):
    s = max(2, i - 83)
    pfPeriod = slice(datetime_dates[s], datetime_dates[i])
    iePeriod = slice(datetime_dates[i + 1], datetime_dates[i + 60])
    tPeriod = slice(datetime_dates[i + 60], datetime_dates[i + 107])

    # Find stocks with adequate return history
    hor_ind = (ret_x_dl.loc[pfPeriod].count() >= 48) & (ret_x_dl.loc[iePeriod].count() >= 60)

    # Portfolio formation betas
    ptf_formation_betas = pd.Series(np.nan, index=ret_x_dl.columns)
    valid_stocks = hor_ind[hor_ind].index
    for j in valid_stocks:
        y = ret_x_dl.loc[pfPeriod, j] - rf.loc[pfPeriod]
        x = sm.add_constant(ew_NYSE.loc[pfPeriod])
        model = sm.OLS(y, x, missing='drop').fit()
        ptf_formation_betas[j] = model.params[1]

    # Assign portfolios
    ptfRankings = aa.makeUnivSortInd(ptf_formation_betas, nPtf)  # You need to define this function
    ind.loc[tPeriod] = ptfRankings.repeat(48).values.reshape(-1, len(ret_x_dl.columns))

    # Loop over the end-of-years in the testing period to reestimate the betas
    for e in range(i + 61, i + 97, 12):  # Adjusted range to fit the testing period spans
        est_betas = pd.Series(np.nan, index=ret_x_dl.columns)
        for j in valid_stocks:
            y = ret_x_dl.loc[datetime_dates[i + 1]:datetime_dates[e], j] - rf.loc[datetime_dates[i + 1]:datetime_dates[e]]
            x = sm.add_constant(ew_NYSE.loc[datetime_dates[i + 1]:datetime_dates[e]])
            model = sm.OLS(y.dropna(), x.loc[y.index].dropna(), missing='drop').fit()
            est_betas[j] = model.params.get(1)
        # Replicate for each month in the year
        ibetas.loc[datetime_dates[e]:datetime_dates[e + 11]] = np.tile(est_betas.values, (12, 1))

# Clean up the individual firm betas and the portfolio indicator matrix
indToDrop = ret.shift(-1).isna()  # Shift backwards, check for NaN
ibetas[indToDrop] = np.nan
ind[indToDrop] = 0

# Initialize the portfolio beta and return matrices
nMonths, nPtf = ind.shape[1], 20
ptf_betas = pd.DataFrame(np.nan, index=ret.index, columns=range(1, nPtf + 1))
ptf_ret = pd.DataFrame(np.nan, index=ret.index, columns=range(1, nPtf + 1))

# Calculate the average portfolio betas and returns
for i in range(1, nPtf + 1):
    temp_betas = ibetas.copy()
    temp_betas[ind != i] = np.nan
    ptf_betas[i] = temp_betas.mean(axis=1, skipna=True)

    temp_ret = ret.copy()
    temp_ret[ind != i] = np.nan
    ptf_ret[i] = temp_ret.mean(axis=1, skipna=True)

# Convert returns to percentage and run Fama Macbeth regression
y = 100 * ptf_ret
x = ptf_betas
res = aa.run_Fama_MacBeth(y, x, dates, minobs=10, timePeriod=[193501, 196812])

