"""
ball.py

Render a simple 3D sphere ("ball") using Plotly.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go


def generate_sphere_mesh(
    radius: float = 1.0,
    center_x: float = 0.0,
    center_y: float = 0.0,
    center_z: float = 0.0,
    number_of_latitudes: int = 60,
    number_of_longitudes: int = 120,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Generate x, y, z coordinate arrays for a sphere surface mesh.

    Uses spherical coordinates:
      x = cx + r sin(phi) cos(theta)
      y = cy + r sin(phi) sin(theta)
      z = cz + r cos(phi)
    """
    phi_angles = np.linspace(0.0, np.pi, number_of_latitudes)
    theta_angles = np.linspace(0.0, 2.0 * np.pi, number_of_longitudes)

    phi_grid, theta_grid = np.meshgrid(phi_angles, theta_angles, indexing="ij")

    x_coordinates = center_x + radius * np.sin(phi_grid) * np.cos(theta_grid)
    y_coordinates = center_y + radius * np.sin(phi_grid) * np.sin(theta_grid)
    z_coordinates = center_z + radius * np.cos(phi_grid)

    return x_coordinates, y_coordinates, z_coordinates


def build_sphere_figure(
    radius: float = 1.0,
    center_x: float = 0.0,
    center_y: float = 0.0,
    center_z: float = 0.0,
) -> go.Figure:
    """Build and return a Plotly figure containing a 3D sphere."""
    x_coordinates, y_coordinates, z_coordinates = generate_sphere_mesh(
        radius=radius,
        center_x=center_x,
        center_y=center_y,
        center_z=center_z,
    )

    surface_trace = go.Surface(
        x=x_coordinates,
        y=y_coordinates,
        z=z_coordinates,
        showscale=False,
    )

    figure = go.Figure(data=[surface_trace])
    figure.update_layout(
        title="3D Sphere (Plotly)",
        scene=dict(
            xaxis_title='x',
            yaxis_title='y',
            zaxis_title='z',
            aspectmode="data",
        ),
        margin=dict(l=0, r=0, t=50, b=0),
    )
    return figure


def main() -> None:
    """Render the sphere in a browser or notebook output."""
    figure = build_sphere_figure(radius=1.0)
    figure.show()


if __name__ == "__main__":
    main()
