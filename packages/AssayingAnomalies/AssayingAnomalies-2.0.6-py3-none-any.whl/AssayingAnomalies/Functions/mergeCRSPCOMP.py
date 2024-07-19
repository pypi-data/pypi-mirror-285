import numpy as np
import pandas as pd
import os
from .makeCOMPUSTATVariables import makeCOMPUSTATVariables
from datetime import datetime


def mergeCRSPCOMP(params):
    # Timekeeping
    print(f"\nNow working on merging CRSP and COMPUSTAT variables. Run started at {datetime.now()}.\n")

    crspFolder = params.crspFolder + os.sep
    compFolder = params.compFolder + os.sep

    # set year of beginning and end of sample
    SAMPLE_START = params.sample_start
    SAMPLE_END = params.sample_end

    # Read the linking file
    crsp_ccmxpf_lnkhist = pd.read_csv(crspFolder + 'crsp_ccmxpf_lnkhist.csv', index_col=0)

    # Filter based on the CCM link; Leave only link types LC or LU :TODO What does 'LC' and 'LU' represent?
    idxToKeep = crsp_ccmxpf_lnkhist['linktype'].isin(['LC', 'LU'])
    crsp_ccmxpf_lnkhist = crsp_ccmxpf_lnkhist[idxToKeep]

    # Remove unwanted variables (columns)
    crsp_ccmxpf_lnkhist = crsp_ccmxpf_lnkhist[['lpermno', 'gvkey', 'linkdt', 'linkenddt']]

    # Replace the missing linkeddt with the chosen end of sample
    indNatEndDate = pd.isna(crsp_ccmxpf_lnkhist['linkenddt'])
    crsp_ccmxpf_lnkhist.loc[indNatEndDate, 'linkenddt'] = datetime(SAMPLE_END, 12, 31)

    # Load the annual COMPUSTAT file
    # comp_funda = pd.read_csv(compFolder + 'comp_funda.csv',  index_col=0, nrows=1000)
    comp_funda = pd.read_csv(compFolder + 'comp_funda.csv', index_col=0)
    comp_funda['datadate'] = pd.to_datetime(comp_funda['datadate'], format='%Y-%m-%d')  # Convert to datetime format

    # First create a boolean series indicating which rows don't satisfy our criteria
    idxToDrop = (comp_funda['datadate'] > datetime(SAMPLE_END, 12, 31)) | \
                (comp_funda['datadate'] < datetime(SAMPLE_START, 1, 1))
    # Then drop the rows
    comp_funda.drop(index=comp_funda[idxToDrop].index, inplace=True)

    # Merge the dataframes, making sure to specify we want to keep all values from comp_funda and crsp_ccmxpf_lnkhist. Setting sort=False increases performance
    comp_funda_linked = pd.merge(comp_funda, crsp_ccmxpf_lnkhist, how='outer', on='gvkey', sort=False)

    # Fiscal period end date must be within link date range. Need to convert the string to a datetime object before doing the comparison.
    comp_funda_linked['linkenddt'] = pd.to_datetime(comp_funda_linked['linkenddt'], format='%Y-%m-%d')
    comp_funda_linked['linkdt'] = pd.to_datetime(comp_funda_linked['linkdt'], format='%Y-%m-%d')
    idxToDrop = (comp_funda_linked['datadate'] > comp_funda_linked['linkenddt']) | \
                (comp_funda_linked['datadate'] < comp_funda_linked['linkdt'])
    comp_funda_linked = comp_funda_linked.loc[~idxToDrop]

    # Must have permno
    indxToDrop = comp_funda_linked.lpermno.isna()
    comp_funda_linked = comp_funda_linked.loc[~indxToDrop]

    # Create a new 'dates' column in YYYYMM format. The '.dt' lets us access the 'year' attribute of the 'datadate' column
    comp_funda_linked['dates'] = (comp_funda_linked['datadate'].dt.year + 1) * 100 + 6

    # Drop a few variables and change the name of permno column
    comp_funda_linked.drop(columns=['gvkey', 'linkdt', 'linkenddt'], inplace=True)
    comp_funda_linked.rename(columns={'lpermno': 'permno'}, inplace=True)

    # Note: there are cases where a company changes its fiscal year end, which
    # results in more than one observation per permno-year. See, e.g., year
    # 1969 for permno 10006. We'll deal with those here by keeping only the
    # data from the fiscal year that happens later in the year
    # Sort the table first
    comp_funda_linked.sort_values(by=['permno', 'datadate'], inplace=True)
    nduplicates = (comp_funda_linked.groupby(['permno', 'dates']).size() > 1).sum()
    print(f"There were {nduplicates} cases of permno-years in which companies moved their fiscal year end.")

    # Apply the anonymous function (i.e., leaving the last element) in the first argument to every variable, by grouping them by permno & date
    # Using 'groupby' method to group 'comp_funda_linked' by permno and dates. Then using nested apply methods. The inner one
    # selects the last element of each variable for each row. The outer one selects the last element of each variable for
    # each group.
    # adj_comp_funda_linked = comp_funda_linked.groupby(['permno', 'dates']).apply(lambda x: x.apply(lambda y: y.iloc[-1]))
    # The above line is VERY slow. Below is a faster method
    adj_comp_funda_linked = comp_funda_linked.groupby(['permno', 'dates']).tail(1).copy()

    # The below code doesn't need to be run. The columns titled 'Fun_....' is a Matlab artifact.
    # Fix the names
    # varNames = adj_comp_funda_linked.Properties.VariableNames';
    # clndVarNames = regexprep(varNames,'Fun_','');
    # adj_comp_funda_linked.Properties.VariableNames = clndVarNames;

    # Create the fiscal year end variable in YYYYMMDD format and drop a couple of variables
    adj_comp_funda_linked['FYE'] = (adj_comp_funda_linked['datadate'].dt.year * 10000 +
                                    adj_comp_funda_linked['datadate'].dt.month * 100 +
                                    adj_comp_funda_linked['datadate'].dt.day)
    adj_comp_funda_linked = adj_comp_funda_linked.drop(columns='datadate', axis=1)

    adj_comp_funda_linked.to_csv(compFolder + 'adj_comp_funda_linked.csv')

    # TODO:F This line is redundant but if I remove it then makeCOMPUSTATVariables acts funny.
    # Note! when reading in the file, the column labeled 'unnamed' looks like permno but it is incorrect. The correct
    # permnos are in the permno column
    adj_comp_funda_linked = pd.read_csv(compFolder + 'adj_comp_funda_linked.csv')

    """At this point, the function should call another function named makeCOMPUSTATVariables."""
    makeCOMPUSTATVariables(params=params, data=adj_comp_funda_linked, quarterly_indicator=False)

    "After running makeCOMPUSTATVariables, we need to perform a similar set of operations to the quarterly file"
    # Load the quarterly COMPUSTAT file
    # comp_funda = pd.read_csv(compFolder + 'comp_funda.csv',  index_col=0, nrows=1000)
    comp_fundq = pd.read_csv(compFolder + 'comp_fundq.csv', index_col=0)
    comp_fundq['datadate'] = pd.to_datetime(comp_fundq['datadate'], format='%Y-%m-%d')  # Convert to datetime format

    # First create a boolean series indicating which rows don't satisfy our criteria
    idxToDrop = (comp_fundq.rdq.isna()) | \
                (comp_fundq['datadate'] > datetime(SAMPLE_END, 12, 31)) | \
                (comp_fundq['datadate'] < datetime(SAMPLE_START, 1, 1))
    # Then drop the rows
    comp_fundq.drop(index=comp_fundq[idxToDrop].index, inplace=True)

    # Merge the dataframes, making sure to specify we want to keep all values from comp_funda and crsp_ccmxpf_lnkhist. Setting sort=False increases performance
    comp_fundq_linked = pd.merge(comp_fundq, crsp_ccmxpf_lnkhist, how='outer', on='gvkey', sort=False)

    # Fiscal period end date must be within link date range. Need to convert the string to a datetime object before doing the comparison.
    comp_fundq_linked['linkenddt'] = pd.to_datetime(comp_fundq_linked['linkenddt'], format='%Y-%m-%d')
    comp_fundq_linked['linkdt'] = pd.to_datetime(comp_fundq_linked['linkdt'], format='%Y-%m-%d')
    idxToDrop = (comp_fundq_linked['datadate'] > comp_fundq_linked['linkenddt']) | \
                (comp_fundq_linked['datadate'] < comp_fundq_linked['linkdt'])
    comp_fundq_linked = comp_fundq_linked.loc[~idxToDrop]

    # Must have permno
    indxToDrop = comp_fundq_linked.lpermno.isna()
    comp_fundq_linked = comp_fundq_linked.loc[~indxToDrop]

    # Drop a few variables
    comp_fundq_linked.drop(columns=['gvkey', 'linkdt', 'linkenddt'], inplace=True)

    # Create the dates variable in yyyymm format - assume available at the end of the RDQ month
    # first converts the 'rdq' column to datetime using pd.to_datetime(), and then applies the .dt.strftime() method
    # to format the date as a string in the 'yyyymm' format.
    # The '.dt' lets us access the 'year' attribute of the 'datadate' column
    comp_fundq_linked['dates'] = pd.to_datetime(comp_fundq_linked['rdq']).dt.strftime('%Y%m')

    # Change the name of permno column
    comp_fundq_linked.rename(columns={'lpermno': 'permno'}, inplace=True)

    # Note: there are cases where multiple stock-quarter data points are
    # associated with a single earnings announcement date (RDQ). These could be
    # due to restatements, or delays in announcements. See, e.g., permno 63079
    # announcements for 200708 in comp_fundq_linked:
    # temp=comp_fundq_linked(comp_fundq_linked.permno==63079 & comp_fundq_linked.dates==200708,:);
    # We'll deal with these by leaving the latest available fiscal quarter associated with each RDQ
    comp_fundq_linked.sort_values(by=['permno', 'datadate', 'rdq'], inplace=True)

    # Count duplicates before selecting the last row
    nduplicates = (comp_fundq_linked.groupby(['permno', 'dates']).size() > 1).sum()

    # Apply the anonymous function (i.e., leaving the last element) in the first argument to every variable,
    # by grouping them by permno & date Using 'groupby' method to group 'comp_fundq_linked' by permno and dates. Then
    # using nested apply methods. The inner one selects the last element of each variable for each row. The outer one
    # selects the last element of each variable for each group.
    # adj_comp_fundq_linked = comp_fundq_linked.groupby(['permno', 'dates']).apply(lambda x: x.apply(lambda y: y.iloc[-1]))

    # The above line is VERY slow. Below is a  faster method
    adj_comp_fundq_linked = comp_fundq_linked.groupby(['permno', 'dates']).tail(1).copy()

    print(f"There were {nduplicates} cases of permno-RDQ months associated with multiple quarters.")

    # Create the RDQ and fiscal-quarter-end variables
    adj_comp_fundq_linked['rdq'] = pd.to_datetime(comp_fundq_linked['rdq'])
    adj_comp_fundq_linked['RDQ'] = adj_comp_fundq_linked['rdq'].dt.year * 10000 + \
                                   adj_comp_fundq_linked['rdq'].dt.month * 100 + \
                                   adj_comp_fundq_linked['rdq'].dt.day

    adj_comp_fundq_linked['FQTR'] = adj_comp_fundq_linked['datadate'].dt.year * 10000 + \
                                    adj_comp_fundq_linked['datadate'].dt.quarter * 100 + 99

    adj_comp_fundq_linked = adj_comp_fundq_linked.drop(['rdq', 'datadate'], axis=1)
    adj_comp_fundq_linked.to_csv(crspFolder + 'adj_comp_fundq_linked.csv')

    # TODO:F This line is redundant but if I remove it then makeCOMPUSTATVariables acts funny.
    # Note! when reading in the file, the column labeled 'unnamed' looks like permno but it is incorrect. The correct
    # permnos are in the permno column
    adj_comp_fundq_linked = pd.read_csv(crspFolder + 'adj_comp_fundq_linked.csv')

    """Next I need to call makeCOMPUSTATVariables again to make the quarterly variables"""
    makeCOMPUSTATVariables(params, data=adj_comp_fundq_linked, quarterly_indicator=True)

    # Timekeeping
    print(f"\nFinished merging CRSP and COMPUSTAT variables. Run ended at {datetime.now()}.\n")

    return
