from math import sqrt, pi, exp


def gaussian(position):
    value = (1 / sqrt(2 * pi)) * exp(-0.5 * position**2)
    return value


if __name__ == "__main__":
    x_values = []
    y_values = []

    start = -4
    end = 4
    number_of_points = 41
    spacing = (end - start) / (number_of_points - 1)

    for index in range(number_of_points):
        x = start + index * spacing
        y = gaussian(x)

        x_values.append(x)
        y_values.append(y)

    print("x                g(x)")
    print("---------------------------")
    for x, y in zip(x_values, y_values):
        print(f"{x:8.2f}         {y:10.6f}")
