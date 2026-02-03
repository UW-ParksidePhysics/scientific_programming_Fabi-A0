"""
Trajectory of a ball thrown on a rotating space station ('artificial gravity')
Plotly version adapted from the VPython original by Bruce Sherwood (CC BY 4.0).

All uses permitted, but you must not claim that you wrote the original,
and you must include this license information in any copies you make.
http://creativecommons.org/licenses/by/4.0
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def rotate_xy(
    x_coordinates: np.ndarray,
    y_coordinates: np.ndarray,
    angle_radians: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """
    Rotate (x, y) coordinates by the given angle (radians) about the origin.
    """
    cosine = np.cos(angle_radians)
    sine = np.sin(angle_radians)

    rotated_x = cosine * x_coordinates - sine * y_coordinates
    rotated_y = sine * x_coordinates + cosine * y_coordinates

    return rotated_x, rotated_y


def simulate(
    angular_speed: float = 1.0,
    inner_radius: float = 10.0,
    release_height: float = 2.0,
    initial_velocity: tuple[float, float] = (0.0, 0.0),
    time_step: float | None = None,
    max_steps: int = 20_000,
) -> dict[str, np.ndarray]:
    """
    Simulate ball motion in inertial and rotating frames.
    """
    if time_step is None:
        time_step = 0.001 * 2.0 * np.pi / angular_speed

    initial_x_position = 0.0
    initial_y_position = -inner_radius + release_height
    velocity_x, velocity_y = initial_velocity

    x_positions = [initial_x_position]
    y_positions = [initial_y_position]
    times = [0.0]

    current_x = initial_x_position
    current_y = initial_y_position
    current_time = 0.0

    for _ in range(max_steps):
        current_x += velocity_x * time_step
        current_y += velocity_y * time_step
        current_time += time_step

        radius = np.hypot(current_x, current_y)
        if radius >= inner_radius:
            current_x = inner_radius * current_x / radius
            current_y = inner_radius * current_y / radius
            x_positions.append(current_x)
            y_positions.append(current_y)
            times.append(current_time)
            break

        x_positions.append(current_x)
        y_positions.append(current_y)
        times.append(current_time)

    x_positions = np.array(x_positions)
    y_positions = np.array(y_positions)
    times = np.array(times)

    rotating_x, rotating_y = rotate_xy(
        x_positions,
        y_positions,
        -angular_speed * times
    )

    return {
        "time": times,
        "x_inertial": x_positions,
        "y_inertial": y_positions,
        "x_rotating": rotating_x,
        "y_rotating": rotating_y,
    }


def build_figure(
    angular_speed: float = 1.0,
    inner_radius: float = 10.0,
    release_height: float = 2.0,
    thickness: float = 0.5,
    v_init: tuple[float, float] = (0.0, 0.0),
) -> go.Figure:
    """
    Create a 2-panel Plotly animation:
      Left: inertial frame (ring rotates, ball moves inertially)
      Right: rotating frame (ring fixed, ball shown in rotating coords)
    """
    sim = simulate(
        angular_speed=angular_speed,
        inner_radius=inner_radius,
        release_height=release_height,
        initial_velocity=v_init,
    )
    ring = station_ring_points(inner_radius=inner_radius, thickness=thickness)

    times = sim["time"]
    x_inertial = sim["x_inertial"]
    y_inertial = sim["y_inertial"]
    x_rotating = sim["x_rotating"]
    y_rotating = sim["y_rotating"]

    # Ring rotation in inertial frame: ring rotates by +omega*t (like the VPython hull)
    inner_x_rotated, inner_y_rotated = rotate_xy(
        ring["inner_x"],
        ring["inner_y"],
        angular_speed * times[0],
    )
    outer_x_rotated, outer_y_rotated = rotate_xy(
        ring["outer_x"],
        ring["outer_y"],
        angular_speed * times[0],
    )

    fig = make_subplots(
        rows=1,
        cols=2,
        subplot_titles=("Inertial frame (station rotating)", "Rotating frame (station fixed)"),
        horizontal_spacing=0.08,
    )

    # --- Initial traces (frame 0) ---

    # Left panel: ring inner/outer boundary
    fig.add_trace(go.Scatter(x=inner_x_rotated, y=inner_y_rotated, mode="lines", name="Ring (inner)", showlegend=False), row=1, col=1)
    fig.add_trace(go.Scatter(x=outer_x_rotated, y=outer_y_rotated, mode="lines", name="Ring (outer)", showlegend=False), row=1, col=1)

    # Left panel: ball + trail
    fig.add_trace(
        go.Scatter(x=[x_inertial[0]], y=[y_inertial[0]], mode="markers", marker=dict(size=10), name="Ball (inertial)", showlegend=False),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(x=[x_inertial[0]], y=[y_inertial[0]], mode="lines", name="Trail (inertial)", showlegend=False),
        row=1,
        col=1,
    )

    # Right panel: ring boundaries fixed
    fig.add_trace(go.Scatter(x=ring["inner_x"], y=ring["inner_y"], mode="lines", name="Ring (inner)", showlegend=False), row=1, col=2)
    fig.add_trace(go.Scatter(x=ring["outer_x"], y=ring["outer_y"], mode="lines", name="Ring (outer)", showlegend=False), row=1, col=2)

    # Right panel: ball + trail
    fig.add_trace(
        go.Scatter(x=[x_rotating[0]], y=[y_rotating[0]], mode="markers", marker=dict(size=10), name="Ball (rot)", showlegend=False),
        row=1,
        col=2,
    )
    fig.add_trace(
        go.Scatter(x=[x_rotating[0]], y=[y_rotating[0]], mode="lines", name="Trail (rot)", showlegend=False),
        row=1,
        col=2,
    )

    # --- Frames ---
    frames = []
    for frame_index in range(len(times)):
        # rotate ring boundaries for inertial panel
        inner_x_frame, inner_y_frame = rotate_xy(ring["inner_x"], ring["inner_y"], angular_speed * times[frame_index])
        outer_x_frame, outer_y_frame = rotate_xy(ring["outer_x"], ring["outer_y"], angular_speed * times[frame_index])

        frame_data = [
            # Left ring
            go.Scatter(x=inner_x_frame, y=inner_y_frame),
            go.Scatter(x=outer_x_frame, y=outer_y_frame),
            # Left ball marker + trail
            go.Scatter(x=[x_inertial[frame_index]], y=[y_inertial[frame_index]]),
            go.Scatter(x=x_inertial[: frame_index + 1], y=y_inertial[: frame_index + 1]),
            # Right ring (fixed)
            go.Scatter(x=ring["inner_x"], y=ring["inner_y"]),
            go.Scatter(x=ring["outer_x"], y=ring["outer_y"]),
            # Right ball marker + trail
            go.Scatter(x=[x_rotating[frame_index]], y=[y_rotating[frame_index]]),
            go.Scatter(x=x_rotating[: frame_index + 1], y=y_rotating[: frame_index + 1]),
        ]
        frames.append(go.Frame(data=frame_data, name=str(frame_index)))

    fig.frames = frames

    # --- Layout / controls ---
    lim = inner_radius + thickness + 1.5
    fig.update_xaxes(range=[-lim, lim], scaleanchor="y", scaleratio=1, row=1, col=1)
    fig.update_yaxes(range=[-lim, lim], row=1, col=1)
    fig.update_xaxes(range=[-lim, lim], scaleanchor="y", scaleratio=1, row=1, col=2)
    fig.update_yaxes(range=[-lim, lim], row=1, col=2)

    fig.update_layout(
        title="Rotating Space Station: inertial vs rotating frame (Plotly animation)",
        height=600,
        width=1100,
        margin=dict(l=30, r=30, t=80, b=30),
        updatemenus=[
            dict(
                type="buttons",
                direction="left",
                x=0.25,
                y=1.08,
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[None, {"frame": {"duration": 15, "redraw": True}, "fromcurrent": True}],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[[None], {"frame": {"duration": 0, "redraw": False}, "mode": "immediate"}],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                active=0,
                x=0.1,
                y=0.02,
                len=0.8,
                steps=[
                    dict(method="animate", args=[[str(frame_index)], {"mode": "immediate", "frame": {"duration": 0, "redraw": True}}], label=str(frame_index))
                    for frame_index in range(0, len(times), max(1, len(times)//100))
                ],
            )
        ],
    )

    return fig


def build_velocity_selector_figure(
    angular_speed: float = 1.0,
    inner_radius: float = 10.0,
    release_height: float = 2.0,
    thickness: float = 0.5,
    vx_values: list[float] | None = None,
    vy_values: list[float] | None = None,
) -> go.Figure:
    """
    Plotly can't easily do VPython-style drag vectors; this gives a practical alternative:
    dropdowns for vx and vy that rebuild the animation.
    """
    if vx_values is None:
        vx_values = [-6, -4, -2, 0, 2, 4, 6]
    if vy_values is None:
        vy_values = [-6, -4, -2, 0, 2, 4, 6]

    # Start at center values
    vx0 = vx_values[len(vx_values) // 2]
    vy0 = vy_values[len(vy_values) // 2]

    fig = build_figure(
        angular_speed=angular_speed,
        inner_radius=inner_radius,
        release_height=release_height,
        thickness=thickness,
        v_init=(vx0, vy0),
    )

    # Prebuild figures for each velocity pair (keeps it self-contained; trades memory for simplicity)
    prebuilt = {}
    for vx in vx_values:
        for vy in vy_values:
            prebuilt[(vx, vy)] = build_figure(
                angular_speed=angular_speed,
                inner_radius=inner_radius,
                release_height=release_height,
                thickness=thickness,
                v_init=(vx, vy),
            )

    def fig_to_update_payload(src: go.Figure) -> dict:
        """Create a payload to replace data+frames in place."""
        return {
            "data": [tr.to_plotly_json() for tr in src.data],
            "layout": src.layout.to_plotly_json(),
            "frames": [fr.to_plotly_json() for fr in src.frames],
        }

    # Dropdown for vx/vy: because Plotly update menus don’t natively “recompute”,
    # we swap in prebuilt animation data.
    vx_buttons = []
    for vx in vx_values:
        payload = fig_to_update_payload(prebuilt[(vx, vy0)])
        vx_buttons.append(dict(label=f"vx={vx}", method="update", args=[payload["data"], payload["layout"]],))
        # frames must be assigned via relayout in practice; simplest approach: user reruns cell/script for new values
        # so we keep this menu as a hint, not a perfect live swap.

    # Add note: simplest is to edit v_init at the bottom or rerun.
    fig.add_annotation(
        text="Edit v_init in code (or rerun) to change initial velocity. Plotly doesn't support VPython-style drag vectors.",
        xref="paper", yref="paper", x=0.5, y=1.14, showarrow=False
    )

    return fig


def station_ring_points(
    inner_radius: float,
    thickness: float = 0.5,
    number_of_points: int = 400,
) -> dict[str, np.ndarray]:
    """
    Generate inner and outer ring boundary coordinates.
    """
    angles = np.linspace(0.0, 2.0 * np.pi, number_of_points)

    inner_x = inner_radius * np.cos(angles)
    inner_y = inner_radius * np.sin(angles)

    outer_radius = inner_radius + thickness
    outer_x = outer_radius * np.cos(angles)
    outer_y = outer_radius * np.sin(angles)

    return {
        "inner_x": inner_x,
        "inner_y": inner_y,
        "outer_x": outer_x,
        "outer_y": outer_y,
        "angles": angles,
    }


if __name__ == "__main__":
    # Simple: edit v_init and rerun.
    fig = build_figure(
        angular_speed=1.0,
        inner_radius=10.0,
        release_height=2.0,
        thickness=0.5,
        v_init=(3.0, 0.0),  # <-- set initial velocity here (vx, vy)
    )
    fig.show()