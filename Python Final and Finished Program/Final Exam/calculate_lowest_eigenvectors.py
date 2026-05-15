"""Identify the eigenvectors with the smallest K eigenvalues for an input matrix."""

__author__ = "Fabian Anguiano"

import numpy as np


def calculate_lowest_eigenvectors(square_matrix, number_of_eigenvectors=3):
    """Find the eigenvectors corresponding to the K smallest eigenvalues.

    Parameters:
        square_matrix: ndarray, shape (M, M)
            Matrix to be characterized. Must be a square
            matrix of M rows and M columns where M is at
            least 1.
        number_of_eigenvectors: int, optional
            Number of eigenvectors K with eigenvalues to
            return. Default is 3.
    Returns:
        eigenvalues: ndarray, shape (K,)
            Array of the K lowest-value eigenvalues ordered
            from lowest to highest.
        eigenvectors: ndarray, shape (K, M)
            Array of K eigenvectors with M components
            arranged in order corresponding to their
            eigenvalues. The first index corresponds to the
            eigenvalue index in the eigenvalues array. The
            order of the components in each eigenvector is
            the same as output by NumPy's eig.
    Raises:
        IndexError
            When square_matrix is not square or when
            number_of_eigenvectors is less than 1 or
            greater than the number of rows in the matrix.
    """
    if len(square_matrix) != len(square_matrix[0]):
        raise IndexError(
            f'square_matrix has {len(square_matrix)} rows and '
            f'{len(square_matrix[0])} columns, not square'
        )
    if (number_of_eigenvectors < 1 or
            number_of_eigenvectors > len(square_matrix)):
        raise IndexError(
            f'number_of_eigenvectors {number_of_eigenvectors} '
            f'is out of range [1, {len(square_matrix)}]'
        )

    all_eigenvalues, all_eigenvectors = np.linalg.eig(square_matrix)
    sort_order = np.argsort(all_eigenvalues)
    selected = sort_order[:number_of_eigenvectors]

    eigenvalues = all_eigenvalues[selected]
    eigenvectors = all_eigenvectors[:, selected].T

    return eigenvalues, eigenvectors


if __name__ == '__main__':
    print('Input: square_matrix = [[2, -1], [-1, 2]], K = 2')
    print('Expected eigenvalues: [1, 3]')
    print('Expected eigenvectors (up to sign):')
    print('  for lambda = 1: [ 1/sqrt(2),  1/sqrt(2)] ~ [ 0.7071,  0.7071]')
    print('  for lambda = 3: [ 1/sqrt(2), -1/sqrt(2)] ~ [ 0.7071, -0.7071]')
    test_matrix = np.array([[2, -1], [-1, 2]])
    test_eigenvalues, test_eigenvectors = calculate_lowest_eigenvectors(
        test_matrix, number_of_eigenvectors=2
    )
    print(f'eigenvalues  = {test_eigenvalues}')
    print(f'eigenvectors =\n{test_eigenvectors}')
