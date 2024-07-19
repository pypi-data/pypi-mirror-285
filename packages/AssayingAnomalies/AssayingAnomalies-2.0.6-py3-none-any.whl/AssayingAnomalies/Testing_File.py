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
from scipy.io import loadmat

"""
Testing wrt Matlab output
"""

# First load in your parameters
params = Config()
params = params.load_params()
# params = json.load(open('config.json'))

# Load all variables we will need from AA
# ret = pd.read_csv(params.crspFolder + os.sep + 'ret.csv', index_col=0).astype(float)
# me = pd.read_csv(params.crspFolder + os.sep + 'me.csv', index_col=0).astype(float)
# dates = pd.read_csv(params.crspFolder + os.sep + 'dates.csv', index_col=0).astype(float)
# NYSE = pd.read_csv(params['crspFolder'] + os.sep + 'NYSE.csv', index_col=0).astype(float)  # Load the NYSE indicator mat.
# exchcd = pd.read_csv(os.path.join(params.crspFolder, 'exchcd.csv'), index_col=0)  # Load the exchcode matrix
# tcosts = pd.read_parquet(os.path.join(params.crspFolder, 'tcosts.parquet'))
# bm = pd.read_csv(os.path.join(params.compFolder, 'bm.csv'), index_col=0)


# Path to .mat files
mat_path = r"C:\Users\josht\OneDrive\Desktop\Data"

# Helper function to compare the outputs from Python and Matlab
def compare_outputs(ind_python, ind_matlab):
    """
    Compare the outputs from Python and Matlab.

    Parameters:
    ind_python (array): The 'ind' variable generated in Python.
    ind_matlab (array): The 'ind' variable loaded from Matlab.
    max_differences (int): The maximum number of differences to display in detail.

    Returns:
    None
    """
    # Compare the two 'ind' arrays
    if isinstance(ind_python, pd.DataFrame):
        ind_python.fillna(0, inplace=True)
        ind_python = ind_python.values
    if isinstance(ind_matlab, pd.DataFrame):
        ind_matlab = ind_matlab.values
    are_equal = np.array_equal(ind_python, ind_matlab)
    if are_equal:
        print("Are the 'ind' variables equal?", are_equal)
        return None

    # If not equal, provide detailed comparison
    if not are_equal:
        differences = np.where(ind_python != ind_matlab)
        row_indices, col_indices = differences

        # Summary of differences
        total_differences = len(row_indices)
        print(f"\nTotal differences found: {total_differences}")

        # Display a limited number of differences for detailed inspection
        # Display a limited number of differences for detailed inspection
        max_differences = 5
        print(f"Displaying the first {max_differences} differences:")
        for i in range(min(total_differences, max_differences)):
            r_idx = row_indices[i]
            c_idx = col_indices[i]
            print(f"\nDifference at index ({r_idx}, {c_idx}):")
            print(f"  ind_python[{r_idx}, {c_idx}] = {ind_python[r_idx, c_idx]}")
            print(f"  ind_matlab[{r_idx}, {c_idx}] = {ind_matlab[r_idx, c_idx]}")

        return differences

# Helper function to load matlab variables
def load_matlab_variable(variable_name, mat_file_path=mat_path):
    """
    Load a specific variable from a MATLAB .mat file. Converts data to lists then to native python floats
    and then to array of floats

    Parameters:
    variable_name (str): The name of the variable to load.
    mat_file_path (str): The path to the .mat file directory.

    Returns:
    variable: The loaded variable from the .mat file.
    """
    path = os.path.join(mat_file_path, variable_name)
    mat_data = loadmat(path, appendmat=True, variable_names=[variable_name], struct_as_record=False)
    if variable_name in mat_data:
        mat_data = mat_data[variable_name]
        mat_data_list = [[float(element) for element in row] for row in mat_data]
        mat_data_array = np.array(mat_data_list, dtype=float)
        return pd.DataFrame(mat_data_array)
    else:
        ve = ValueError(f"Variable '{variable_name}' not found in the .mat file")
        print(f"Value Error: {ve}")
        return None

# Load Matlab data
ret = load_matlab_variable('ret')
me = load_matlab_variable('me')
dates = load_matlab_variable('dates', os.path.join(mat_path, 'CRSP')).values.flatten()
nyse = load_matlab_variable('NYSE')
permnos = load_matlab_variable('permno', os.path.join(mat_path, 'CRSP')).values.flatten()

# ======================================== Test Function(s) ============================================================



# ======================================================================================================================

# Load the 'ind' variable from MATLAB for comparison
ind_test = load_matlab_variable('ind_test')

# Generate the 'ind' variable in Python and load its analog from Matlab
ind = makeUnivSortInd(var=-me, ptfNumThresh=5)
ind = makeUnivSortInd(var=-me, ptfNumThresh=[30, 70])
ind = makeUnivSortInd(var=-me, ptfNumThresh=[30, 70], breaksFilterInd=nyse)
ind = makeUnivSortInd(var=-me, ptfNumThresh=5, portfolioMassInd=me)

# Compare the generated 'ind' variable with the MATLAB 'ind_test' variable
differences = compare_outputs(ind, ind_test)


results_1 = aa.runUnivSort(params=params, ret=ret, ind=ind, mcap=me, dates=dates, plotFigure=0)



start = 196301
end = 202112

ret = ret[ret.index <= 202112]
ret.dropna(how='all', axis=1, inplace=True)
columns = ret.columns
columns = ret.columns.values

