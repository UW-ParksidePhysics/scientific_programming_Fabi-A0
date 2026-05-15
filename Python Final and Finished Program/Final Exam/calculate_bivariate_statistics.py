"""Calculate statistical characteristics of a data set."""

__author__ = "Fabian Anguiano"

import numpy as np
from scipy import stats


def calculate_bivariate_statistics(data):
    """Calculate statistical statistics for x-y data.

    Parameters:
        data: ndarray, shape (2, M)
            x-y data to be characterized. M is the number of
            data points.
    Returns:
        statistics: ndarray, shape (6,)
            Mean of y, standard deviation of y, minimum
            x-value, maximum x-value, minimum y-value,
            maximum y-value.
    Raises:
        IndexError
            When the data array has inappropriate dimensions,
            including anything other than 2 rows or fewer
            than 2 columns.
    """
    if len(data) != 2:
        raise IndexError(f'Data has incorrect length of {len(data)}')
    elif len(data[0]) < 2:
        raise IndexError(
            f'Data has too short a length of {len(data[0])}'
        )

    description = stats.describe(data[1])
    mean_y = description.mean
    standard_deviation_y = np.sqrt(description.variance)
    minimum_x = np.min(data[0])
    maximum_x = np.max(data[0])
    minimum_y = description.minmax[0]
    maximum_y = description.minmax[1]

    return np.array([
        mean_y,
        standard_deviation_y,
        minimum_x,
        maximum_x,
        minimum_y,
        maximum_y,
    ])


if __name__ == '__main__':
    print('Input: y = x**2 on x in [-10, 10]')
    print('Expected: mean_y ~ 36.67, min_x = -10, max_x = 10,')
    print('          min_y = 0, max_y = 100')
    x = np.linspace(-10, 10, 21)
    y = x**2
    test_statistics = calculate_bivariate_statistics(np.vstack((x, y)))
    print(f'mean of y          = {test_statistics[0]:15.8f}')
    print(f'std deviation of y = {test_statistics[1]:15.8f}')
    print(f'minimum x          = {test_statistics[2]:15.8f}')
    print(f'maximum x          = {test_statistics[3]:15.8f}')
    print(f'minimum y          = {test_statistics[4]:15.8f}')
    print(f'maximum y          = {test_statistics[5]:15.8f}')
