import numpy as np


def gaussian(position):
    value = (1 / np.sqrt(2 * np.pi)) * np.exp(-0.5 * position**2)
    return value


if __name__ == "__main__":
    start = -4
    end = 4
    number_of_points = 41

    x_values = np.linspace(start, end, number_of_points)
    y_values = gaussian(x_values)

    print("x                g(x)")
    print("---------------------------")
    for x, y in zip(x_values, y_values):
        print(f"{x:8.2f}         {y:10.6f}")
