"""Fit a quadratic polynomial to a two-row NumPy array of x-y data."""

__author__ = "Fabian Anguiano"

import numpy as np
import numpy.polynomial.polynomial as polynomial


def calculate_quadratic_fit(data):
    """Fit a quadratic polynomial to x-y data.

    Parameters:
        data: ndarray, shape (2, M)
            x-y data to be fit. M is the number of data points.
    Returns:
        quadratic_coefficients: ndarray, shape (3,)
            Quadratic polynomial coefficients, ordered constant
            term first, then linear term, and quadratic term last.
    Raises:
        IndexError
            When the data array has inappropriate dimensions,
            including anything other than 2 rows or too few
            columns to fit a quadratic polynomial.
    """
    if len(data) != 2:
        raise IndexError(f'Data has incorrect length of {len(data)}')
    elif len(data[0]) < 3:
        raise IndexError(
            f'Data has too short a length of {len(data[0])}'
        )

    return polynomial.polyfit(data[0], data[1], 2)


if __name__ == '__main__':
    print('Input: y = x**2 on x in [-1, 1]')
    print('Expected coefficients: [0, 0, 1]')
    x = np.linspace(-1, 1)
    y = x**2
    test_coefficients = calculate_quadratic_fit(np.vstack((x, y)))
    print(f'constant_term  = {test_coefficients[0]:15.8f}')
    print(f'linear_term    = {test_coefficients[1]:15.8f}')
    print(f'quadratic_term = {test_coefficients[2]:15.8f}')
