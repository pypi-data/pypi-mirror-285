import numpy as np
import pandas as pd
from datetime import datetime
import requests
from io import BytesIO
import zipfile
import os
import AssayingAnomalies
from AssayingAnomalies.Functions.makeBivSortInd import makeBivSortInd
from AssayingAnomalies.Functions.runBivSort import runBivSort
import statsmodels.api as sm


def makeCOMPUSTATDerivedVariables(params):
    # Timekeeping
    print(f"\nNow working on making variables derived from COMPUSTAT. Run started at {datetime.now()}.\n")

    # Set dataPaths
    crsp_path = params.crspFolder + os.sep
    comp_path = params.compFolder + os.sep

    # Make Operating costs
    cogs = pd.read_csv(comp_path + 'COGS.csv', index_col=0)
    xsga = pd.read_csv(comp_path + 'XSGA.csv', index_col=0)
    OC = cogs + xsga
    OC.to_csv(comp_path + 'OC.csv')

    # Make Total Debt
    dlc = pd.read_csv(comp_path + 'DLC.csv', index_col=0)
    dltt = pd.read_csv(comp_path + 'DLTT.csv', index_col=0)
    D = dlc + dltt
    D.to_csv(comp_path + 'D.csv')

    # Make Investment. (Cumulative) Investment = property plant and equipment
    ppegt = pd.read_csv(comp_path + 'PPEGT.csv', index_col=0)
    invt = pd.read_csv(comp_path + 'INVT.csv', index_col=0)
    INV = ppegt + invt
    INV.to_csv(comp_path + 'INV.csv')

    # Make free cash-flow = net earnings + depreciation and amortization - changes in working capital - capex
    ni = pd.read_csv(comp_path +'NI.csv', index_col=0)
    dp = pd.read_csv(comp_path + 'DP.csv', index_col=0)
    wcapch = pd.read_csv(comp_path + 'WCAPCH.csv', index_col=0)
    capx = pd.read_csv(comp_path + 'CAPX.csv', index_col=0)
    FCF = ni + dp - wcapch - capx
    FCF.to_csv(comp_path + 'FCF.csv')

    # Make dividends (really it's money returned to equity holders (dividends and buy-backs)
    prstkc = pd.read_csv(comp_path + 'PRSTKC.csv', index_col=0)
    prstkc = prstkc.astype(float).fillna(0)
    prstkpc = pd.read_csv(comp_path + 'PRSTKPC.csv', index_col=0)
    prstkpc = prstkpc.astype(float).fillna(0)
    prstkcc = pd.read_csv(comp_path + 'PRSTKCC.csv', index_col=0)
    prstkcc = prstkcc.astype(float).fillna(0)
    dvc = pd.read_csv(comp_path + 'DVC.csv', index_col=0)
    dvc = dvc.astype(float).fillna(0)
    temp = prstkc - prstkpc
    prstkcc = prstkcc.combine_first(temp) # this combines PRSTKCC with the temp dataframe, such that any missing values in PRSTKCC are replaced by the corresponding values in 'temp'
    DIV = dvc + prstkcc
    DIV.to_csv(comp_path + 'DIV.csv')

    # Make Working capital
    act = pd.read_csv(comp_path + 'ACT.csv', index_col=0)
    lct = pd.read_csv(comp_path + 'LCT.csv', index_col=0)
    WCAP = act - lct
    WCAP.to_csv(comp_path + 'WCAP.csv')

    # Make CFO (cash flow from operations)
    OANCF = pd.read_csv(comp_path + 'OANCF.csv', index_col=0)
    IB = pd.read_csv(comp_path + 'IB.csv', index_col=0)
    DP = pd.read_csv(comp_path + 'DP.csv', index_col=0)
    XIDO = pd.read_csv(comp_path + 'XIDO.csv', index_col=0)
    TXDC = pd.read_csv(comp_path + 'TXDC.csv', index_col=0)
    ESUBC = pd.read_csv(comp_path + 'ESUBC.csv', index_col=0)
    SPPIV = pd.read_csv(comp_path + 'SPPIV.csv', index_col=0)
    FOPO = pd.read_csv(comp_path + 'FOPO.csv', index_col=0)
    RECCH = pd.read_csv(comp_path + 'RECCH.csv', index_col=0)
    INVCH = pd.read_csv(comp_path + 'INVCH.csv', index_col=0)
    APALCH = pd.read_csv(comp_path + 'APALCH.csv', index_col=0)
    TXACH = pd.read_csv(comp_path + 'TXACH.csv', index_col=0)
    AOLOCH = pd.read_csv(comp_path + 'AOLOCH.csv', index_col=0)
    temp = IB + DP # Income before extraordinary items + depreciation and amortization
    temp = temp + XIDO # + extraordinary items and discontinued operations
    temp = temp + TXDC # + deferred taxes (CF)
    temp = temp + ESUBC # + equity in net loss (Earnings)
    temp = temp - SPPIV # - sale of PPE and sale of investments gain (loss)
    temp = temp + FOPO # + funds from operations - Other
    temp = temp + RECCH # + accounts receivable - decrease (increase)
    temp = temp + INVCH # + inventory - decrease (increase)
    temp = temp + APALCH # + accounts payable and accrued liabilities - increase (decrease)
    temp = temp + TXACH # + income taxes - acctued - increase (decrease)
    temp = temp + AOLOCH # + assets and liabi.ities - other (net change)
    CFO = temp.copy()  # operating activities - net cash flow (i.e., CFFO)
    CFO = CFO.combine_first(OANCF)
    CFO.to_csv(comp_path + 'CFO.csv')

    # Make book equity. Start with shareholder's equity
    SEQ = pd.read_csv(comp_path + 'SEQ.csv', index_col=0)
    CEQ = pd.read_csv(comp_path + 'CEQ.csv', index_col=0)
    PSTK = pd.read_csv(comp_path + 'PSTK.csv', index_col=0)
    AT = pd.read_csv(comp_path + 'AT.csv', index_col=0)
    LT = pd.read_csv(comp_path + 'LT.csv', index_col=0)
    SE = SEQ.copy()                          # Shareholder equity
    temp = CEQ + PSTK
    SE[SE.isna()] = temp[SE.isna()]         # Uses common equity + preferred stock if SEQ is missing
    temp = AT - LT
    SE[SE.isna()] = temp[SE.isna()]         # Uses assets - liabilities, if others are missing

    # Make preferred stock
    PSTKRV = pd.read_csv(comp_path + 'PSTKRV.csv', index_col=0)
    PSTKL = pd.read_csv(comp_path + 'PSTKL.csv', index_col=0)
    PSTK = pd.read_csv(comp_path + 'PSTK.csv', index_col=0)
    PS = PSTKRV.copy()
    PS[PS.isna()] = PSTKL[PS.isna()]
    PS[PS.isna()] = PSTK[PS.isna()]
    PS.to_csv(comp_path + 'PS.csv')

    # Make Deferred taxes
    TXDITC = pd.read_csv(comp_path + 'TXDITC.csv', index_col=0)
    TXDB = pd.read_csv(comp_path + 'TXDB.csv', index_col=0)
    ITCB = pd.read_csv(comp_path + 'ITCB.csv', index_col=0)
    DT = TXDITC.copy()
    temp = TXDB + ITCB
    DT[DT.isna()] = temp[DT.isna()]

    # Book equity is shareholder equity + deferred taxes - preferred stock
    BE = SE + (DT - PS)

    "Add in the Davis, Fama and French (1997) book equities (from before the accounting data is available on COMPUSTAT)"
    # First load the dates and permno vectors
    # dates = pd.read_csv(comp_path + 'dates.csv', index_col=0)
    # permno = pd.read_csv(comp_path + 'permno.csv', index_col=0)
    ffurl = 'http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Historical_BE_Data.zip'

    # tricks the host site into thinking the HTTP call is from user instead of machine
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(ffurl, headers=headers)
    # saving the zip file as an object
    zf = zipfile.ZipFile(BytesIO(response.content))
    # extracting and saving the contents
    zf.extractall(comp_path)
    # loading the txt file that was extracted.
    ffdata = pd.read_csv(comp_path + 'DFF_BE_With_Nonindust.txt', header=None)

    # Split the data into columns
    ffdata = ffdata[0].str.split(' ', expand=True)
    # replace all empty cells with NaN values; keep the -99.99s for now
    ffdata.replace('', np.nan, inplace=True)
    ffdata = ffdata.apply(pd.to_numeric, errors='coerce')

    # # create a new dataframe to store rearranged values
    # temp_df = pd.DataFrame()
    # Create a list to collect rows
    rows = []

    # loop through each row and collect only non NaN values.
    for row in ffdata.values:
        # get the non-NaN values
        new_row = row[~np.isnan(row)]

        # # append the rearranged row to the new dataframe
        # temp_df = pd.concat([temp_df, pd.Series(new_row)], ignore_index=True)
        # Append the new row to the list
        rows.append(new_row)

    # cleaned data
    ffdata = pd.DataFrame(rows)

    # Rename the columns
    ffdata.columns = ['permno', 'start', 'end'] + list(range(1, ffdata.shape[1]-2))

    # Set permno as the index
    ffdata = ffdata.set_index('permno')

    # Convert start and end to integers
    ffdata['start'] = ffdata['start'].astype(int)
    ffdata['end'] = ffdata['end'].astype(int)

    # Create a new DataFrame with the years as columns
    newdata = pd.DataFrame(index=ffdata.index, columns=[str(year) for year in range(ffdata['start'].min(),
                                                                                    ffdata['end'].max()+1)])
    # newdata = pd.DataFrame(index=ffdata.index, columns=[str(year*100 + 6) for year in range(ffdata['start'].min(), ffdata['end'].max()+1)])

    # Fill in the new DataFrame with the values corresponding to the correct years
    for perm in ffdata.index:
        start = ffdata.loc[perm, 'start']
        end = ffdata.loc[perm, 'end']
        newdata.loc[perm, str(start):str(end)] = ffdata.loc[perm, list(range(1, end-start+2))].values

    # Convert the values to numeric
    newdata = newdata.apply(pd.to_numeric)

    # Replacing the -99.99 values with NaN
    newdata = newdata.replace(-99.99, np.nan)
    ffdata = newdata.copy()

    # Renaming the columns
    ffdata.columns = [i + '06.0' for i in ffdata.columns]
    ffdata.columns = ffdata.columns.astype(float)

    # Putting ffdata in date x permno form. Then change the column names to be the same datatype (str) as BE columns
    ffdata = ffdata.T
    ffdata.columns = ffdata.columns.astype(str)

    # Identify overlapping firms
    BE.columns = BE.columns.astype(int)  # Make sure both have the same column datatypes
    ffdata.columns = ffdata.columns.astype(float).astype(int)
    common_permno = BE.columns.intersection(ffdata.columns)

    # ffdata has a float index but BE has int index.
    ffdata.index = ffdata.index.astype(int)

    # Get the overlapping dates
    common_dates = BE.index.intersection(ffdata.index)

    # Update BE with data from ffdata for the common firms and additional dates
    for permno in common_permno:
        BE.loc[common_dates, permno] = ffdata.loc[common_dates, permno]

    # Save the extended book equity dataframe, which we rename back to BE
    BE.to_csv(comp_path + 'BE.csv')

    # load market value of equity and set the columns to be integers
    me = pd.read_csv(crsp_path + 'me.csv', index_col=0)
    me.columns = me.columns.values.astype(float).astype(int)

    # Following Fama-French 1993, we divide each value in BE by the value of me six months ago. This avoids a short
    # momentum position from sneaking into value strategies.
    # -- First I need to find the permnos in me that are also in BE since BE has a lot more permnos
    # common_permno = BE.columns.intersection(me.columns)

    # First make sure me and be have the same indices and coluns
    BE.columns = me.columns
    BE.index = me.index

    # Divide 'BE' by Shifted 'me' for Common Firms
    bm = BE.divide(me.shift(6), axis=0)

    # Save the book market dataframe
    bm.to_csv(comp_path + 'BM.csv')

    # The assets of financial firms are very different (and larger than) those of other firms; when we scale by assets we'll
    # often want to kick out financial
    SIC = pd.read_csv(crsp_path + 'siccd.csv', index_col=0)
    FinFirms = (SIC >= 6000) & (SIC <= 6999) # creates a boolean mask that is 1 when the SIC is in the 6000's.
    # uses the .any() method with axis=0 to check which columns have at least one True value (i.e., meet the condition) and
    FinFirms = FinFirms.columns[FinFirms.any(axis=0)].values
    # Changes FinFirms to a dataframe
    FinFirms = pd.DataFrame(FinFirms)
    # Set the column label
    FinFirms.columns = ['permno']
    # Save to path
    FinFirms.to_csv(comp_path + 'FinFirms.csv')

    # Compare our HML factor with that from Ken French's website
    NYSE = pd.read_csv(crsp_path + 'NYSE.csv', index_col=0).astype(int)
    ret = pd.read_csv(crsp_path + 'ret.csv', index_col=0).astype(float)
    bm = pd.read_csv(comp_path + 'BM.csv', index_col=0).astype(float)
    ff = pd.read_csv(crsp_path + 'ff.csv', index_col=0).astype(float)
    dates = pd.read_csv(crsp_path + 'dates.csv', index_col=0).astype(int)

    # Fama and French kick out the negative book-equity firms (the most growthy)
    bm[bm < 0] = np.nan
    ind = makeBivSortInd(me, 2, bm, [30, 70], breaksFilterInd=NYSE)
    res = runBivSort(params, ret, ind, 2, 3, me, dates, printResults=0)

    # Replicate HML from the corner portfolios
    hmlrep = (res[0]['pret'][:, 2] + res[0]['pret'][:, 5] - res[0]['pret'][:, 0] - res[0]['pret'][:, 3])/2

    # Should see a high (~99%) correlation, but it WON'T be perfect for a couple of reasons. Fama-French construct the
    # variable using data available at the time of construction (they don't go back and change it if the fix data errors
    # in crsp/comp). It shouldn't matter: "value" is a robust phenomena -- one of the reasons it is important is that
    # the details don't "matter" for getting a real "exposure" to value.

    # Let the user know of the check.
    print("\nNow let's compare our HML with that form Ken French's website.")

    # Correlation should be >95%
    hml = ff['hml'].to_numpy()
    index = np.isfinite(hmlrep + hml)
    correlation = np.corrcoef(hmlrep[index], hml[index])[0, 1]

    # Print the correlation
    print(f"The correlation between HML from Ken French and replicated HML is {correlation * 100:.2f}%.")

    # Calculate the mean return of HML and replicated HML
    mean_hml = np.nanmean(hml)
    mean_hmlrep = np.nanmean(hmlrep)
    print(f"\nMean return of HML: {mean_hml:.2f}% per month")
    print(f"Mean return of replicated HML: {mean_hmlrep:.2f}% per month")

    # Regress HML on replicated HML
    model1 = sm.OLS(hml, sm.add_constant(hmlrep), missing='drop').fit()
    print('\nRegress HML on replicated HML:')
    print(model1.summary())

    # Regress replicated HML on HML
    model2 = sm.OLS(hmlrep, sm.add_constant(hml), missing='drop').fit()
    print('\nRegress replicated HML on HML:')
    print(model2.summary())

    # Make quarterly book equity. Start with shareholder's equity
    SEQQ = pd.read_csv(comp_path + 'SEQQ.csv', index_col=0)  # Shareholder equity
    CEQQ = pd.read_csv(comp_path + 'CEQQ.csv', index_col=0)  # Common equity
    PSTKQ = pd.read_csv(comp_path + 'PSTKQ.csv', index_col=0)  # Preferred stock
    ATQ = pd.read_csv(comp_path + 'ATQ.csv', index_col=0)  # Assets
    LTQ = pd.read_csv(comp_path + 'LTQ.csv', index_col=0)  # Liabilities
    DT = pd.read_csv(comp_path + 'TXDITCQ.csv', index_col=0)  # Deferred taxes

    SE = SEQQ.copy()  # Initialize SE with SEQQ

    # Update SE where it's NaN with the sum of common equity (CEQQ) and preferred stock (PSTKQ)
    SE.update(CEQQ.add(PSTKQ, fill_value=0), overwrite=False)

    # Further update SE where it's still NaN with the difference between assets (ATQ) and liabilities (LTQ)
    SE.update(ATQ.subtract(LTQ, fill_value=0), overwrite=False)

    # Book equity is shareholder equity + deferred taxes - preferred stock
    BEQ = SE + DT - PSTKQ
    BEQ.to_csv(comp_path + 'BEQ.csv')

    # Make quarterly gross profitability
    REVTQ = pd.read_csv(comp_path + 'REVTQ.csv', index_col=0)
    COGSQ = pd.read_csv(comp_path + 'COGSQ.csv', index_col=0)
    GPQ = REVTQ - COGSQ
    GPQ.to_csv(comp_path + 'GPQ.csv')

    # Make quarterly return-on-assets
    IBQ = pd.read_csv(comp_path + 'IBQ.csv', index_col=0)
    roa = IBQ / ATQ.shift(3, axis=0)
    roa.to_csv(comp_path + 'roa.csv')

    # SUE and dROE
    EPSPXQ = pd.read_csv(comp_path + 'EPSPXQ.csv', index_col=0)

    # The commented out section below works but is very very slow.
    # Find the report dates for IBQ and create a boolean matrix
    # idxRprtDate = (IBQ != IBQ.shift(1)).fillna(False) & IBQ.notna()
    #
    # # Initialize variables for the quarterly lags
    # BEQL1 = pd.DataFrame(np.nan, index=IBQ.index, columns=IBQ.columns)
    # IBQL4 = BEQL1.copy()
    #
    # # Create IBQ and EPSPXQ only for the report dates
    # IBQL0 = IBQ.where(idxRprtDate)
    # EPSPXQL0 = EPSPXQ.where(idxRprtDate)
    #
    # # Initiate the index of the number of lagged report dates available
    # numLagIdx = idxRprtDate.astype(int)
    #
    # # Dictionary to store lagged EPSPXQ data
    # epsStruct = {i: pd.DataFrame(np.nan, index=IBQ.index, columns=IBQ.columns) for i in range(1, 13)}
    #
    # # Loop over the past 60 months
    # for i in range(1, 61):
    #     numLagIdx += idxRprtDate.shift(i).fillna(False).astype(int)
    #     thisNumLagIdx = numLagIdx * idxRprtDate.shift(i).fillna(False).astype(int)
    #
    #     lIBQ = IBQ.shift(i)
    #     lBEQ = BEQ.shift(i)
    #     lEPSPXQ = EPSPXQ.shift(i)
    #
    #     IBQL4[thisNumLagIdx == 5] = lIBQ[thisNumLagIdx == 5]
    #     BEQL1[thisNumLagIdx == 2] = lBEQ[thisNumLagIdx == 2]
    #
    #     for j in range(1, 13):
    #         epsStruct[j][thisNumLagIdx == j + 1] = lEPSPXQ[thisNumLagIdx == j + 1]

    # Timekeeping

    # Create lagged data for different quarters

    # Function to fill in months between announcements

    # Fill in the months in between announcements
    # Initialize SUE dataframe with NaN
    SUE = pd.DataFrame(index=IBQ.index, columns=IBQ.columns).astype(float)

    # Difference between quarterly EPS and the EPS of the same quarter last year
    EPS_diff = EPSPXQ - EPSPXQ.shift(12, axis=0)

    # Rolling 2 year standard deviations; requiring at least 6 observations
    EPS_std = EPS_diff.rolling(window=24, min_periods=6).std()

    # Dividing the eps difference by the 2 year standard deviations
    SUE = EPS_diff / EPS_std

    # Forward fill missing data and save it
    SUE = SUE.ffill()
    SUE.to_csv(comp_path + 'SUE.csv')

    # Create and store dROE, which equals the annual change in net income divided by the previous quarters shareholder's
    # equity
    dROE = (IBQ - IBQ.shift(12)) / BEQ.shift(4)
    dROE = dROE.ffill()
    dROE.to_csv(comp_path + 'dROE.csv')

    # Make SUE2 -- a simpler construction
    # current earnings minus earnings from one year ago, scaled by the stand. dev. of last 8 quarterly earnings.
    SUE2 = (IBQ - IBQ.shift(12)) / IBQ.rolling(window=24, min_periods=2).std()
    SUE2 = SUE2.ffill()
    SUE2.to_csv(comp_path + 'SUE2.csv')

    # Make dROA -- difference between current earnings and average of the last four quarters, scaled by lagged assets
    # :TODO Ask Mish if ATQ should be lagged or not. The description says to but it doesn't appear in Matlab code.
    # :TODO Also ask Mish if we should forward fill dROA like we did for dROE.
    dROA = (IBQ - IBQ.rolling(window=12, min_periods=2).mean()) / ATQ
    dROA = dROA.ffill()
    dROA.to_csv(comp_path + 'dROA.csv')

    # announcement month effect (Frazzini-Lamont)
    amonth = IBQ != IBQ.shift(1)

    # Filter to ensure that changes are only flagged where IBQ has valid data
    amonth = amonth & IBQ.notna()
    amonth.to_csv(comp_path + 'amonth.csv')

    # from AssayingAnomalies.Functions.runUnivSort import runUnivSort
    # indAMO = IBQ + amonth.shift(2)
    # dates = pd.read_csv(crsp_path + 'dates.csv', index_col=0)
    # ret = pd.read_csv(crsp_path + "ret.csv", index_col=0)
    # me = pd.read_csv(crsp_path + 'me.csv', index_col=0)
    # res = runUnivSort(params, ret, indAMO, me, dates)

    print(f"\nCOMPUSTAT derived variables run ended at {datetime.now()}.\n")

    return


if __name__ == "__main__":
    params = AssayingAnomalies.Config.load_params(
        r"C:\Users\josht\PycharmProjects\AssayingAnomalies-1.6.3\AssayingAnomalies\config.json"
    )
    makeCOMPUSTATDerivedVariables(params)
