"""Make a fit curve using fit polynomial coefficients, NumPy's polynomial, and minimum and maximum x-values."""

__author__ = "Fabian Anguiano"

import numpy as np
import numpy.polynomial.polynomial as polynomial


def fit_curve_array(quadratic_coefficients, minimum_x, maximum_x,
                    number_of_points=100):
    """Generate an x-y fit curve from quadratic polynomial coefficients.

    Parameters:
        quadratic_coefficients: ndarray, shape (3,)
            Quadratic polynomial coefficients, ordered constant
            term first, then linear term, and quadratic term last.
        minimum_x: float
            Starting value for the fit curve array.
        maximum_x: float
            Ending value for the fit curve array.
        number_of_points: int, optional
            Number of points N to return for final fit curve.
            Default is 100.
    Returns:
        fit_curve: ndarray, shape (2, N)
            x-y data created by the coefficients of the fit
            function. N is the number of function evaluation
            points.
    Raises:
        ArithmeticError
            When maximum_x < minimum_x.
        IndexError
            When number_of_points <= 2.
    """
    if maximum_x < minimum_x:
        raise ArithmeticError(
            f'maximum_x {maximum_x} is less than minimum_x {minimum_x}'
        )
    if number_of_points <= 2:
        raise IndexError(
            f'number_of_points {number_of_points} is too few'
        )

    x = np.linspace(minimum_x, maximum_x, number_of_points)
    y = polynomial.polyval(x, quadratic_coefficients)
    return np.vstack((x, y))


if __name__ == '__main__':
    print('Input: coefficients = [0, 0, 1], min_x = -2, max_x = 2, N = 100')
    print('Expected: fit_curve[1] should equal fit_curve[0]**2')
    test_fit_curve = fit_curve_array(np.array([0, 0, 1]), -2, 2)
    print(f'fit_curve shape  = {test_fit_curve.shape}')
    print(f'first point      = ({test_fit_curve[0, 0]:.4f}, '
          f'{test_fit_curve[1, 0]:.4f})')
    print(f'last point       = ({test_fit_curve[0, -1]:.4f}, '
          f'{test_fit_curve[1, -1]:.4f})')
    maximum_deviation = np.max(
        np.abs(test_fit_curve[1] - test_fit_curve[0]**2)
    )
    print(f'max |y - x**2|   = {maximum_deviation:.2e}')
