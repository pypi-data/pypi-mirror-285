import numpy as np
import pandas as pd


def check_and_clean_sort_variables(var: [np.ndarray, pd.DataFrame], ptfNumThresh: [int, float, list, np.ndarray],
                                   breaksFilterInd=None, portfolioMassInd=None) -> None:
    # Validate inputs
    if not (isinstance(var, pd.DataFrame) or isinstance(var, np.ndarray)):
        raise ValueError("Input 'var' must be a DataFrame or a NumPy array.")

    if not np.isscalar(ptfNumThresh) and not isinstance(ptfNumThresh, (np.ndarray, list)):
        raise ValueError("Input 'ptfNumThresh' must be a scalar, list, or a NumPy array.")

    if breaksFilterInd is not None:
        if not (isinstance(breaksFilterInd, pd.DataFrame) or isinstance(breaksFilterInd, np.ndarray)):
            raise ValueError("Input 'breaksFilterInd' must be a DataFrame, a NumPy array, or None.")
        if var.shape != breaksFilterInd.shape:
            raise ValueError(f"Input 'breaksFilterInd' has shape {breaksFilterInd.shape} but 'var' has shape {var.shape}.")

    if portfolioMassInd is not None:
        if not (isinstance(portfolioMassInd, pd.DataFrame) or isinstance(portfolioMassInd, np.ndarray)):
            raise ValueError("Input 'portfolioMassInd' must be a DataFrame, a NumPy array, or None.")
        if var.shape != portfolioMassInd.shape:
            raise ValueError(f"Input 'portfolioMassInd' has shape {portfolioMassInd.shape} but must have the same shape"
                             f"as 'var', {var.shape}.")

        return

