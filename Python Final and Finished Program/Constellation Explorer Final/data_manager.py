"""Data access layer for stars, constellations, and star colors."""

__author__ = "Fabian Anguiano"

import csv
import os

from config import (
    BV_CSV_PATH,
    color_from_bv,
    DESCRIPTION_COLOR_KEYWORDS,
)
from save_manager import SaveManager


class DataManager:
    """Load constellation and star data and serve it to the game.

    The manager wraps a :class:`SaveManager` so the same code paths
    work on both desktop and the browser build. It also maintains
    derived lookups (``stars_by_name``, the per-constellation
    ``_edge_set`` cache, and a star-color cache) that the rest of
    the game uses without re-reading files.
    """

    def __init__(self, constellations_path, stars_path, save_manager=None):
        """Load all data and build the derived lookups.

        Parameters:
            constellations_path: str
                Path to the constellations JSON file. Used only if
                ``save_manager`` is not provided.
            stars_path: str
                Path to the stars JSON file. Used only if
                ``save_manager`` is not provided.
            save_manager: SaveManager, optional
                Existing manager to reuse. When omitted a new one is
                created from the two paths above.
        """
        # build a save manager if one wasn't given
        if save_manager is None:
            save_manager = SaveManager(constellations_path, stars_path)

        self.save_manager = save_manager

        # primary data
        self.constellations = []
        self.stars = []

        # fast lookup of stars by name
        self.stars_by_name = {}

        # HIP number -> B-V color value
        self._bv_by_hip = {}

        # cache of resolved star colors so we do not recompute
        self._color_cache = {}

        # load everything on construction
        self._load_from_save_manager()
        self._load_bv_index(BV_CSV_PATH)

    # -------------------------------
    # loading data
    # -------------------------------
    def _load_from_save_manager(self):
        """Load constellations and stars through the save manager.

        Also rebuilds the ``stars_by_name`` lookup and the
        per-constellation ``_edge_set`` cache.
        """
        self.constellations = self.save_manager.load_constellations()
        self.stars = self.save_manager.load_stars()

        # quick name lookup for stars
        self.stars_by_name = {
            s['name']: s for s in self.stars if 'name' in s
        }

        # store edges in a fast lookup structure
        for c in self.constellations:
            self._rebuild_edge_set(c)

    def _rebuild_edge_set(self, constellation):
        """Refresh the ``_edge_set`` cache for one constellation.

        Parameters:
            constellation: dict
                A constellation record. The ``edges`` field is read
                and its content is stored under ``_edge_set`` as a
                set of ordered ``(low, high)`` index tuples.
        """
        raw = constellation.get('edges', []) or []
        edge_set = set()
        for pair in raw:
            try:
                a, b = pair[0], pair[1]
            except (IndexError, TypeError):
                continue
            edge_set.add((min(a, b), max(a, b)))
        constellation['_edge_set'] = edge_set

    def _load_bv_index(self, csv_path):
        """Load HIP-keyed B-V values from a CSV file if present.

        Parameters:
            csv_path: str
                Path to a CSV with at least ``HIP`` and ``B-V``
                columns. A missing or unreadable file is silently
                ignored so the game still runs without color data.
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
                        # skip rows whose numbers don't parse
                        continue
        except (OSError, csv.Error):
            # skip the file if it cannot be read
            self._bv_by_hip = {}

    # -------------------------------
    # refresh — call after the editor changes data
    # -------------------------------
    def refresh_caches(self):
        """Rebuild derived lookups after editor edits.

        Rebuilds ``stars_by_name`` and the per-constellation
        ``_edge_set`` cache, and clears the color cache. Does not
        re-read files from disk.
        """
        self.stars_by_name = {
            s['name']: s for s in self.stars if 'name' in s
        }
        self._color_cache.clear()

        for c in self.constellations:
            self._rebuild_edge_set(c)

    # -------------------------------
    # accessor helpers
    # -------------------------------
    def get_constellation(self, name):
        """Look up a constellation record by display name.

        Parameters:
            name: str
                The constellation name to search for.
        Returns:
            constellation: dict or None
                The record, or ``None`` when no match is found.
        """
        for c in self.constellations:
            if c['name'] == name:
                return c
        return None

    def get_star(self, name):
        """Look up a star record by display name.

        Parameters:
            name: str
                The star name to search for.
        Returns:
            star: dict or None
                The record, or ``None`` when no match is found.
        """
        return self.stars_by_name.get(name)

    def constellation_names(self):
        """Return the list of all known constellation names.

        Returns:
            names: list of str
                Names in their stored order.
        """
        return [c['name'] for c in self.constellations]

    def edges_for(self, constellation):
        """Return the cached set of required edges for a constellation.

        Parameters:
            constellation: dict
                A constellation record.
        Returns:
            edges: set of tuple
                Each element is an ordered ``(low, high)`` pair of
                ``display_stars`` indices.
        """
        return constellation.get('_edge_set', set())

    def star_screen_positions(self, constellation, stage_rect):
        """Map normalized star positions to pixel coordinates.

        Parameters:
            constellation: dict
                A constellation record whose ``display_stars`` carry
                normalized ``pos`` values in the ``[0, 1]`` range.
            stage_rect: pygame.Rect
                The on-screen draw area the positions should fill.
        Returns:
            positions: list of tuple
                One ``(x, y)`` pixel coordinate per display star, in
                the same order as ``display_stars``.
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
        """Resolve the rendering color for a named star.

        Resolution order:
            1. B-V index from the loaded CSV (if available).
            2. Color keywords found in the star's description.
            3. The default warm-white fallback.

        Parameters:
            name: str
                The star name to look up.
        Returns:
            color: tuple of int, shape (3,)
                The RGB color to render the star with.
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

            # 2. try color keywords in the description
            if color is None:
                desc = (star.get('description') or '').lower()
                for keyword, kw_color in DESCRIPTION_COLOR_KEYWORDS:
                    if keyword in desc:
                        color = kw_color
                        break

        # 3. use the default warm-white color
        if color is None:
            color = color_from_bv(None)

        self._color_cache[name] = color
        return color


if __name__ == '__main__':
    print('Input: a DataManager built from the project JSON files.')
    print('Expected: counts > 0 and a recognizable RGB tuple for "Vega".')

    from config import CONSTELLATIONS_PATH, STARS_PATH

    data = DataManager(CONSTELLATIONS_PATH, STARS_PATH)
    print(f'constellation count = {len(data.constellations)}')
    print(f'star count          = {len(data.stars)}')
    print(f'color for "Vega"    = {data.get_star_color("Vega")}')
