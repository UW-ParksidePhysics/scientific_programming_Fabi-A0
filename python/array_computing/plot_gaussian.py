import numpy as np
import matplotlib.pyplot as plt


def gaussian(position):
    value = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * position**2)
    return value


if __name__ == "__main__":
    start = -4
    end = 4
    number_of_points = 41

    x_values = np.linspace(start, end, number_of_points)
    y_values = gaussian(x_values)

    plt.plot(x_values, y_values)

    plt.title("Gaussian Function")
    plt.xlabel("x")
    plt.ylabel("g(x)")
    plt.grid()

    plt.show()
