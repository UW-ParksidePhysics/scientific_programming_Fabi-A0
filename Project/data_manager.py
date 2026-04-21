"""
data_manager.py
Loads JSON data and gives helper functions to access stars and constellations.
"""

import json


class DataManager:
    def __init__(self, constellations_path, stars_path):
        # store data
        self.constellations = []
        self.stars = []

        # quick lookup for stars by name
        self.stars_by_name = {}

        # load everything when class is created
        self._load(constellations_path, stars_path)


    # -------------------------------
    # loading data
    # -------------------------------
    def _load(self, cp, sp):
        # load constellation data
        with open(cp, 'r', encoding='utf-8') as f:
            self.constellations = json.load(f)

        # load star data
        with open(sp, 'r', encoding='utf-8') as f:
            self.stars = json.load(f)

        # make a dictionary so we can grab stars fast by name
        self.stars_by_name = {s['name']: s for s in self.stars}

        # precompute edges so we don’t keep recalculating them later
        for c in self.constellations:
            raw = c.get('edges', [])
            edge_set = set()

            for a, b in raw:
                # keep order consistent (small → big)
                edge_set.add((min(a, b), max(a, b)))

            c['_edge_set'] = edge_set


    # -------------------------------
    # helper / query functions
    # -------------------------------
    def get_constellation(self, name):
        # find constellation by name
        for c in self.constellations:
            if c['name'] == name:
                return c
        return None


    def get_star(self, name):
        # quick lookup instead of looping
        return self.stars_by_name.get(name)


    def constellation_names(self):
        # return list of all names
        return [c['name'] for c in self.constellations]


    def edges_for(self, constellation):
        """returns edges like (minIndex, maxIndex)"""
        return constellation.get('_edge_set', set())


    def star_screen_positions(self, constellation, stage_rect):
        """
        convert 0–1 positions into actual screen coords
        """
        positions = []

        for item in constellation.get('display_stars', []):
            nx, ny = item['pos']

            # scale based on screen area
            x = stage_rect.x + int(nx * stage_rect.width)
            y = stage_rect.y + int(ny * stage_rect.height)

            positions.append((x, y))

        return positions