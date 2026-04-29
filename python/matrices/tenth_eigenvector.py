import numpy as np
import matplotlib.pyplot as plt

matrix_dimension = 10

H = (1 / (2 * (1 / (matrix_dimension + 1))**2)) * (
    np.diagflat(2 * np.ones(matrix_dimension)) +
    np.diagflat(-1 * np.ones(matrix_dimension - 1), 1) +
    np.diagflat(-1 * np.ones(matrix_dimension - 1), -1)
)

values, vectors = np.linalg.eig(H)

index = np.argsort(values)
values = values[index]
vectors = vectors[:, index]

tenth_vector = -vectors[:, 0] * np.sqrt(matrix_dimension + 1)

x_values = np.linspace(
    1 / (matrix_dimension + 1),
    matrix_dimension / (matrix_dimension + 1),
    matrix_dimension
)

x = np.linspace(0, 1, 100)
y = np.sqrt(2) * np.sin(np.pi * x)

print("Eigenvalues:")
print(values)

print("Tenth Eigenvector:")
print(tenth_vector)

plt.plot(x_values, tenth_vector, "o", label="tenth eigenvector")
plt.plot(x, y, label="sqrt(2)sin(pi x)")
plt.xlabel("x")
plt.ylabel("y")
plt.legend()
plt.savefig("tenth_eigenvector.png")
plt.show()
