"""Annotate a plot with text labels using Pyplot's text function."""

__author__ = "Fabian Anguiano"

from datetime import date

import numpy as np
import matplotlib.pyplot as plt


def annotate_plot(annotations):
    """Place text annotations on the current figure.

    Parameters:
        annotations: dict
            Dictionary whose keys are the label strings to
            be annotated and whose values are dictionaries
            with the following key-value pairs:
                'position': ndarray, shape (2,)
                    x, y coordinates (figure-relative, 0 to
                    1) for the position of the textbox.
                'alignment': list or tuple of str, shape (2,)
                    Horizontal alignment and vertical
                    alignment values for the text function.
                'fontsize': float
                    Value of the font size in points.
    Returns:
        annotation_objects: list
            List of text annotation objects returned by
            Pyplot's text function.
    Raises:
        KeyError
            When a required key is missing from the
            annotation dictionary.
    """
    annotation_objects = []
    for label, properties in annotations.items():
        try:
            position = properties['position']
            alignment = properties['alignment']
            fontsize = properties['fontsize']
        except KeyError as missing_key:
            raise KeyError(
                f'Annotation for {label!r} is missing key {missing_key}'
            )

        text_object = plt.text(
            position[0], position[1], label,
            horizontalalignment=alignment[0],
            verticalalignment=alignment[1],
            fontsize=fontsize,
            transform=plt.gcf().transFigure,
        )
        annotation_objects.append(text_object)

    return annotation_objects


if __name__ == '__main__':
    today_iso = date.today().isoformat()
    signature = f'Created by Fabian Anguiano {today_iso}'
    print(f'Input: annotation labeled "{signature}"')
    print('Expected: signature shown in the bottom-left of the figure,')
    print('          below the axes labels and tickmarks')

    x = np.linspace(-2, 2, 50)
    y = x**2
    plt.plot(x, y)
    plt.xlabel('x')
    plt.ylabel('y')
    plt.title('Test plot for annotate_plot')

    test_annotations = {
        signature: {
            'position': np.array([0.02, 0.02]),
            'alignment': ('left', 'bottom'),
            'fontsize': 8.0,
        }
    }
    test_annotation_objects = annotate_plot(test_annotations)
    print(f'Returned {len(test_annotation_objects)} text object(s)')
    plt.show()
