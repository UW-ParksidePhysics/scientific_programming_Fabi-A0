"""Read in two columns of data from a text file of arbitrary length."""

__author__ = "Fabian Anguiano"

import numpy as np


def read_two_columns_text(filename):
    """Read two columns of x-y data from a text file.

    Parameters:
        filename: str
            Name of file to be read in.
    Returns:
        data: ndarray, shape (2, M)
            x-y data read in from file. M is the number of
            data points.
    Raises:
        OSError
            When filename cannot be found for reading.
    """
    try:
        data = np.loadtxt(filename)
    except FileNotFoundError:
        raise OSError(f'File {filename} not found for reading')

    return data.T


if __name__ == '__main__':
    print('Input: volumes_energies.dat')
    print('Expected: shape (2, M) where M is the number of rows in file')
    data = read_two_columns_text('volumes_energies.dat')
    print(f'{data=}, shape={data.shape}')
