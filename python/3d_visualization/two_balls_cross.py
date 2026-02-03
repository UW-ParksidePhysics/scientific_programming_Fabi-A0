"""
two_balls_cross.py

Animate two balls moving linearly and crossing paths using Plotly (3D).

This is a Plotly replacement for the original VPython version and follows the
same overall structure as two_balls_bounce.py (physics simulation + figure builder).
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go


def generate_sphere_mesh(
    center_x: float,
    center_y: float,
    center_z: float,
    radius: float,
    number_of_latitudes: int = 24,
    number_of_longitudes: int = 48,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate surface coordinates for a sphere."""
    phi_angles = np.linspace(0.0, np.pi, number_of_latitudes)
    theta_angles = np.linspace(0.0, 2.0 * np.pi, number_of_longitudes)
    phi_grid, theta_grid = np.meshgrid(phi_angles, theta_angles, indexing="ij")

    x_coordinates = center_x + radius * np.sin(phi_grid) * np.cos(theta_grid)
    y_coordinates = center_y + radius * np.sin(phi_grid) * np.sin(theta_grid)
    z_coordinates = center_z + radius * np.cos(phi_grid)

    return x_coordinates, y_coordinates, z_coordinates


def simulate_motion(
    initial_positions: np.ndarray,
    initial_velocities: np.ndarray,
    time_step: float,
    stop_time: float,
) -> list[np.ndarray]:
    """
    Simulate linear motion (constant velocity) for each ball.

    Returns a list of positions arrays, one per time step. Each positions array
    has shape (number_of_balls, 3).
    """
    positions_over_time: list[np.ndarray] = []

    positions = initial_positions.copy()
    velocities = initial_velocities.copy()
    current_time = 0.0

    while current_time <= stop_time:
        positions_over_time.append(positions.copy())
        positions = positions + velocities * time_step
        current_time += time_step

    return positions_over_time


def build_animation_figure(
    positions_over_time: list[np.ndarray],
    ball_radius: float,
) -> go.Figure:
    """Build a Plotly 3D animation of two linearly moving balls."""
    frames: list[go.Frame] = []

    for frame_index, positions in enumerate(positions_over_time):
        frame_traces: list[go.Surface] = []

        for x_position, y_position, z_position in positions:
            sphere_x, sphere_y, sphere_z = generate_sphere_mesh(
                center_x=float(x_position),
                center_y=float(y_position),
                center_z=float(z_position),
                radius=ball_radius,
            )
            frame_traces.append(
                go.Surface(
                    x=sphere_x,
                    y=sphere_y,
                    z=sphere_z,
                    showscale=False,
                )
            )

        frames.append(go.Frame(data=frame_traces, name=str(frame_index)))

    initial_traces = frames[0].data
    figure = go.Figure(data=[*initial_traces], frames=frames)

    figure.update_layout(
        title="Two Balls Crossing (Plotly 3D)",
        scene=dict(
            xaxis=dict(range=[-2, 2], autorange=False, title="x"),
            yaxis=dict(range=[-2, 2], autorange=False, title="y"),
            zaxis=dict(range=[-2, 2], autorange=False, title="z"),
            aspectmode="manual",
            aspectratio=dict(x=1, y=1, z=1),
        ),
        uirevision="lock",
        updatemenus=[
            dict(
                type="buttons",
                showactive=False,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {"duration": 40, "redraw": True},
                                "transition": {"duration": 0},
                                "fromcurrent": True,
                                "mode": "immediate",
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"mode": "immediate", "frame": {"duration": 0, "redraw": False}}],
                    ),
                ],
            )
        ],
    )

    return figure


def main() -> None:
    """Run the simulation and display the animation."""
    initial_positions = np.array(
        [
            [-1.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
        ],
        dtype=float,
    )
    initial_velocities = np.array(
        [
            [0.3, 0.3, 0.0],
            [-0.3, 0.3, 0.0],
        ],
        dtype=float,
    )

    time_step = 0.05
    stop_time = 10.0
    ball_radius = 0.1

    positions_over_time = simulate_motion(
        initial_positions=initial_positions,
        initial_velocities=initial_velocities,
        time_step=time_step,
        stop_time=stop_time,
    )

    figure = build_animation_figure(
        positions_over_time=positions_over_time,
        ball_radius=ball_radius,
    )
    figure.show()


if __name__ == "__main__":
    main()
