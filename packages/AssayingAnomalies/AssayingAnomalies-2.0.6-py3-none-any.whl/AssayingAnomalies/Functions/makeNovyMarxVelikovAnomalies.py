import pandas as pd
import numpy as np
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from AssayingAnomalies.Functions.rank_with_nan import rank_with_nan
from AssayingAnomalies.Functions.fill_months import fill_months
from AssayingAnomalies.Functions.makePastPerformance import makePastPerformance
from AssayingAnomalies.Functions.assignToPtf import assignToPtf
from AssayingAnomalies.Functions.makeUnivSortInd import makeUnivSortInd


def makeNovyMarxVelikovAnomalies(params):
    # Timekeeping
    print(
        f"\nNow working on making anomaly signals from Novy-Marx and Velikov (RFS, 2016). Run started at {datetime.now()}\n")

    # Labels
    labels = ['size', 'value', 'grossProfitability', 'valProf', 'accruals', 'assetGrowth', 'investment', 'piotroski',
              'issuance', 'roe', 'distress', 'valMomProf', 'valMom', 'iVol', 'momentum', 'peadSUE', 'peadCAR3',
              'industryMomentum', 'industryRelativeReversal', 'highFrequencyCombo', 'reversals', 'seasonality',
              'industryRelativeReversalLowVol']


    # Store the general and daily CRSP data path
    crsp_path = params.crspFolder + os.sep
    daily_path = params.daily_crsp_folder + os.sep
    comp_path = params.compFolder + os.sep

    # Load a few basic variables
    ret = pd.read_csv(crsp_path + 'ret.csv', index_col=0).astype(float)
    me = pd.read_csv(crsp_path + 'me.csv', index_col=0).astype(float)
    dates = pd.read_csv(crsp_path + 'dates.csv', index_col=0).astype(int).values.flatten()

    # Store a few constants
    nMonths = len(ret.index)
    nStocks = len(ret.columns)

    # Initialize anomalies array
    anoms = np.full((nMonths, nStocks, 23), np.nan)

    # Size anomaly
    juneIndicator = (dates % 100 == 6)
    size = -me * juneIndicator[:, np.newaxis]  # turn juneIndicator into a col vector to multiply each col of me with.
    size[size == 0] = np.nan
    anoms[:, :, 0] = size

    # Value Anomaly
    value = pd.read_csv(comp_path + 'BM.csv', index_col=0).astype(float)
    anoms[:, :, 1] = value

    # Profitability Anomaly
    GP = pd.read_csv(comp_path + 'GP.csv', index_col=0).astype(float)
    AT = pd.read_csv(comp_path + 'AT.csv', index_col=0).astype(float)
    SIC = pd.read_csv(crsp_path + 'siccd.csv', index_col=0)
    FinFirms = (SIC >= 6000) & (SIC <= 6999) # creates a boolean mask that is 1 when the SIC is in the 6000's.
    gp = GP / AT
    gp[FinFirms == 1] = np.nan
    anoms[:, :, 2] = gp

    # ValProf Anomaly
    value[value == 0] = np.nan
    # gp_rank = np.apply_along_axis(rankdata, 1, gp)
    gp_rank = rank_with_nan(gp)
    # bm_rank = np.apply_along_axis(rankdata, 1, value)
    bm_rank = rank_with_nan(value)
    valProf = gp_rank + bm_rank
    anoms[:, :, 3] = valProf

    # Accruals
    ACT = pd.read_csv(comp_path + 'ACT.csv', index_col=0).astype(float)
    CHE = pd.read_csv(comp_path + 'CHE.csv', index_col=0).astype(float)
    LCT = pd.read_csv(comp_path + 'LCT.csv', index_col=0).astype(float)
    DLC = pd.read_csv(comp_path + 'DLC.csv', index_col=0).astype(float)
    TXP = pd.read_csv(comp_path + 'TXP.csv', index_col=0).astype(float)
    DP = pd.read_csv(comp_path + 'DP.csv', index_col=0).astype(float)

    dCA = ACT - ACT.shift(12)
    dCash = CHE - CHE.shift(12)
    dCL = LCT - LCT.shift(12)
    dSTD = DLC - DLC.shift(12)
    dTP = TXP - TXP.shift(12)
    Accruals = (dCA - dCash) - (dCL - dSTD - dTP) - DP
    accruals = -2 * Accruals / (AT + AT.shift(12))
    anoms[:, :, 4] = accruals

    # Asset Growth
    assetGrowth = -AT / AT.shift(12)
    assetGrowth[FinFirms == 1] = np.nan
    anoms[:, :, 5] = assetGrowth

    # Investment
    PPEGT = pd.read_csv(comp_path + 'PPEGT.csv', index_col=0).astype(float)
    INVT = pd.read_csv(comp_path + 'INVT.csv', index_col=0).astype(float)
    investment = -(PPEGT - PPEGT.shift(12) + INVT - INVT.shift(12)) / AT.shift(12)
    investment[FinFirms == 1] = np.nan
    anoms[:, :, 6] = investment

    # Piotroski's F-score (JAR 2000)
    IB = pd.read_csv(comp_path + 'IB.csv', index_col=0).astype(float)
    DLTT = pd.read_csv(comp_path + 'DLTT.csv', index_col=0).astype(float)
    SCSTKC = pd.read_csv(comp_path + 'SCSTKC.csv', index_col=0).astype(float)
    PRSTKCC = pd.read_csv(comp_path + 'PRSTKCC.csv', index_col=0).astype(float)
    # shrout = pd.read_csv(crsp_path + 'shrout.csv', index_col=0).astype(float)
    COGS = pd.read_csv(comp_path + 'COGS.csv', index_col=0).astype(float)
    REVT = pd.read_csv(comp_path + 'REVT.csv', index_col=0).astype(float)
    CFO = pd.read_csv(comp_path + 'CFO.csv', index_col=0).astype(float)

    ROA = IB / AT.shift(12)
    DTA = DLTT / AT
    ATL = ACT / LCT
    EqIss = SCSTKC.fillna(0) - PRSTKCC.fillna(0)
    # dshrout = shrout / shrout.shift(12) - 1
    GM = 1 - COGS / REVT
    ATO = REVT / AT.shift(12)

    # Financial Performance Signals
    F_ROA = (IB > 0).astype(int)
    F_CFO = (CFO > 0).astype(int)
    F_DROA = (ROA - ROA.shift(12) > 0).astype(int)
    F_ACCR = (CFO - IB > 0).astype(int)
    F_DLEV = ((DTA - DTA.shift(12) < 0) | ((DLTT == 0) & (DLTT.shift(12) == 0))).astype(int)
    F_ATL = (ATL - ATL.shift(12) > 0).astype(int)
    F_EQ = (EqIss <= 0).astype(int)
    F_GM = (GM - GM.shift(12) > 0).astype(int)
    F_ATO = (ATO - ATO.shift(12) > 0).astype(int)

    piotroski = F_ROA + F_CFO + F_DROA + F_ACCR + F_DLEV + F_ATL + F_EQ + F_GM + F_ATO

    # Available signals
    available = (F_ROA.notna() & F_CFO.notna() & F_DROA.notna() & F_ACCR.notna() &
                 F_DLEV.notna() & F_ATL.notna() & F_EQ.notna() & F_GM.notna() & F_ATO.notna()).sum(axis=1)
    piotroski[available < 9] = np.nan

    # Adjusting with Book-to-Market ratio
    bm_ranks = value.rank(axis=1)
    piotroski += bm_ranks / 1000

    # Store it
    anoms[:, :, 7] = piotroski

    # Issuance anomaly
    dashrout = pd.read_csv(crsp_path + 'dashrout.csv', index_col=0).astype(float)
    screen = np.ones(ret.shape)
    issuance = -dashrout * screen
    anoms[:, :, 8] = issuance

    # Return on Book Equity (ROE) anomaly
    IBQ = pd.read_csv(comp_path + 'IBQ.csv', index_col=0).astype(float)
    BEQ = pd.read_csv(comp_path + 'BEQ.csv', index_col=0).astype(float)
    roe = IBQ / BEQ.shift(3)
    anoms[:, :, 9] = roe

    # Distress risk
    IVOL = pd.read_parquet(crsp_path + 'IVOL.parquet').astype(float)
    prc = pd.read_csv(crsp_path + 'prc.csv', index_col=0).astype(float)
    ff = pd.read_csv(crsp_path + 'ff.csv', index_col=0).astype(float)
    # ACTQ = pd.read_csv(comp_path + 'ACTQ.csv', index_col=0).astype(float)
    # ATQ = pd.read_csv(comp_path + 'ATQ.csv', index_col=0).astype(float)
    CHEQ = pd.read_csv(comp_path + 'CHEQ.csv', index_col=0).astype(float)
    # DLCQ = pd.read_csv(comp_path + 'DLCQ.csv', index_col=0).astype(float)
    # DLTTQ = pd.read_csv(comp_path + 'DLTTQ.csv', index_col=0).astype(float)
    # IBQ = pd.read_csv(comp_path + 'IBQ.csv', index_col=0).astype(float)
    # LCTQ = pd.read_csv(comp_path + 'LCTQ.csv', index_col=0).astype(float)
    LTQ = pd.read_csv(comp_path + 'LTQ.csv', index_col=0).astype(float)
    NIQ = pd.read_csv(comp_path + 'NIQ.csv', index_col=0).astype(float)
    # PIQ = pd.read_csv(comp_path + 'PIQ.csv', index_col=0).astype(float)

    mktmat = (ff['mkt'] + ff['rf']).values.reshape(-1, 1) @ np.ones((1, me.shape[1]))
    temp = np.nansum(me, axis=1)
    memat = np.tile(temp, (me.shape[1], 1)).T  # repeats the temp series len(me.columns) times.
    coef = np.array([-20.264, 1.416, -7.129, 1.411, -0.045, -2.132, 0.075, -0.058])
    c = 2 ** (-1 / 3)
    NIfac = (1 - c ** 3) / (1 - c ** 12)

    # Calculating NIMTAAVG
    me.columns = me.columns.astype(float).astype(int).astype(str)  # :TODO fix how crsp columns labels are stored
    niq = NIQ / (LTQ + me)
    NIMTAAVG = np.full_like(me, np.nan, dtype=float)
    for i in range(9, len(me)):
        v1 = niq.iloc[i, :] + (c ** 3) * niq.iloc[i - 3, :] + (c ** 6) * niq.iloc[i - 6, :] + (
                c ** 9) * niq.iloc[i - 9, :]
        v2 = NIfac * v1
        NIMTAAVG[i, :] = NIfac * (niq.iloc[i, :] + (c ** 3) * niq.iloc[i - 3, :] + (c ** 6) * niq.iloc[i - 6, :] + (
                c ** 9) * niq.iloc[i - 9, :])

    # Calculating TLMTA
    TLMTA = (LTQ / (LTQ + me)).to_numpy()

    # Calculating EXRET
    EXRET = (np.log(1 + ret) - np.log(1 + mktmat)).to_numpy()
    XRfac = (1 - c) / (1 - c ** 12)
    EXRETAVG = np.full_like(me, np.nan, dtype=float)
    for i in range(12, len(me)):
        temp = EXRET[i - 1, :]
        for j in range(2, 13):
            temp += (c ** j) * EXRET[i - j, :]
        EXRETAVG[i, :] = XRfac * temp

    # Calculating SIGMA, RSIZE, and CASHMTA
    SIGMA = (np.sqrt(252) * IVOL).to_numpy()
    RSIZE = np.log(me / memat).to_numpy()
    CASHMTA = (CHEQ / (LTQ + me)).to_numpy()

    # Sum of negative book equity values
    BE = pd.read_csv(comp_path + 'BE.csv', index_col=0).astype(float)
    # negative_be_sum = (BE < 0).sum().sum()

    # Adjust BE and handle negative or zero values
    adjBE = 0.9 * BE + 0.1 * me
    adjBE[adjBE <= 0] = 0.001

    # Calculate MB and carry forward values
    MB = me.shift(6) / adjBE
    finite_mb_indices = MB.apply(lambda x: x.count(), axis=1) > 0

    for i in finite_mb_indices[finite_mb_indices].index:
        for j in range(1, 12):
            if i + j in MB.index:
                MB.loc[i + j] = MB.loc[i]

    MB = MB.to_numpy()
    # Calculate PRICE
    PRICE = prc.abs().clip(upper=15)
    PRICE[PRICE < 1] = np.nan
    PRICE[prc.isna()] = np.nan

    # Create helper function to winsorize the data
    def winsorize(series, percentile):
        lower = np.nanpercentile(series, percentile)
        upper = np.nanpercentile(series, 100 - percentile)
        return np.clip(series, lower, upper)

    # Applying winsorization and calculating 'distress'
    DISTRESS = sum(coef[i] * winsorize(variable, 5) for i, variable in
                   enumerate([NIMTAAVG, TLMTA, EXRETAVG, SIGMA, RSIZE, CASHMTA, MB, PRICE]))
    distress = -DISTRESS

    # Store the anomaly
    anoms[:, :, 10] = distress

    # Make ValMom & valMomPRof anoms
    R = pd.read_csv(crsp_path + 'R.csv', index_col=0).astype(float)
    # r_rank = np.apply_along_axis(rankdata, 1, R)
    r_rank = rank_with_nan(R)
    valMom = r_rank + fill_months(bm_rank, annual_or_quarterly='annual')  # :TODO Why are we filling months here?
    valMomProf = r_rank + fill_months(bm_rank, annual_or_quarterly='annual') + \
                 fill_months(gp_rank, annual_or_quarterly='annual')

    # Store the anomalies
    anoms[:, :, 11] = valMom
    anoms[:, :, 12] = valMomProf

    # Idiosyncratic volatility
    anoms[:, :, 13] = -pd.read_parquet(crsp_path + 'IffVOL3.parquet')

    # Momentum
    momentum = makePastPerformance(ret, 12, 1)
    anoms[:, :, 14] = momentum

    # PEAD (SUE)
    anoms[:, :, 15] = pd.read_csv(comp_path + 'SUE2.csv', index_col=0).astype(float)

    # PEAD (CAR3)
    anoms[:, :, 16] = pd.read_parquet(crsp_path + 'CAR3.parquet').astype(float)

    # Industry Momentum
    # FF49 = pd.read_csv(crsp_path + 'FF49.csv', index_col=0).astype(float)
    iFF49ret = pd.read_csv(crsp_path + 'iFF49ret.csv', index_col=0).astype(float)
    iFF49reta = pd.read_csv(crsp_path + 'iFF49reta.csv', index_col=0).astype(float)
    industryMomentum = assignToPtf(iFF49reta, np.sort(iFF49ret))
    # this expression creates a matrix where each row is a copy of the maximum value from the corresponding row in
    # industryMomentum, and the number of columns in this new matrix is the same as the number of columns in ret.
    max_values = np.tile(industryMomentum.max(axis=1), (ret.shape[1], 1)).T
    industryMomentum[industryMomentum == 0] = np.nan
    industryMomentum = industryMomentum / max_values
    anoms[:, :, 17] = pd.DataFrame(industryMomentum)

    # Industry-Relative Reversals
    IRR = rank_with_nan(iFF49reta.T - ret.T).T
    max_values = np.tile(np.nanmax(IRR, axis=1), (ret.shape[1], 1)).T
    industryRelativeReversal = IRR / max_values
    anoms[:, :, 18] = pd.DataFrame(industryRelativeReversal)

    # High Frequency Combo
    anoms[:, :, 19] = pd.DataFrame(industryMomentum + industryRelativeReversal)

    # Reversals
    anoms[:, :, 20] = -ret

    # Seasonality (Heston-Sadka)
    seasonality = pd.DataFrame(0, index=ret.index, columns=ret.columns)
    for i in range(1, 6):
        seasonality += ret.shift(periods=12 * i - 1)

    # Replace zeros with NaN and store
    seasonality.replace(0, np.nan, inplace=True)
    anoms[:, :, 21] = pd.DataFrame(seasonality)

    # IRRLowVol
    NYSE = pd.read_csv(crsp_path + 'NYSE.csv', index_col=0).astype(float)
    IffVol3 = pd.read_parquet(crsp_path + 'IffVOL3.parquet').astype(float)
    ind = makeUnivSortInd(IffVol3, 2, NYSE)
    industryRelativeReversalLowVol = IRR.copy()
    industryRelativeReversalLowVol[ind == 2] = np.nan
    anoms[:, :, 22] = pd.DataFrame(industryRelativeReversalLowVol)

    if not params.num_cpus:
        for i, label in enumerate(labels):
            pd.DataFrame(anoms[:, :, i]).to_csv(crsp_path + f'nvmv_{label}.csv')

    else:
        def save_anoms(args):
            df, label = args
            print(f"Saving {label}")
            df.to_csv(crsp_path + f'nvmv_{label}.csv')
            print(f"Save completed for {label}.")

        tasks = [(pd.DataFrame(anoms[:, :, i]), labels[i]) for i in range(anoms.shape[2])]

        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            executor.map(save_anoms, tasks)

    # :TODO:NOTE Here I have departed from the Matlab implemenation. Instead of saving a large panel dataframe, I am
    # # saving each dataframe independently. To turn the 3D array into a panel structure and save it, you can uncomment
    # # the section below and run it but it takes a significant amount of RAM.
    # Reshape and stack data into a table
    # nAnoms = len(labels)
    # # nObs = nStocks * nMonths
    # outputData = []
    #
    # permno_repeated = np.tile(ret.columns.astype(float), nMonths)
    # dates_repeated = np.tile(ret.index.astype(int), nStocks)
    #
    # outputData.append(permno_repeated)
    # outputData.append(dates_repeated)
    #
    # # Append all the anomaly columns
    # for i in range(nAnoms):
    #     outputData.append(anoms[:, :, i].flatten())
    #
    # # Create DataFrame
    # col_names = ['permno', 'date'] + labels
    # outputData = pd.DataFrame(outputData, index=col_names).T
    #
    # # Drop rows that are entirely nan values
    # outputData.dropna(how='all', inplace=True, subset=labels)
    #
    # # Save
    # outputData.columns = outputData.columns.astype(str)
    # outputData.to_parquet(crsp_path + 'novyMarxVelikovAnomalies.parquet')

    # Timekeeping
    print(f"\nAnomaly signal run ended, data exported at {datetime.now()}\n")

    return


