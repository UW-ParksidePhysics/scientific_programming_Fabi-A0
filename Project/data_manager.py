"""
data_manager.py
This file loads the data for the program.

It helps with:
- loading stars and constellations
- finding stars by name
- getting line data
- turning star positions into screen positions
- getting star colors
"""

import csv
import json
import os

from config import (
    BV_CSV_PATH,
    color_from_bv,
    DESCRIPTION_COLOR_KEYWORDS,
)


class DataManager:
    def __init__(self, constellations_path, stars_path):
        # save main data
        self.constellations = []
        self.stars = []

        # quick way to find stars by name
        self.stars_by_name = {}

        # HIP number -> B-V color value
        self._bv_by_hip = {}

        # save star colors so we do not keep checking again
        self._color_cache = {}

        # load everything when this class starts
        self._load(constellations_path, stars_path)
        self._load_bv_index(BV_CSV_PATH)

    # -------------------------------
    # loading data
    # -------------------------------
    def _load(self, cp, sp):
        # load constellation file
        with open(cp, 'r', encoding='utf-8') as f:
            self.constellations = json.load(f)

        # load star file
        with open(sp, 'r', encoding='utf-8') as f:
            self.stars = json.load(f)

        # make a quick name lookup for stars
        self.stars_by_name = {s['name']: s for s in self.stars}

        # save the needed lines in a clean format
        for c in self.constellations:
            raw = c.get('edges', [])
            edge_set = set()

            for a, b in raw:
                # keep the smaller number first
                edge_set.add((min(a, b), max(a, b)))

            c['_edge_set'] = edge_set

    def _load_bv_index(self, csv_path):
        """
        Load HIP and B-V values from the CSV file.
        If the file is missing or broken, the program just skips it.
        """
        if not csv_path or not os.path.exists(csv_path):
            return

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    hip_raw = row.get('HIP', '').strip()
                    bv_raw = row.get('B-V', '').strip()

                    if not hip_raw or not bv_raw:
                        continue

                    try:
                        self._bv_by_hip[int(hip_raw)] = float(bv_raw)
                    except ValueError:
                        # skip bad number rows
                        continue
        except (OSError, csv.Error):
            # skip the file if it cannot be read
            self._bv_by_hip = {}

    # -------------------------------
    # helper functions
    # -------------------------------
    def get_constellation(self, name):
        # find a constellation by name
        for c in self.constellations:
            if c['name'] == name:
                return c
        return None

    def get_star(self, name):
        # find a star by name fast
        return self.stars_by_name.get(name)

    def constellation_names(self):
        # return all constellation names
        return [c['name'] for c in self.constellations]

    def edges_for(self, constellation):
        # return the needed lines for a constellation
        return constellation.get('_edge_set', set())

    def star_screen_positions(self, constellation, stage_rect):
        """
        Turn 0 to 1 star positions into real screen positions.
        """
        positions = []

        for item in constellation.get('display_stars', []):
            nx, ny = item['pos']

            # stretch the points to fit the draw area
            x = stage_rect.x + int(nx * stage_rect.width)
            y = stage_rect.y + int(ny * stage_rect.height)

            positions.append((x, y))

        return positions

    # -------------------------------
    # star color
    # -------------------------------
    def get_star_color(self, name):
        """
        Get the color for a star.

        Order:
        1. use B-V value from CSV
        2. look for color words in the description
        3. use default warm white
        """
        if name in self._color_cache:
            return self._color_cache[name]

        star = self.stars_by_name.get(name)
        color = None

        if star is not None:
            # 1. try B-V value from HIP data
            hip = star.get('hip')
            if hip is not None and hip in self._bv_by_hip:
                color = color_from_bv(self._bv_by_hip[hip])

            # 2. try color words in description
            if color is None:
                desc = (star.get('description') or '').lower()
                for keyword, kw_color in DESCRIPTION_COLOR_KEYWORDS:
                    if keyword in desc:
                        color = kw_color
                        break

        # 3. use default color
        if color is None:
            color = color_from_bv(None)

        self._color_cache[name] = color
        return color