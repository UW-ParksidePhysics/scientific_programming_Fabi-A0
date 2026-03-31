import numpy as np
import matplotlib.pyplot as plt


def wave_packet(x, t, alpha, f, k, omega):
    value = np.exp(-(alpha * x - f * t)**2) * np.sin(k * x - omega * t)
    return value


if __name__ == "__main__":
    t = 0
    f = 3
    k = 3 * np.pi
    omega = 3 * np.pi

    x_values = np.linspace(-4, 4, 1001)

    alpha_values = [0.5, 1, 2]

    for alpha in alpha_values:
        y_values = wave_packet(x_values, t, alpha, f, k, omega)
        plt.plot(x_values, y_values, label=f"alpha = {alpha}")

    plt.title("Wave Packet")
    plt.xlabel("x")
    plt.ylabel("f(x, t)")
    plt.grid()
    plt.legend()

    plt.show()
