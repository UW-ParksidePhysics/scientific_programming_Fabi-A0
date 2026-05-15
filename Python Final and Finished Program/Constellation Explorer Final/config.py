"""Project-wide settings and constants for Constellation Explorer."""

__author__ = "Fabian Anguiano"

import os


# -------------------------------
# game speed and screen settings
# -------------------------------
FPS = 60                     # frames per second target
STAR_HIT_RADIUS = 38         # pixel distance to register a tap on a star
STAR_SNAP_RADIUS = 55        # pixel distance for a drag to snap to a star
STAR_SHINE_MS = 650          # milliseconds a star glows after being touched
SCROLL_VISIBLE = 5           # number of constellation names visible at once


# -------------------------------
# colors (RGB or RGBA tuples)
# -------------------------------
BG_COLOR = (6, 7, 18)                # dark background color
TEXT_COLOR = (250, 250, 255)         # main text color
MUTED_TEXT = (210, 215, 235)         # softer text color
PANEL_FILL = (16, 18, 38, 230)       # panel background color
PANEL_BORDER = (160, 175, 230)       # panel border color
ACCENT = (200, 220, 255)             # main highlight color
ACCENT_SOFT = (155, 180, 255)        # softer highlight color
SUCCESS = (220, 240, 255)            # success color
ERROR = (255, 200, 200)              # error color
HIGHLIGHT_BG = (50, 60, 110)         # color when a list item is hovered
SELECTED_BG = (75, 90, 160)          # color when a list item is selected

# default star colors
STAR_COLOR = (255, 250, 240)         # default star center color
STAR_GLOW = (220, 235, 255)          # default star glow color

# guide line colors
LINE_COLOR = (245, 245, 250)         # older line color
LINE_GUIDE = (75, 90, 140)           # older guide line color
GUIDE_LINE_GLOW = (75, 90, 140)      # outer guide glow
GUIDE_LINE_MID = (150, 165, 215)     # middle guide glow
GUIDE_LINE_CORE = (225, 232, 255)    # bright guide center
LINE_GLOW = (255, 230, 120)          # glow for finished lines

# finished line colors
EDGE_PENDING = (90, 110, 190, 140)   # unfinished line color
EDGE_DONE_CORE = (255, 250, 215)     # bright center of finished line
EDGE_DONE_MID = (255, 230, 120)      # middle glow of finished line
EDGE_DONE_GLOW = (255, 215, 80)      # outer glow of finished line

# old name kept for backward compatibility
EDGE_DONE = EDGE_DONE_CORE

# drag line colors
DRAG_LINE_CORE = (255, 252, 220)     # center of drag line
DRAG_LINE_GLOW = (255, 225, 110)     # glow of drag line

# star pulse colors
SHINE_CORE = (255, 248, 180)         # center of star pulse
SHINE_GLOW = (255, 220, 100)         # glow of star pulse


# -------------------------------
# layout ratios
# -------------------------------
DESIGN_RATIO = 16 / 10       # main screen shape ratio
CENTER_RATIO = 1.45          # draw area shape inside center panel


# -------------------------------
# star size tiers
# Lower magnitude value means a brighter and bigger star.
# Each tuple is (max magnitude, radius, glow radius, alpha).
# -------------------------------
STAR_TIERS = (
    (0.5, 10, 22, 255),   # very bright
    (1.5, 8, 17, 245),    # bright
    (2.5, 6, 13, 225),    # medium
    (10.0, 5, 10, 205),   # dim
)


# -------------------------------
# star color by B-V index
# -------------------------------
def color_from_bv(bv):
    """Convert a B-V color index into an approximate RGB star color.

    Parameters:
        bv: float or None
            The B-V color index for the star. When ``None`` the
            default warm-white fallback color is returned.
    Returns:
        color: tuple of int, shape (3,)
            An RGB tuple suitable for use with pygame drawing
            functions.
    """
    if bv is None:
        return (255, 250, 240)        # default warm white

    if bv < -0.30:
        return (170, 200, 255)        # blue
    if bv < -0.02:
        return (195, 215, 255)        # blue-white
    if bv < 0.30:
        return (230, 235, 255)        # white
    if bv < 0.58:
        return (255, 250, 230)        # yellow-white
    if bv < 0.81:
        return (255, 240, 195)        # yellow
    if bv < 1.40:
        return (255, 200, 140)        # orange
    return (255, 165, 110)            # red-orange


# fallback color words used when no B-V data is available
# more specific keywords are listed first
DESCRIPTION_COLOR_KEYWORDS = (
    ('blue-white', (195, 215, 255)),
    ('blue white', (195, 215, 255)),
    ('yellow-white', (255, 250, 230)),
    ('yellow white', (255, 250, 230)),
    ('red giant', (255, 165, 110)),
    ('red ', (255, 175, 120)),
    ('orange', (255, 200, 140)),
    ('yellow', (255, 240, 195)),
    ('blue', (180, 205, 255)),
    ('white', (235, 240, 255)),
    ('gold', (255, 235, 180)),
)


# -------------------------------
# viewing location
# -------------------------------
OBSERVER_LOCATION = 'Kenosha, WI (~42.6 N)'


# -------------------------------
# editor access (hidden in-game editor)
# -------------------------------
# Press the trigger combo in the game (default: Ctrl+Shift+E) to open the
# editor unlock prompt. Enter this code to unlock the editor.
#
# Change this to something only you know if you share the game with
# others. Anyone with access to this file can read the code, so this is
# "obscurity" protection, not real security.
EDITOR_ACCESS_CODE = 'stardust'

# Set to True to skip the unlock prompt entirely (always unlocked).
# Useful while developing.
EDITOR_NO_CODE = False


# -------------------------------
# file paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SEARCH_PATHS = [
    BASE_DIR,                       # current folder
    '/storage/emulated/0/Pv2',      # phone project folder
]


def resolve_path(*candidates):
    """Return the first existing path among several candidates.

    Parameters:
        *candidates: str
            One or more file paths to try, in order of preference.
            Absolute paths are checked as-is; relative paths are
            joined against each entry in ``SEARCH_PATHS``.
    Returns:
        path: str
            The first existing candidate, or the first candidate
            unchanged when none of the options exists.
    """
    for candidate in candidates:
        if os.path.isabs(candidate) and os.path.exists(candidate):
            return candidate

        for root in SEARCH_PATHS:
            path = os.path.join(root, candidate)
            if os.path.exists(path):
                return path

    # nothing found — fall back to the first candidate
    return candidates[0]


BACKGROUND_PATH = resolve_path(
    'Space.png',
    '/storage/emulated/0/Pv2/Space.png',
)

CONSTELLATIONS_PATH = resolve_path(
    'constellations_v2.json',
    '/storage/emulated/0/Pv2/constellations_v2.json',
)

STARS_PATH = resolve_path(
    'stars_v2.json',
    '/storage/emulated/0/Pv2/stars_v2.json',
)

# optional star color data
BV_CSV_PATH = resolve_path(
    'result-1.csv',
    '/storage/emulated/0/Pv2/result-1.csv',
)


if __name__ == '__main__':
    print('Input: B-V values -1.0, 0.0, 0.5, 1.5, None')
    print('Expected: a tuple of three ints in 0..255 for each call')
    for test_bv in (-1.0, 0.0, 0.5, 1.5, None):
        print(f'color_from_bv({test_bv!r:>5}) = {color_from_bv(test_bv)}')

    print()
    print('Input: resolve_path("config.py")')
    print('Expected: an absolute path that exists on disk')
    print(f'Result:   {resolve_path("config.py")}')
