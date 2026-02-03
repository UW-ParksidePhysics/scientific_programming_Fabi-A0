"""
two_balls_bounce.py

Animate two balls bouncing off a wall using Plotly (3D).

This replaces the original VPython implementation.
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
    wall_x_position: float,
    time_step: float,
    stop_time: float,
) -> list[np.ndarray]:
    """
    Simulate elastic collisions with a vertical wall at x = wall_x_position.
    """
    positions_over_time: list[np.ndarray] = []

    positions = initial_positions.copy()
    velocities = initial_velocities.copy()
    current_time = 0.0

    while current_time <= stop_time:
        positions_over_time.append(positions.copy())

        for index in range(len(positions)):
            if positions[index, 0] >= wall_x_position:
                velocities[index, 0] *= -1.0

            positions[index] += velocities[index] * time_step

        current_time += time_step

    return positions_over_time


def build_wall_box_trace(
    wall_center_x: float,
    wall_center_y: float = 0.0,
    wall_center_z: float = 0.0,
    thickness_x: float = 0.25,
    height_y: float = 10.0,
    depth_z: float = 10.0,
    opacity: float = 0.5,
) -> go.Mesh3d:
    """
    Build a rectangular wall as a 3D box (rectangular prism), similar to VPython box.

    VPython example:
        box(pos=vector(x, y, z), size=vector(thickness_x, height_y, depth_z))
    """
    half_thickness_x = thickness_x / 2.0
    half_height_y = height_y / 2.0
    half_depth_z = depth_z / 2.0

    x_min = wall_center_x - half_thickness_x
    x_max = wall_center_x + half_thickness_x
    y_min = wall_center_y - half_height_y
    y_max = wall_center_y + half_height_y
    z_min = wall_center_z - half_depth_z
    z_max = wall_center_z + half_depth_z

    # 8 vertices of the box
    x_vertices = np.array([x_min, x_max, x_max, x_min, x_min, x_max, x_max, x_min])
    y_vertices = np.array([y_min, y_min, y_max, y_max, y_min, y_min, y_max, y_max])
    z_vertices = np.array([z_min, z_min, z_min, z_min, z_max, z_max, z_max, z_max])

    # 12 triangles (two per face) using vertex indices
    i_indices = np.array([0, 0, 1, 1, 4, 4, 5, 5, 0, 0, 2, 2])
    j_indices = np.array([1, 2, 2, 3, 5, 6, 6, 7, 4, 7, 6, 3])
    k_indices = np.array([2, 3, 3, 0, 6, 7, 7, 4, 7, 3, 3, 6])

    return go.Mesh3d(
        x=x_vertices,
        y=y_vertices,
        z=z_vertices,
        i=i_indices,
        j=j_indices,
        k=k_indices,
        opacity=opacity,
        color="red",
        flatshading=True,
    )


def build_animation_figure(
    positions_over_time: list[np.ndarray],
    ball_radius: float,
    wall_x_position: float,
) -> go.Figure:
    """Build a Plotly 3D animation of two bouncing balls."""
    frames = []

    for frame_index, positions in enumerate(positions_over_time):
        frame_traces = []

        for ball_index, (x_pos, y_pos, z_pos) in enumerate(positions):
            sphere_x, sphere_y, sphere_z = generate_sphere_mesh(
                center_x=x_pos,
                center_y=y_pos,
                center_z=z_pos,
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

    # Initial frame
    initial_traces = frames[0].data

    wall_box_trace = build_wall_box_trace(
        wall_center_x=wall_x_position,
        thickness_x=0.25,
        height_y=10.0,
        depth_z=10.0,
        opacity=0.5,
    )

    figure = go.Figure(data=[*initial_traces, wall_box_trace], frames=frames)

    figure.update_layout(
        title="Two Balls Bouncing Off a Wall (Plotly 3D)",
        scene=dict(
            xaxis=dict(range=[-12, 12], autorange=False, title="x"),
            yaxis=dict(range=[-6, 6], autorange=False, title="y"),
            zaxis=dict(range=[-6, 6], autorange=False, title="z"),
            aspectmode="manual",
            aspectratio=dict(x=2, y=1, z=1),
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
                                "frame": {"duration": 30, "redraw": True},
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
            [-10.0, 0.0, 0.0],
            [-8.0, 1.5, 0.0],
        ]
    )
    initial_velocities = np.array(
        [
            [25.0, 0.0, 0.0],
            [18.0, 0.0, 0.0],
        ]
    )

    wall_x_position = 0.0
    time_step = 0.01
    stop_time = 1.0
    ball_radius = 0.5

    positions_over_time = simulate_motion(
        initial_positions=initial_positions,
        initial_velocities=initial_velocities,
        wall_x_position=wall_x_position,
        time_step=time_step,
        stop_time=stop_time,
    )

    figure = build_animation_figure(
        positions_over_time=positions_over_time,
        ball_radius=ball_radius,
        wall_x_position=wall_x_position,
    )

    figure.show()


if __name__ == "__main__":
    main()
