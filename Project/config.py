"""
config.py
This file stores all the constants for the program,
like colors, timing, layout settings, and file paths.
"""

import os


# -------------------------------
# Timing / Display settings
# -------------------------------
FPS = 60                     # frames per second
STAR_HIT_RADIUS = 45         # how close you need to tap a star to select it
STAR_SNAP_RADIUS = 65        # while dragging, finger can snap to a nearby star
STAR_SHINE_MS = 450          # how long the star glow effect lasts after being touched
SCROLL_VISIBLE = 5           # number of constellations visible in scroll list


# -------------------------------
# Colors
# -------------------------------
BG_COLOR = (6, 7, 18)                # dark background color
TEXT_COLOR = (245, 245, 255)         # main text color
MUTED_TEXT = (185, 190, 215)         # softer text color
PANEL_FILL = (14, 16, 34, 210)       # panel background with transparency
PANEL_BORDER = (110, 120, 175)       # border color for panels
ACCENT = (173, 196, 255)             # main accent color
ACCENT_SOFT = (115, 140, 235)        # softer accent color
STAR_COLOR = (255, 248, 235)         # color of the stars
STAR_GLOW = (210, 230, 255)          # glow around the stars
LINE_COLOR = (245, 245, 250)         # constellation line color
LINE_GLOW = (170, 190, 255)          # glow for constellation lines
SUCCESS = (200, 235, 255)            # color for success messages/highlights
ERROR = (255, 190, 190)              # color for error messages
HIGHLIGHT_BG = (40, 48, 90)          # background for highlighted item
SELECTED_BG = (55, 65, 120)          # background for selected item
EDGE_PENDING = (80, 100, 170, 120)   # unfinished edge/connection color
EDGE_DONE = (180, 210, 255)          # completed edge/connection color
DRAG_LINE_COLOR = (255, 255, 200, 180)  # temporary line shown while dragging


# -------------------------------
# Layout settings
# -------------------------------
DESIGN_RATIO = 16 / 10       # screen design ratio
CENTER_RATIO = 1.28          # used for centering things on screen


# -------------------------------
# File paths
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SEARCH_PATHS = [
    BASE_DIR,                       # current project folder
    '/storage/emulated/0/Pv2',      # phone storage project folder
]


def resolve_path(*candidates):
    """
    Checks multiple possible file locations and returns
    the first one that actually exists.
    """
    for candidate in candidates:
        if os.path.isabs(candidate) and os.path.exists(candidate):
            return candidate

        for root in SEARCH_PATHS:
            path = os.path.join(root, candidate)
            if os.path.exists(path):
                return path

    # if nothing is found, return the first option anyway
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