if __name__ == "__main__":
    import AssayingAnomalies
    params = AssayingAnomalies.Config.load_params(
        r"C:\Users\josht\PycharmProjects\AssayingAnomalies-1.6.3\AssayingAnomalies\config.json"
    )
    makeNovyMarxVelikovAnomalies(params)

    # # Example Data
    # nMonths = 2  # For example, two months
    # nStocks = 3  # For example, three stocks
    # nAnoms = 3  # Three anomalies
    #
    # # Simulate stock identifiers and dates
    # permno = np.array([101, 102, 103])  # Stock identifiers
    # dates = pd.date_range(start='2020-01-01', periods=nMonths, freq='M')  # Dates for two months
    #
    # # Simulate anomaly data
    # anoms = np.random.rand(nMonths, nStocks, nAnoms)  # Random data for anomalies
    #
    # # Reshape and stack data into a table
    # nObs = nStocks * nMonths
    # outputData = []
    #
    # # Add permno and dates columns
    # permno_repeated = np.tile(permno, nMonths)
    # dates_repeated = np.repeat(dates, nStocks)
    # outputData.append(permno_repeated)
    # outputData.append(dates_repeated)
    #
    # # Append all the anomaly columns
    # for i in range(nAnoms):
    #     outputData.append(anoms[:, :, i].flatten())
    #
    # # Create DataFrame
    # outputData = pd.DataFrame(outputData).T
    # outputData.columns = ['permno', 'dates', 'anom1', 'anom2', 'anom3']
    #
    # # Remove rows with NaNs in all anomaly columns
    # outputData = outputData.dropna(subset=['anom1', 'anom2', 'anom3'], how='all')

