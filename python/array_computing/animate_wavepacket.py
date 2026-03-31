import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


def wave_packet(x, t, alpha, f, k, omega):
    return np.exp(-(alpha * x - f * t)**2) * np.sin(k * x - omega * t)


if __name__ == "__main__":
    # parameters (same as problem 26)
    alpha = 1
    f = 3
    k = 3 * np.pi
    omega = 3 * np.pi

    # x and t values
    x_values = np.linspace(-6, 6, 1001)
    t_values = np.linspace(-1, 1, 61)

    fig, ax = plt.subplots()
    line, = ax.plot(x_values, wave_packet(x_values, t_values[0], alpha, f, k, omega))

    ax.set_xlim(-6, 6)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlabel("x")
    ax.set_ylabel("f(x, t)")
    ax.set_title("Wave Packet Animation")

    def update(frame):
        t = t_values[frame]
        y = wave_packet(x_values, t, alpha, f, k, omega)
        line.set_ydata(y)
        return line,

    animation = FuncAnimation(fig, update, frames=len(t_values), interval=1000/6)

    # save GIF
    animation.save("wavepacket.gif", writer=PillowWriter(fps=6))

    plt.show()
