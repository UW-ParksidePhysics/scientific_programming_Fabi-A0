"""
game_state.py
This file keeps track of what is happening in the game.

It keeps track of:
- which constellation is picked
- which lines are finished
- dragging from star to star
- when the constellation is complete
"""

import math
import pygame
from config import (
    STAR_HIT_RADIUS, STAR_SNAP_RADIUS, STAR_SHINE_MS, SCROLL_VISIBLE,
)


class GameState:
    def __init__(self, data_mgr):
        self.data = data_mgr

        # list position and picked constellation
        self.scroll_offset = 0
        self.selected_constellation_name = None

        # drawing progress
        self.drawn_edges = set()       # finished lines
        self.drag_from_idx = None      # star where drag started
        self.last_visited_idx = None   # current star being followed
        self.drag_pos = None           # current mouse or finger spot
        self.completed = False

        # glow effect on stars
        self.star_shine_until = {}     # star index -> time glow ends

        # star info and message text
        self.selected_star = None
        self.status = 'Select a constellation from the list.'

    # -------------------------------
    # constellation list
    # -------------------------------
    @property
    def visible_names(self):
        # names currently showing in the list
        names = self.data.constellation_names()
        end = min(self.scroll_offset + SCROLL_VISIBLE, len(names))
        return names[self.scroll_offset:end]

    @property
    def can_scroll_up(self):
        return self.scroll_offset > 0

    @property
    def can_scroll_down(self):
        total = len(self.data.constellation_names())
        return self.scroll_offset + SCROLL_VISIBLE < total

    def scroll_up(self):
        if self.can_scroll_up:
            self.scroll_offset -= 1

    def scroll_down(self):
        if self.can_scroll_down:
            self.scroll_offset += 1

    def select_constellation(self, name):
        # set the picked constellation
        self.selected_constellation_name = name

        # clear old progress
        self.drawn_edges.clear()
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None
        self.star_shine_until.clear()
        self.completed = False
        self.selected_star = None

        c = self.data.get_constellation(name)
        n_edges = len(self.data.edges_for(c))

        self.status = (
            f'{name} — drag across the stars. '
            f'{n_edges} edges to find.'
        )

    # -------------------------------
    # current constellation helpers
    # -------------------------------
    @property
    def constellation(self):
        # get the current constellation data
        if self.selected_constellation_name:
            return self.data.get_constellation(self.selected_constellation_name)
        return None

    def star_positions(self, stage_rect):
        # get the star spots on screen
        c = self.constellation
        if not c:
            return []
        return self.data.star_screen_positions(c, stage_rect)

    def required_edges(self):
        # get the lines needed to finish this constellation
        c = self.constellation
        if not c:
            return set()
        return self.data.edges_for(c)

    def star_magnitude(self, idx):
        """
        Get the brightness value of a star.
        Lower number means brighter.
        """
        c = self.constellation
        if not c:
            return 3.0

        stars = c.get('display_stars', [])
        if not (0 <= idx < len(stars)):
            return 3.0

        star = self.data.get_star(stars[idx]['name'])
        if star is None:
            return 3.0

        try:
            return float(star.get('magnitude', 3.0))
        except (TypeError, ValueError):
            return 3.0

    # -------------------------------
    # clicking near stars
    # -------------------------------
    def hit_star(self, pos, stage_rect, radius=None):
        """Return the nearest star in range, or None."""
        r = radius if radius is not None else STAR_HIT_RADIUS
        pts = self.star_positions(stage_rect)

        best_i, best_d = None, r

        for i, (sx, sy) in enumerate(pts):
            d = math.hypot(pos[0] - sx, pos[1] - sy)
            if d <= best_d:
                best_i, best_d = i, d

        return best_i

    # -------------------------------
    # star glow effect
    # -------------------------------
    def _shine_star(self, idx):
        # turn on glow for a star
        self.star_shine_until[idx] = pygame.time.get_ticks() + STAR_SHINE_MS

    def shine_level(self, idx):
        """Return how much glow time is left from 0.0 to 1.0."""
        until = self.star_shine_until.get(idx)
        if until is None:
            return 0.0

        now = pygame.time.get_ticks()
        remaining = until - now

        if remaining <= 0:
            return 0.0

        return max(0.0, min(1.0, remaining / STAR_SHINE_MS))

    def has_active_shines(self):
        # check if any stars are still glowing
        if not self.star_shine_until:
            return False

        now = pygame.time.get_ticks()

        # remove stars whose glow ended
        expired = [k for k, v in self.star_shine_until.items() if v <= now]
        for k in expired:
            del self.star_shine_until[k]

        return bool(self.star_shine_until)

    # -------------------------------
    # dragging
    # -------------------------------
    def begin_drag(self, star_idx):
        # start dragging from a star
        self.drag_from_idx = star_idx
        self.last_visited_idx = star_idx
        self.drag_pos = None
        self._shine_star(star_idx)

    def update_drag(self, pos, stage_rect=None):
        """
        Update the drag and add a line if the player reaches
        the next correct star.

        Return True if a new line was added.
        """
        if self.drag_from_idx is None:
            return False

        self.drag_pos = pos

        if stage_rect is None or self.last_visited_idx is None:
            return False

        pts = self.star_positions(stage_rect)

        # find the nearest star that is not the current one
        best_i, best_d = None, STAR_SNAP_RADIUS
        for i, (sx, sy) in enumerate(pts):
            if i == self.last_visited_idx:
                continue

            d = math.hypot(pos[0] - sx, pos[1] - sy)
            if d <= best_d:
                best_i, best_d = i, d

        if best_i is None:
            return False

        a, b = self.last_visited_idx, best_i
        edge = (min(a, b), max(a, b))
        required = self.required_edges()

        # only add the line if it is needed and not done yet
        if edge in required and edge not in self.drawn_edges:
            self.drawn_edges.add(edge)
            self._shine_star(best_i)
            self.last_visited_idx = best_i

            remaining = len(required) - len(self.drawn_edges)

            if remaining == 0:
                self.completed = True
                self.status = (
                    f'{self.selected_constellation_name} complete! '
                    f'Tap a star for details.'
                )
            else:
                self.status = (
                    f'Nice — {remaining} '
                    f'{"edge" if remaining == 1 else "edges"} left.'
                )

            return True

        return False

    def end_drag(self, star_idx=None):
        """Stop dragging."""
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None

    def cancel_drag(self):
        # cancel dragging
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None

    # -------------------------------
    # star info
    # -------------------------------
    def tap_star_info(self, star_idx):
        # show info for the tapped star
        c = self.constellation
        if not c:
            return

        stars = c.get('display_stars', [])

        if 0 <= star_idx < len(stars):
            name = stars[star_idx]['name']
            self.selected_star = self.data.get_star(name)

            if self.selected_star:
                self.status = f'Viewing {name}'
                self._shine_star(star_idx)

    # -------------------------------
    # clear and reset
    # -------------------------------
    def clear(self):
        # clear current drawing progress
        self.drawn_edges.clear()
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None
        self.star_shine_until.clear()
        self.completed = False
        self.selected_star = None

        if self.selected_constellation_name:
            c = self.constellation
            n_edges = len(self.data.edges_for(c))
            self.status = (
                f'{self.selected_constellation_name} — '
                f'{n_edges} edges to find.'
            )
        else:
            self.status = 'Select a constellation from the list.'

    def full_reset(self):
        # reset everything back to the start
        self.selected_constellation_name = None
        self.drawn_edges.clear()
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None
        self.star_shine_until.clear()
        self.completed = False
        self.selected_star = None
        self.status = 'Select a constellation from the list.'