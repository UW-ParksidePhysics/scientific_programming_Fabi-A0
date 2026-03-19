from math import sqrt, pi, exp


def gaussian(position):
    value = (1 / sqrt(2 * pi)) * exp(-0.5 * position**2)
    return value


if __name__ == "__main__":
    positions = []
    gaussian_values = []

    start = -4
    end = 4
    number_of_points = 41
    spacing = (end - start) / (number_of_points - 1)

    for index in range(number_of_points):
        x = start + index * spacing
        g = gaussian(x)

        positions.append(x)
        gaussian_values.append(g)

    print("x                g(x)")
    print("---------------------------")
    for x, g in zip(positions, gaussian_values):
        print(f"{x:8.2f}         {g:10.6f}")
