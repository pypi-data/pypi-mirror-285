import pandas as pd
import os
from .makeFF10Indus import makeFF10Indus
from .makeFF17Indus import makeFF17Indus
from .makeFF49Indus import makeFF49Indus

# saveFolder = r'/home/jlaws13/PycharmProjects/AssayingAnomalies_root/Data/CRSP/'
def makeIndustryClassifications(params):
    """
    Purpose: This function creates and stores various industry classifications. Those include 4-digit SIC code, FF10,
    FF17, and FF49.
    :return:
    """
    saveFolder = params.crspFolder + os.sep

    siccd = pd.read_csv(saveFolder + 'siccd.csv', index_col=0)
    siccd.to_csv(saveFolder + 'SIC.csv')
    # Make the industry classifications
    FF10, FF10Names = makeFF10Indus(siccd)
    FF17, FF17Names = makeFF17Indus(siccd)
    FF49, FF49Names = makeFF49Indus(siccd)
    # TODO:F I have not made FF49 yet. It is very tedious.

    # Store the industry classification matrices
    FF10.to_csv(saveFolder + 'FF10.csv')
    FF10Names.to_csv(saveFolder + 'FF10Names.csv')
    FF17.to_csv(saveFolder + 'FF17.csv')
    FF17Names.to_csv(saveFolder + 'FF17Names.csv')
    FF49.to_csv(saveFolder + 'FF49.csv')
    FF49Names.to_csv(saveFolder + 'FF49Names.csv')

    return

