"""Create a combined scatter and curve plot of x-y data and a fit curve."""

__author__ = "Fabian Anguiano"

import numpy as np
import matplotlib.pyplot as plt


def plot_data_with_fit(data, fit_curve, data_format='o', fit_format=''):
    """Plot x-y data as scatter points alongside a fit polynomial curve.

    Parameters:
        data: ndarray, shape (2, M)
            x-y data that was fit. M is the number of data
            points.
        fit_curve: ndarray, shape (2, N)
            x-y data created by the coefficients of the fit
            function. N is the number of function evaluation
            points, usually much greater than M.
        data_format: str, optional
            Optional formatting specification for the style
            of the scatter plot data points. Default is 'o'.
        fit_format: str, optional
            Optional formatting specification for the curve
            of the fit function. Default is ''.
    Returns:
        combined_plot
            A list of Line2D objects representing the plotted
            data. This is the default return type from
            Pyplot's plot.
    Raises:
        IndexError
            When either input array does not have shape
            (2, M) or (2, N).
    """
    if len(data) != 2:
        raise IndexError(
            f'data has incorrect length of {len(data)}'
        )
    if len(fit_curve) != 2:
        raise IndexError(
            f'fit_curve has incorrect length of {len(fit_curve)}'
        )

    combined_plot = plt.plot(
        data[0], data[1], data_format,
        fit_curve[0], fit_curve[1], fit_format,
    )
    return combined_plot


if __name__ == '__main__':
    print('Input: data      = [[-2,-1,0,1,2], [4,1,0,1,4]]')
    print('       fit_curve = [linspace(-2,2), linspace(-2,2)**2]')
    print('Expected: scatter points marked "x" with a dashed parabola')
    test_data = np.array([[-2, -1, 0, 1, 2], [4, 1, 0, 1, 4]])
    test_fit_curve = np.array(
        [np.linspace(-2, 2), np.linspace(-2, 2)**2]
    )
    test_combined_plot = plot_data_with_fit(
        test_data, test_fit_curve,
        data_format='x', fit_format='--',
    )
    print(f'Returned {len(test_combined_plot)} Line2D objects')
    plt.show()
