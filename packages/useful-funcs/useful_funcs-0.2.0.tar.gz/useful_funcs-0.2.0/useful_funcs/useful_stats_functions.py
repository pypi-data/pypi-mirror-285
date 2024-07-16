import numpy as np

def corrgiver0(var1: np.ndarray, var2: np.ndarray, lags):
    """Calculates lag-based Correlation Coefficients of two variables
    for lags provided. And returns these values as an array.
    
    --------
    Parameters
    ----------
    var1: np.ndarray
        1-D array containing n values of first variable.
    
    var2: np.ndarray
        1-D array containing n values of second variable.

    lags: int
        Number of lags to be provided
    
    Returns
    -------
    corr_list: np.ndarray
        1-D array containing (1+lags) number of elements which
        are the lag-based correlation coefficients of the given variables.
    
    Raises
    ------
    AssertionError
        
    """
    assert var1.__len__() == var2.__len__(), "var1 and var2 are not of equal length"
    assert var1.__len__() >= 3, "At least 3 elements are required per variable to calculate correlation coefficient"
    assert lags <= var1.__len__()-2, "Choose lower number of lags"

    corr_list = np.empty(lags+1, dtype=float)
    corr_list[0] = (np.corrcoef(var1, var2)[0,1])

    for i in range(1,lags+1):
        var1_sub = var1[i:]
        var2_sub = var2[:-i]
        corr_list[i] = (np.corrcoef(var1_sub, var2_sub)[0,1])

    return corr_list



