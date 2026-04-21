"""
game_state.py
Keeps track of selection, drawing edges, and when a constellation is finished.

How drawing works:
- Drag starts when the finger or mouse goes down near a star.
- `last_visited_idx` keeps track of the current star in the path.
- While dragging, if the finger gets close enough to another star
  and that edge is required and not already drawn, it snaps in.
- If the edge is not needed or already done, nothing happens,
  and the user can keep moving.
"""

import math
import pygame
from config import (
    STAR_HIT_RADIUS, STAR_SNAP_RADIUS, STAR_SHINE_MS, SCROLL_VISIBLE,
)


class GameState:
    def __init__(self, data_mgr):
        self.data = data_mgr

        # constellation list stuff
        self.scroll_offset = 0
        self.selected_constellation_name = None

        # drawing progress
        self.drawn_edges = set()       # stores completed edges as (minIdx, maxIdx)
        self.drag_from_idx = None      # first star where drag started
        self.last_visited_idx = None   # current star in the trail
        self.drag_pos = None           # current finger/mouse position
        self.completed = False

        # star shine effect
        self.star_shine_until = {}     # star index -> time when shine ends

        # info panel / status
        self.selected_star = None
        self.status = 'Select a constellation from the list.'

    # -------------------------------
    # constellation list
    # -------------------------------
    @property
    def visible_names(self):
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
        # set current constellation
        self.selected_constellation_name = name

        # reset progress
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
    # active constellation helpers
    # -------------------------------
    @property
    def constellation(self):
        if self.selected_constellation_name:
            return self.data.get_constellation(self.selected_constellation_name)
        return None

    def star_positions(self, stage_rect):
        c = self.constellation
        if not c:
            return []
        return self.data.star_screen_positions(c, stage_rect)

    def required_edges(self):
        c = self.constellation
        if not c:
            return set()
        return self.data.edges_for(c)

    # -------------------------------
    # hit detection
    # -------------------------------
    def hit_star(self, pos, stage_rect, radius=None):
        """Returns the closest star inside the radius, or None."""
        r = radius if radius is not None else STAR_HIT_RADIUS
        pts = self.star_positions(stage_rect)

        best_i, best_d = None, r

        for i, (sx, sy) in enumerate(pts):
            d = math.hypot(pos[0] - sx, pos[1] - sy)
            if d <= best_d:
                best_i, best_d = i, d

        return best_i

    # -------------------------------
    # shine / pulse effect
    # -------------------------------
    def _shine_star(self, idx):
        self.star_shine_until[idx] = pygame.time.get_ticks() + STAR_SHINE_MS

    def shine_level(self, idx):
        """Returns a value from 0.0 to 1.0 for how much shine is left."""
        until = self.star_shine_until.get(idx)
        if until is None:
            return 0.0

        now = pygame.time.get_ticks()
        remaining = until - now

        if remaining <= 0:
            return 0.0

        return max(0.0, min(1.0, remaining / STAR_SHINE_MS))

    def has_active_shines(self):
        if not self.star_shine_until:
            return False

        now = pygame.time.get_ticks()

        # remove expired shine effects
        expired = [k for k, v in self.star_shine_until.items() if v <= now]
        for k in expired:
            del self.star_shine_until[k]

        return bool(self.star_shine_until)

    # -------------------------------
    # dragging logic
    # -------------------------------
    def begin_drag(self, star_idx):
        self.drag_from_idx = star_idx
        self.last_visited_idx = star_idx
        self.drag_pos = None
        self._shine_star(star_idx)

    def update_drag(self, pos, stage_rect=None):
        """
        Updates drag position and adds an edge if the drag reaches
        a valid nearby star.

        Returns True if a new edge was added.
        """
        if self.drag_from_idx is None:
            return False

        self.drag_pos = pos

        if stage_rect is None or self.last_visited_idx is None:
            return False

        pts = self.star_positions(stage_rect)

        # find closest nearby star that is not the current one
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

        # only add the edge if it is needed and not already drawn
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
        """Ends the drag. Edge creation already happens in update_drag."""
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None

    def cancel_drag(self):
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None

    # -------------------------------
    # star info tap
    # -------------------------------
    def tap_star_info(self, star_idx):
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
    # clear / reset
    # -------------------------------
    def clear(self):
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
        self.selected_constellation_name = None
        self.drawn_edges.clear()
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None
        self.star_shine_until.clear()
        self.completed = False
        self.selected_star = None
        self.status = 'Select a constellation from the list.'