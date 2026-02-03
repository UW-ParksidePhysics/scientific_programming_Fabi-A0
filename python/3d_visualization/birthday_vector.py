import numpy as np
import plotly.graph_objects as go


def thick_3d_line(position_start, position_end, color, line_width=10, name=None):
    """
    Render a cylinder-like 3D axis using a thick line.
    """
    return go.Scatter3d(
        x=[position_start[0], position_end[0]],
        y=[position_start[1], position_end[1]],
        z=[position_start[2], position_end[2]],
        mode="lines",
        line=dict(color=color, width=line_width),
        name=name,
        showlegend=False,
    )


def arrow_3d(
    position_start,
    position_end,
    color="white",
    line_width=10,
    head_fraction=0.18,
    head_size_reference=0.6,
    name=None,
):
    """
    Render a 3D arrow using a line for the shaft and a cone for the head.
    """
    position_start = np.array(position_start, dtype=float)
    position_end = np.array(position_end, dtype=float)

    direction_vector = position_end - position_start
    vector_length = np.linalg.norm(direction_vector)

    if vector_length == 0:
        raise ValueError("Arrow length must be nonzero.")

    head_length = head_fraction * vector_length
    shaft_end_position = (
        position_end - (head_length / vector_length) * direction_vector
    )

    shaft = go.Scatter3d(
        x=[position_start[0], shaft_end_position[0]],
        y=[position_start[1], shaft_end_position[1]],
        z=[position_start[2], shaft_end_position[2]],
        mode="lines",
        line=dict(color=color, width=line_width),
        name=name,
        showlegend=False,
    )

    cone = go.Cone(
        x=[shaft_end_position[0]],
        y=[shaft_end_position[1]],
        z=[shaft_end_position[2]],
        u=[position_end[0] - shaft_end_position[0]],
        v=[position_end[1] - shaft_end_position[1]],
        w=[position_end[2] - shaft_end_position[2]],
        anchor="tail",
        colorscale=[[0, color], [1, color]],
        showscale=False,
        sizemode="scaled",
        sizeref=head_size_reference,
        name=name,
        showlegend=False,
    )

    return shaft, cone


# Scene parameters
axis_length = 10
label_offset = 1.0

# Coordinate axes
x_axis = thick_3d_line(
    position_start=(0, 0, 0),
    position_end=(axis_length, 0, 0),
    color="red",
    line_width=8,
    name="X axis",
)

y_axis = thick_3d_line(
    position_start=(0, 0, 0),
    position_end=(0, axis_length, 0),
    color="green",
    line_width=8,
    name="Y axis",
)

z_axis = thick_3d_line(
    position_start=(0, 0, 0),
    position_end=(0, 0, axis_length),
    color="blue",
    line_width=8,
    name="Z axis",
)

# Vector r
arrow_shaft, arrow_head = arrow_3d(
    position_start=(0, 0, 0),
    position_end=(2, 10, 7),
    color="gray",
    line_width=10,
    head_size_reference=0.7,
    name="r",
)

figure = go.Figure(
    data=[x_axis, y_axis, z_axis, arrow_shaft, arrow_head]
)

figure.update_layout(
    width=600,
    height=600,
    paper_bgcolor="white",
    scene=dict(
        bgcolor="white",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        zaxis=dict(visible=False),
        annotations=[
            dict(
                x=axis_length + label_offset,
                y=0,
                z=0,
                text=r"$x$",
                showarrow=False,
                font=dict(color="red", size=18),
            ),
            dict(
                x=0,
                y=axis_length + label_offset,
                z=0,
                text=r"$y$",
                showarrow=False,
                font=dict(color="green", size=18),
            ),
            dict(
                x=0,
                y=0,
                z=axis_length + label_offset,
                text=r"$z$",
                showarrow=False,
                font=dict(color="blue", size=18),
            ),
        ],
        camera=dict(
            eye=dict(x=0.5, y=0.3, z=1.0)
        ),
        aspectmode="data",
    ),
    margin=dict(l=0, r=0, t=0, b=0),
)

figure.show()