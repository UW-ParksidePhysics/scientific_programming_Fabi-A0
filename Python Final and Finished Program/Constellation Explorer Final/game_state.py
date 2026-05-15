"""Track the player's interaction state for Constellation Explorer."""

__author__ = "Fabian Anguiano"

import math

import pygame

from config import (
    STAR_HIT_RADIUS, STAR_SNAP_RADIUS, STAR_SHINE_MS, SCROLL_VISIBLE,
)


class GameState:
    """Track which constellation is active and how far it is drawn.

    The state object stores the selected constellation, finished
    edges, in-progress drag, completion status, per-star glow timers,
    and the message shown in the status bar.
    """

    def __init__(self, data_mgr):
        """Initialise an empty state bound to a :class:`DataManager`.

        Parameters:
            data_mgr: DataManager
                The data layer used to look up constellations, stars,
                and per-star colors.
        """
        self.data = data_mgr

        # list scrolling and current selection
        self.scroll_offset = 0
        self.selected_constellation_name = None

        # drawing progress
        self.drawn_edges = set()       # completed edges
        self.drag_from_idx = None      # star where the drag started
        self.last_visited_idx = None   # most recently snapped star
        self.drag_pos = None           # current mouse or finger spot
        self.completed = False

        # per-star glow timers (star index -> time the glow ends)
        self.star_shine_until = {}

        # selected star and status bar message
        self.selected_star = None
        self.status = 'Select a constellation from the list.'

    # -------------------------------
    # constellation list
    # -------------------------------
    @property
    def visible_names(self):
        """list of str: Names currently shown in the side list."""
        names = self.data.constellation_names()
        end = min(self.scroll_offset + SCROLL_VISIBLE, len(names))
        return names[self.scroll_offset:end]

    @property
    def can_scroll_up(self):
        """bool: True when the list can scroll up by one row."""
        return self.scroll_offset > 0

    @property
    def can_scroll_down(self):
        """bool: True when the list can scroll down by one row."""
        total = len(self.data.constellation_names())
        return self.scroll_offset + SCROLL_VISIBLE < total

    def scroll_up(self):
        """Move the visible list window up by one entry, if possible."""
        if self.can_scroll_up:
            self.scroll_offset -= 1

    def scroll_down(self):
        """Move the visible list window down by one entry, if possible."""
        if self.can_scroll_down:
            self.scroll_offset += 1

    def select_constellation(self, name):
        """Select a constellation and reset all drawing progress.

        Parameters:
            name: str
                The constellation name to activate. Drawn edges,
                drag state, and shine timers are all cleared.
        """
        self.selected_constellation_name = name

        # clear any old progress
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
        """dict or None: The currently selected constellation record."""
        if self.selected_constellation_name:
            return self.data.get_constellation(
                self.selected_constellation_name
            )
        return None

    def star_positions(self, stage_rect):
        """Return pixel positions of the current constellation's stars.

        Parameters:
            stage_rect: pygame.Rect
                The on-screen draw area.
        Returns:
            positions: list of tuple
                One ``(x, y)`` per star; empty when no constellation
                is selected.
        """
        c = self.constellation
        if not c:
            return []
        return self.data.star_screen_positions(c, stage_rect)

    def required_edges(self):
        """Return the set of edges the player needs to draw.

        Returns:
            edges: set of tuple
                Each element is an ordered ``(low, high)`` index pair
                for the active constellation; an empty set when no
                constellation is selected.
        """
        c = self.constellation
        if not c:
            return set()
        return self.data.edges_for(c)

    def star_magnitude(self, idx):
        """Look up the magnitude (brightness) of one star.

        Parameters:
            idx: int
                Index of the star within ``display_stars`` of the
                active constellation.
        Returns:
            magnitude: float
                Apparent magnitude of the star. A fallback value of
                ``3.0`` is returned when no data is available.
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
    # hit testing
    # -------------------------------
    def hit_star(self, pos, stage_rect, radius=None):
        """Find the nearest star within range of a point.

        Parameters:
            pos: tuple of int
                The ``(x, y)`` screen position to test.
            stage_rect: pygame.Rect
                The active draw area.
            radius: float, optional
                Maximum distance to consider a hit; defaults to
                ``STAR_HIT_RADIUS``.
        Returns:
            index: int or None
                The index of the closest star in range, or ``None``
                when no star is within ``radius``.
        """
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
        """Start a fresh shine timer for a star.

        Parameters:
            idx: int
                Index of the star in the active constellation.
        """
        self.star_shine_until[idx] = (
            pygame.time.get_ticks() + STAR_SHINE_MS
        )

    def shine_level(self, idx):
        """Return how much shine time is left for a star.

        Parameters:
            idx: int
                Index of the star in the active constellation.
        Returns:
            level: float
                A value between ``0.0`` (no glow) and ``1.0``
                (just started). Returns ``0.0`` when the star has
                never been shone.
        """
        until = self.star_shine_until.get(idx)
        if until is None:
            return 0.0

        now = pygame.time.get_ticks()
        remaining = until - now

        if remaining <= 0:
            return 0.0

        return max(0.0, min(1.0, remaining / STAR_SHINE_MS))

    def has_active_shines(self):
        """Check if at least one star is still glowing.

        Returns:
            active: bool
                ``True`` while any timer is still in the future.
                Expired entries are pruned as a side effect.
        """
        if not self.star_shine_until:
            return False

        now = pygame.time.get_ticks()

        # drop stars whose glow ended
        expired = [
            k for k, v in self.star_shine_until.items() if v <= now
        ]
        for k in expired:
            del self.star_shine_until[k]

        return bool(self.star_shine_until)

    # -------------------------------
    # dragging
    # -------------------------------
    def begin_drag(self, star_idx):
        """Start a drag rooted at a star.

        Parameters:
            star_idx: int
                Index of the star where the drag begins.
        """
        self.drag_from_idx = star_idx
        self.last_visited_idx = star_idx
        self.drag_pos = None
        self._shine_star(star_idx)

    def update_drag(self, pos, stage_rect=None):
        """Update the current drag and record a newly completed edge.

        Parameters:
            pos: tuple of int
                Current pointer position in pixels.
            stage_rect: pygame.Rect, optional
                Active draw area; without this the drag position is
                updated but no edge can be added.
        Returns:
            edge_added: bool
                ``True`` when this update completed a new required
                edge; ``False`` otherwise.
        """
        if self.drag_from_idx is None:
            return False

        self.drag_pos = pos

        if stage_rect is None or self.last_visited_idx is None:
            return False

        pts = self.star_positions(stage_rect)

        # find the nearest star other than the current one
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

        # add the line only if it is required and not already drawn
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
                edge_word = 'edge' if remaining == 1 else 'edges'
                self.status = f'Nice — {remaining} {edge_word} left.'

            return True

        return False

    def end_drag(self, star_idx=None):
        """End the current drag, optionally committing a final edge.

        When ``star_idx`` is provided and forms a valid, undrawn
        required edge with ``last_visited_idx``, that edge is committed
        before the drag state is cleared. This catches the case where
        the pointer is released directly on a star without a separate
        motion event firing close enough to trigger the snap inside
        :meth:`update_drag`.

        Parameters:
            star_idx: int, optional
                Index of the star under the release point, or ``None``
                if the pointer was released on empty space.
        Returns:
            edge_added: bool
                ``True`` when this call completed a new required edge.
        """
        edge_added = False

        if (star_idx is not None
                and self.last_visited_idx is not None
                and star_idx != self.last_visited_idx):
            a, b = self.last_visited_idx, star_idx
            edge = (min(a, b), max(a, b))
            required = self.required_edges()

            if edge in required and edge not in self.drawn_edges:
                self.drawn_edges.add(edge)
                self._shine_star(star_idx)
                edge_added = True

                remaining = len(required) - len(self.drawn_edges)

                if remaining == 0:
                    self.completed = True
                    self.status = (
                        f'{self.selected_constellation_name} complete! '
                        f'Tap a star for details.'
                    )
                else:
                    edge_word = 'edge' if remaining == 1 else 'edges'
                    self.status = f'Nice — {remaining} {edge_word} left.'

        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None

        return edge_added

    def cancel_drag(self):
        """Abort the current drag without recording anything."""
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None

    # -------------------------------
    # star info
    # -------------------------------
    def tap_star_info(self, star_idx):
        """Show the detail card for a tapped star.

        Parameters:
            star_idx: int
                Index of the star in the active constellation.
        """
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
        """Clear progress on the current constellation but keep it selected."""
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
        """Reset to the initial state, deselecting any constellation."""
        self.selected_constellation_name = None
        self.drawn_edges.clear()
        self.drag_from_idx = None
        self.last_visited_idx = None
        self.drag_pos = None
        self.star_shine_until.clear()
        self.completed = False
        self.selected_star = None
        self.status = 'Select a constellation from the list.'


if __name__ == '__main__':
    print('Input: a GameState with no DataManager attached.')
    print('Expected: properties default sensibly without crashing.')

    class _StubData:
        """Minimal stand-in for DataManager used in this self-test."""

        def constellation_names(self):
            return []

        def get_constellation(self, name):
            return None

        def edges_for(self, constellation):
            return set()

        def star_screen_positions(self, c, rect):
            return []

        def get_star(self, name):
            return None

    state = GameState(_StubData())
    print(f'status            = {state.status!r}')
    print(f'visible_names     = {state.visible_names}')
    print(f'can_scroll_up     = {state.can_scroll_up}')
    print(f'has_active_shines = {state.has_active_shines()}')
