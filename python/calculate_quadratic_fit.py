"""
Fit a quadratic polynomial to a two-row NumPy array of x-y data 
"""

__author__ = "Fabian"

import numpy as np


def calculate_quadratic_fit(data):
    """
    Parameters:
        data: ndarray, shape (2, M)
            x-y data to be fit. M is the number of data points.
    Returns:
        quadratic_coefficients: ndarray, shape (3,)
            Quadratic polynomial coefficients, ordered constant term first, then linear term, and quadratic term last.
    Raises:
        IndexError
            When the data array has inappropriate dimensions, including anything other than 2 rows or too few columns to fit a quadratic polynomial. 
    """

    if len(data) != 2:
        raise IndexError(f'Data has incorrect length of {len(data)}')
    elif len(data[0]) < 3:
        raise IndexError(f'Data has too short a length of {len(data[0])}')


    import numpy.polynomial.polynomial as polynomial

    return polynomial.polyfit(data[0], data[1], 2)    


if __name__ == '__main__':
    x = np.linspace(-1, 1)
    y = x**2
    test_coefficients = calculate_quadratic_fit(np.vstack((x, y)))
    # test_coefficients = calculate_quadratic_fit(np.vstack((x, y, x)))
    
    # coefficients = 
    print(f'constant_term. = {test_coefficients[0]:15.8f}')
    print(f'linear_term    = {test_coefficients[1]:15.8f}')
    print(f'quadratic_term = {test_coefficients[2]:15.8f}')
