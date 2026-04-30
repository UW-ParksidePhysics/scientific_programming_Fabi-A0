"""
config.py
This file keeps the main settings for the program.

It stores things like:
- speed
- colors
- sizes
- star settings
- file paths
"""

import os


# -------------------------------
# game speed and screen settings
# -------------------------------
FPS = 60                     # how fast the program updates
STAR_HIT_RADIUS = 38         # how close you need to tap a star
STAR_SNAP_RADIUS = 55        # how close your drag needs to get to a star
STAR_SHINE_MS = 650          # how long a star glows after being touched
SCROLL_VISIBLE = 5           # how many constellation names show at once


# -------------------------------
# colors
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
LINE_GUIDE      = (75,  90, 140)     # older guide line color
GUIDE_LINE_GLOW = (75,  90, 140)     # outer guide glow
GUIDE_LINE_MID  = (150, 165, 215)    # middle guide glow
GUIDE_LINE_CORE = (225, 232, 255)    # bright guide center
LINE_GLOW = (255, 230, 120)          # glow for finished lines

# finished line colors
EDGE_PENDING = (90, 110, 190, 140)   # unfinished line color
EDGE_DONE_CORE = (255, 250, 215)     # bright center of finished line
EDGE_DONE_MID  = (255, 230, 120)     # middle glow of finished line
EDGE_DONE_GLOW = (255, 215,  80)     # outer glow of finished line

# old name kept for compatibility
EDGE_DONE = EDGE_DONE_CORE

# drag line colors
DRAG_LINE_CORE = (255, 252, 220)     # center of drag line
DRAG_LINE_GLOW = (255, 225, 110)     # glow of drag line

# star pulse colors
SHINE_CORE = (255, 248, 180)         # center of star pulse
SHINE_GLOW = (255, 220, 100)         # glow of star pulse


# -------------------------------
# layout settings
# -------------------------------
DESIGN_RATIO = 16 / 10       # main screen shape ratio
CENTER_RATIO = 1.45          # draw area shape inside center panel


# -------------------------------
# star size groups
# lower number = brighter star = bigger size
# each group is:
# (max brightness value, size, glow size, alpha)
# -------------------------------
STAR_TIERS = (
    (0.5, 10, 22, 255),   # very bright
    (1.5,  8, 17, 245),   # bright
    (2.5,  6, 13, 225),   # medium
    (10.0, 5, 10, 205),   # dim
)


# -------------------------------
# star color by B-V value
# -------------------------------
def color_from_bv(bv):
    """
    Turn a B-V value into a star color.
    If there is no value, use warm white.
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


# backup color words if B-V data is missing
# more specific words go first
DESCRIPTION_COLOR_KEYWORDS = (
    ('blue-white',   (195, 215, 255)),
    ('blue white',   (195, 215, 255)),
    ('yellow-white', (255, 250, 230)),
    ('yellow white', (255, 250, 230)),
    ('red giant',    (255, 165, 110)),
    ('red ',         (255, 175, 120)),
    ('orange',       (255, 200, 140)),
    ('yellow',       (255, 240, 195)),
    ('blue',         (180, 205, 255)),
    ('white',        (235, 240, 255)),
    ('gold',         (255, 235, 180)),
)


# -------------------------------
# viewing location
# -------------------------------
OBSERVER_LOCATION = 'Kenosha, WI (~42.6 N)'


# -------------------------------
# file paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SEARCH_PATHS = [
    BASE_DIR,                       # current folder
    '/storage/emulated/0/Pv2',      # phone project folder
]


def resolve_path(*candidates):
    """
    Check different file spots and use the first one that exists.
    """
    for candidate in candidates:
        if os.path.isabs(candidate) and os.path.exists(candidate):
            return candidate

        for root in SEARCH_PATHS:
            path = os.path.join(root, candidate)
            if os.path.exists(path):
                return path

    # if nothing is found, return the first one
    return candidates[0]


BACKGROUND_PATH = resolve_path(
    'Space.png',
    '/storage/emulated/0/Pv2/Space.png'
)

CONSTELLATIONS_PATH = resolve_path(
    'constellations_v2.json',
    '/storage/emulated/0/Pv2/constellations_v2.json'
)

STARS_PATH = resolve_path(
    'stars_v2.json',
    '/storage/emulated/0/Pv2/stars_v2.json'
)

# optional star color data
BV_CSV_PATH = resolve_path(
    'result-1.csv',
    '/storage/emulated/0/Pv2/result-1.csv'
)