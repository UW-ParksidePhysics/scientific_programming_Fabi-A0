"""Visual editor for constellations_v2.json and stars_v2.json."""

__author__ = "Fabian Anguiano"

import pygame


# -------------------------------
# constants
# -------------------------------
FPS = 60
WINDOW_W = 1400
WINDOW_H = 850
MIN_W = 1000
MIN_H = 650

STAR_HIT_RADIUS = 14

# colors (matches the main game palette)
BG = (8, 10, 24)
PANEL_FILL = (18, 22, 44)
PANEL_BORDER = (90, 105, 160)
TEXT = (245, 245, 252)
MUTED = (180, 190, 220)
ACCENT = (200, 220, 255)
ACCENT_SOFT = (130, 155, 220)
SUCCESS = (180, 240, 200)
WARN = (255, 200, 130)
DANGER = (255, 150, 150)

STAR_COLOR = (255, 250, 240)
STAR_SELECTED = (255, 230, 130)
EDGE_COLOR = (255, 230, 120)

GRID_COLOR = (35, 42, 70)
CANVAS_BG = (12, 14, 32)
CANVAS_BORDER = (160, 180, 220)

FIELD_BG = (24, 30, 60)
FIELD_BG_ACTIVE = (38, 50, 100)
FIELD_BORDER = (90, 105, 160)
FIELD_BORDER_ACTIVE = (200, 220, 255)

DIVIDER = (60, 75, 120)

# editable fields on a constellation and on a single star
CONST_FIELDS = ('name', 'subtitle', 'months', 'description')
STAR_FIELDS = (
    'star_name', 'star_constellation', 'star_magnitude',
    'star_distance', 'star_spectral', 'star_description',
)
NUMERIC_STAR_FIELDS = {'star_magnitude', 'star_distance'}
STAR_FIELD_TO_KEY = {
    'star_name':          'name',
    'star_constellation': 'constellation',
    'star_magnitude':     'magnitude',
    'star_distance':      'distance_ly',
    'star_spectral':      'spectral_type',
    'star_description':   'description',
}


# -------------------------------
# small helpers
# -------------------------------
def _wrap_text(text, font, width):
    """Wrap a string into lines that fit a maximum pixel width.

    Parameters:
        text: str or None
            The string to wrap. ``None`` is treated as empty.
        font: pygame.font.Font
            Font used to measure word widths.
        width: int
            Maximum line width in pixels.
    Returns:
        lines: list of str
            One entry per visual line; always at least one entry.
    """
    words = (text or '').split()
    lines = []
    current = ''
    for w in words:
        test = current + (' ' if current else '') + w
        if font.size(test)[0] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = w
    if current:
        lines.append(current)
    return lines or ['']


def _fmt_num(v):
    """Format a number for display in a text field.

    Parameters:
        v: float, int, str, or None
            The value to format.
    Returns:
        text: str
            Empty for ``None``; the integer form for whole-number
            floats; rounded to four decimals otherwise.
    """
    if v is None:
        return ''
    if isinstance(v, float):
        if v == int(v):
            return str(int(v))
        return str(round(v, 4))
    return str(v)


def _make_fonts():
    """Create the small set of fonts the editor uses.

    Returns:
        fonts: dict of pygame.font.Font
            Keys are ``'xs'``, ``'sm'``, ``'md'``, ``'lg'``.
    """
    return {
        'xs': pygame.font.SysFont('arial', 13),
        'sm': pygame.font.SysFont('arial', 16),
        'md': pygame.font.SysFont('arial', 20),
        'lg': pygame.font.SysFont('arial', 26),
    }


# -------------------------------
# state
# -------------------------------
class EditorState:
    """Hold the editor's data and UI state.

    The state mutates the constellations and stars lists in place so
    the host game can see edits immediately after the editor exits.
    Saves are delegated to a :class:`SaveManager` so desktop and
    browser builds use the same code paths.
    """

    def __init__(self, constellations, stars, save_manager):
        """Create the editor state from existing in-memory lists.

        Parameters:
            constellations: list of dict
                The live constellations list (edited in place).
            stars: list of dict
                The live stars list (edited in place).
            save_manager: SaveManager
                The save layer used for Ctrl+S.
        """
        self.constellations = constellations
        self.stars = stars
        self.save_manager = save_manager

        self.stars_by_name = {
            s['name']: s for s in stars
            if isinstance(s, dict) and 'name' in s
        }

        self.current_index = 0 if constellations else -1

        self.selected_star_idx = None
        self.dragging = False
        self.drag_offset = (0, 0)

        self.constellations_dirty = False
        self.stars_dirty = False

        self.active_field = None
        self.cursor_blink = 0
        self._num_buffer = ''

        self.list_scroll = 0

        self.search_open = False
        self.search_text = ''
        self.search_results = []
        self.search_selected = 0
        self.search_scroll = 0

        mode_hint = save_manager.mode_label
        self.status = (
            f'Editor open ({mode_hint}). '
            f'Pick a constellation or press Ctrl+N for a new one.'
        )

    @property
    def current(self):
        """dict or None: The currently selected constellation record."""
        if 0 <= self.current_index < len(self.constellations):
            return self.constellations[self.current_index]
        return None

    @property
    def dirty(self):
        """bool: True when either list has unsaved changes."""
        return self.constellations_dirty or self.stars_dirty

    def mark_const_dirty(self):
        """Mark the constellations list as having unsaved changes."""
        self.constellations_dirty = True

    def mark_star_dirty(self):
        """Mark the stars list as having unsaved changes."""
        self.stars_dirty = True

    # -------------------------------
    # selection helpers
    # -------------------------------
    def get_selected_star_record(self):
        """Look up the full star record for the selected display star.

        Returns:
            star: dict or None
                The star record, or ``None`` when nothing is
                selected or the name does not appear in
                ``stars_by_name``.
        """
        c = self.current
        if c is None or self.selected_star_idx is None:
            return None
        ds = c.get('display_stars', [])
        if not (0 <= self.selected_star_idx < len(ds)):
            return None
        name = ds[self.selected_star_idx].get('name')
        return self.stars_by_name.get(name)

    def select_constellation(self, idx):
        """Make a constellation the active one.

        Parameters:
            idx: int
                Index into ``self.constellations``. Out-of-range
                values are silently ignored.
        """
        self._commit_num_buffer()
        if 0 <= idx < len(self.constellations):
            self.current_index = idx
            self.selected_star_idx = None
            self.active_field = None
            self.search_open = False
            name = self.constellations[idx]['name']
            self.status = f'Editing: {name}'

    def new_constellation(self):
        """Append a new empty constellation and select it for editing."""
        self._commit_num_buffer()
        new_c = {
            'name': 'New Constellation',
            'subtitle': '',
            'best_months': '',
            'description': '',
            'display_stars': [],
            'edges': [],
        }
        self.constellations.append(new_c)
        self.current_index = len(self.constellations) - 1
        self.selected_star_idx = None
        self.active_field = 'name'
        self.mark_const_dirty()
        self.status = (
            'New constellation. Edit the name on the right, '
            'then add stars.'
        )

    # -------------------------------
    # scrolling
    # -------------------------------
    @property
    def can_scroll_up(self):
        """bool: True when the constellation list can scroll up."""
        return self.list_scroll > 0

    @property
    def can_scroll_down(self):
        """bool: True when the constellation list can scroll down."""
        visible = getattr(self, '_visible_count', 1)
        return self.list_scroll + visible < len(self.constellations)

    def scroll_up(self):
        """Scroll the constellation list up by one row, if possible."""
        if self.can_scroll_up:
            self.list_scroll -= 1

    def scroll_down(self):
        """Scroll the constellation list down by one row, if possible."""
        if self.can_scroll_down:
            self.list_scroll += 1

    # -------------------------------
    # star operations
    # -------------------------------
    def add_star_to_current(self, star_record, pos=(0.5, 0.5)):
        """Attach an existing star record to the current constellation.

        Parameters:
            star_record: dict
                A record from the global stars list.
            pos: tuple of float, optional
                Initial normalized position in ``[0, 1]``. Defaults
                to the center of the canvas.
        """
        c = self.current
        if c is None:
            return
        existing_names = {s['name'] for s in c['display_stars']}
        if star_record['name'] in existing_names:
            self.status = (
                f'"{star_record["name"]}" is already in '
                f'this constellation.'
            )
            return
        c['display_stars'].append({
            'name': star_record['name'],
            'hip': star_record.get('hip'),
            'pos': [round(pos[0], 4), round(pos[1], 4)],
        })
        self.mark_const_dirty()
        self.status = f'Added "{star_record["name"]}".'

    def remove_star_from_current(self, idx):
        """Remove a star from the current constellation and fix edges.

        Parameters:
            idx: int
                Index of the star within ``display_stars``.
        """
        c = self.current
        if c is None or not (0 <= idx < len(c['display_stars'])):
            return
        name = c['display_stars'][idx]['name']
        c['display_stars'].pop(idx)
        new_edges = []
        for a, b in c['edges']:
            if a == idx or b == idx:
                continue
            new_a = a - 1 if a > idx else a
            new_b = b - 1 if b > idx else b
            new_edges.append([min(new_a, new_b), max(new_a, new_b)])
        c['edges'] = new_edges
        if self.selected_star_idx == idx:
            self.selected_star_idx = None
            self.active_field = None
        elif (self.selected_star_idx is not None
                and self.selected_star_idx > idx):
            self.selected_star_idx -= 1
        self.mark_const_dirty()
        self.status = f'Removed "{name}".'

    def toggle_edge(self, a, b):
        """Toggle the edge between two stars in the current constellation.

        Parameters:
            a: int
                Index of the first star.
            b: int
                Index of the second star.
        """
        c = self.current
        if c is None or a == b:
            return
        edge = [min(a, b), max(a, b)]
        edges_set = {tuple(e) for e in c['edges']}
        if tuple(edge) in edges_set:
            c['edges'] = [
                list(e) for e in edges_set - {tuple(edge)}
            ]
            self.status = 'Removed edge.'
        else:
            c['edges'].append(edge)
            self.status = 'Added edge.'
        self.mark_const_dirty()

    # -------------------------------
    # search modal
    # -------------------------------
    def update_search(self):
        """Refresh the search-result list from the current query."""
        q = self.search_text.strip().lower()
        if not q:
            self.search_results = sorted(
                self.stars, key=lambda s: s.get('name', ''),
            )[:50]
        else:
            matches = [
                s for s in self.stars
                if q in s.get('name', '').lower()
            ]
            self.search_results = matches[:200]
        self.search_selected = 0
        self.search_scroll = 0

    # -------------------------------
    # numeric edit buffer
    # -------------------------------
    def set_active_field(self, field):
        """Make a field the keyboard-focused one and prime its buffer.

        Parameters:
            field: str or None
                The field key, or ``None`` to clear the focus. For
                numeric star fields the current value is copied into
                the edit buffer so backspace works on what is shown.
        """
        self._commit_num_buffer()
        self.active_field = field
        if field in NUMERIC_STAR_FIELDS:
            star = self.get_selected_star_record()
            if star is not None:
                key = STAR_FIELD_TO_KEY[field]
                self._num_buffer = _fmt_num(star.get(key))
            else:
                self._num_buffer = ''

    def _commit_num_buffer(self):
        """Parse the numeric buffer and write it back to the star record."""
        if self.active_field not in NUMERIC_STAR_FIELDS:
            return
        star = self.get_selected_star_record()
        if star is None:
            return
        key = STAR_FIELD_TO_KEY[self.active_field]
        text = self._num_buffer.strip()
        if not text:
            new_val = None
        else:
            try:
                new_val = float(text)
            except ValueError:
                self.status = (
                    f'Could not parse "{text}" as a number — '
                    f'kept the old value.'
                )
                return
        if star.get(key) != new_val:
            star[key] = new_val
            self.mark_star_dirty()

    # -------------------------------
    # save
    # -------------------------------
    def save(self):
        """Commit pending edits and save dirty lists via the SaveManager."""
        self._commit_num_buffer()
        msgs = []
        if self.constellations_dirty:
            msgs.append(
                self.save_manager.save_constellations(self.constellations)
            )
            self.constellations_dirty = False
        if self.stars_dirty:
            msgs.append(self.save_manager.save_stars(self.stars))
            self.stars_dirty = False
        if not msgs:
            self.status = 'Nothing to save.'
        else:
            self.status = ' · '.join(msgs)


# -------------------------------
# layout
# -------------------------------
class Layout:
    """Pure-rectangle layout for the editor window.

    Far simpler than the game's main layout: the editor always uses
    a wide three-column arrangement with a status bar at the bottom.
    """

    def __init__(self, w, h):
        """Build the layout for an initial window size.

        Parameters:
            w: int
                Window width in pixels.
            h: int
                Window height in pixels.
        """
        self.update(w, h)

    def update(self, w, h):
        """Recompute every rectangle for a new window size.

        Parameters:
            w: int
                Window width in pixels.
            h: int
                Window height in pixels.
        """
        self.w = max(MIN_W, w)
        self.h = max(MIN_H, h)
        pad = 14
        gap = 12
        bottom_h = 36
        left_w = max(220, int(self.w * 0.18))
        right_w = max(300, int(self.w * 0.26))
        top_h = self.h - bottom_h - pad * 2 - gap
        self.left_panel = pygame.Rect(pad, pad, left_w, top_h)
        self.right_panel = pygame.Rect(
            self.w - right_w - pad, pad, right_w, top_h,
        )
        center_x = self.left_panel.right + gap
        center_w = self.right_panel.left - gap - center_x
        self.canvas_outer = pygame.Rect(center_x, pad, center_w, top_h)
        margin = 26
        self.canvas = self.canvas_outer.inflate(-margin * 2, -margin * 2)
        self.status_bar = pygame.Rect(
            pad, self.h - bottom_h - pad,
            self.w - pad * 2, bottom_h,
        )


# -------------------------------
# coordinate conversion
# -------------------------------
def norm_to_screen(canvas, pos):
    """Convert a normalized position to a pixel position.

    Parameters:
        canvas: pygame.Rect
            The drawing area on screen.
        pos: tuple of float
            Normalized ``(x, y)`` in ``[0, 1]``.
    Returns:
        position: tuple of int
            ``(x, y)`` pixel coordinates inside ``canvas``.
    """
    return (
        canvas.x + int(pos[0] * canvas.width),
        canvas.y + int(pos[1] * canvas.height),
    )


def screen_to_norm(canvas, pos):
    """Convert a pixel position to a normalized position.

    Parameters:
        canvas: pygame.Rect
            The drawing area on screen.
        pos: tuple of int
            ``(x, y)`` pixel coordinates.
    Returns:
        position: tuple of float
            Normalized ``(x, y)`` clamped to ``[0.02, 0.98]`` so
            stars never sit flush with the canvas edge.
    """
    nx = (pos[0] - canvas.x) / max(canvas.width, 1)
    ny = (pos[1] - canvas.y) / max(canvas.height, 1)
    return (
        max(0.02, min(0.98, nx)),
        max(0.02, min(0.98, ny)),
    )


def hit_test_star(canvas, display_stars, screen_pos):
    """Return the index of the star nearest a pointer, or None.

    Parameters:
        canvas: pygame.Rect
            The drawing area on screen.
        display_stars: list of dict
            The constellation's display-star list. Each entry must
            have a normalized ``pos`` key.
        screen_pos: tuple of int
            ``(x, y)`` pointer position in pixels.
    Returns:
        index: int or None
            Index of the closest star within ``STAR_HIT_RADIUS``
            pixels, or ``None`` when none are in range.
    """
    best_i, best_d = None, STAR_HIT_RADIUS
    for i, s in enumerate(display_stars):
        sx, sy = norm_to_screen(canvas, s['pos'])
        dx = sx - screen_pos[0]
        dy = sy - screen_pos[1]
        d = (dx * dx + dy * dy) ** 0.5
        if d <= best_d:
            best_i, best_d = i, d
    return best_i


# -------------------------------
# drawing primitives
# -------------------------------
def _draw_panel(screen, rect):
    """Draw the standard rounded panel background.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        rect: pygame.Rect
            Panel rectangle.
    """
    pygame.draw.rect(screen, PANEL_FILL, rect, border_radius=12)
    pygame.draw.rect(screen, PANEL_BORDER, rect, 1, border_radius=12)


def _draw_text(screen, text, font, color, x, y):
    """Draw a single-line string at a given position.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        text: str
            The string to draw.
        font: pygame.font.Font
            Font used to render the text.
        color: tuple of int
            RGB color of the text.
        x: int
            Left-edge pixel coordinate.
        y: int
            Top-edge pixel coordinate.
    Returns:
        rect: pygame.Rect
            The blitted text rectangle.
    """
    surf = font.render(text, True, color)
    screen.blit(surf, (x, y))
    return surf.get_rect(topleft=(x, y))


def _draw_button(screen, rect, label, font, hover=False, enabled=True):
    """Draw a labelled button.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        rect: pygame.Rect
            Button rectangle.
        label: str
            Visible label text.
        font: pygame.font.Font
            Font for the label.
        hover: bool, optional
            Renders with a brighter fill when ``True``.
        enabled: bool, optional
            Renders dimmed and non-interactive looking when ``False``.
    """
    if not enabled:
        fill = (20, 24, 48)
        border = (60, 70, 100)
        color = (110, 120, 150)
    else:
        fill = (50, 65, 130) if hover else (32, 40, 80)
        border = PANEL_BORDER
        color = TEXT
    pygame.draw.rect(screen, fill, rect, border_radius=8)
    pygame.draw.rect(screen, border, rect, 1, border_radius=8)
    surf = font.render(label, True, color)
    screen.blit(surf, surf.get_rect(center=rect.center))


def _draw_arrow_button(screen, rect, direction, enabled, hover=False):
    """Draw an up or down arrow button.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        rect: pygame.Rect
            Button rectangle.
        direction: str
            ``'up'`` or ``'down'``.
        enabled: bool
            Renders dimmed when ``False``.
        hover: bool, optional
            Renders brighter when ``True`` and ``enabled``.
    """
    if enabled and hover:
        fill = (38, 50, 96)
    elif enabled:
        fill = (28, 34, 64)
    else:
        fill = (18, 22, 40)
    border = PANEL_BORDER if enabled else (60, 70, 100)
    color = TEXT if enabled else (100, 110, 140)
    pygame.draw.rect(screen, fill, rect, border_radius=6)
    pygame.draw.rect(screen, border, rect, 1, border_radius=6)
    cx, cy = rect.centerx, rect.centery
    sz = min(rect.width, rect.height) // 4
    if direction == 'up':
        pts = [(cx, cy - sz), (cx - sz, cy + sz), (cx + sz, cy + sz)]
    else:
        pts = [(cx, cy + sz), (cx - sz, cy - sz), (cx + sz, cy - sz)]
    pygame.draw.polygon(screen, color, pts)


def _draw_grid(screen, canvas):
    """Draw a faint 10x10 reference grid inside the canvas.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        canvas: pygame.Rect
            The canvas rectangle.
    """
    for i in range(1, 10):
        x = canvas.x + int(canvas.width * i / 10)
        y = canvas.y + int(canvas.height * i / 10)
        pygame.draw.line(
            screen, GRID_COLOR,
            (x, canvas.y), (x, canvas.bottom), 1,
        )
        pygame.draw.line(
            screen, GRID_COLOR,
            (canvas.x, y), (canvas.right, y), 1,
        )


def _draw_field(screen, rect, label, value, font, label_font,
                active, multiline=False, placeholder=''):
    """Draw a labelled editable text field.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        rect: pygame.Rect
            Bounding rectangle of the labelled field; the inner
            input box sits below the label.
        label: str
            Visible label text.
        value: str
            Current value of the field; placeholder is shown if empty.
        font: pygame.font.Font
            Font used for the value.
        label_font: pygame.font.Font
            Font used for the label.
        active: bool
            Renders with the active highlight when ``True``.
        multiline: bool, optional
            Wraps long text inside the box when ``True``.
        placeholder: str, optional
            Hint shown when ``value`` is empty.
    Returns:
        field_rect: pygame.Rect
            The clickable input rectangle.
    """
    lbl_surf = label_font.render(label, True, MUTED)
    screen.blit(lbl_surf, (rect.x, rect.y))
    field_y = rect.y + lbl_surf.get_height() + 2
    field_rect = pygame.Rect(
        rect.x, field_y, rect.width,
        rect.height - lbl_surf.get_height() - 2,
    )
    bg = FIELD_BG_ACTIVE if active else FIELD_BG
    border = FIELD_BORDER_ACTIVE if active else FIELD_BORDER
    pygame.draw.rect(screen, bg, field_rect, border_radius=6)
    pygame.draw.rect(screen, border, field_rect, 1, border_radius=6)
    text = value
    color = TEXT
    if not text:
        text = placeholder
        color = MUTED
    inner_x = field_rect.x + 8
    inner_y = field_rect.y + 6
    if multiline:
        lines = _wrap_text(text, font, field_rect.width - 16)
        lh = font.get_linesize()
        max_lines = max(1, (field_rect.height - 12) // lh)
        for i, line in enumerate(lines[:max_lines]):
            ls = font.render(line, True, color)
            screen.blit(ls, (inner_x, inner_y + i * lh))
    else:
        ts = font.render(text, True, color)
        ty = field_rect.y + (field_rect.height - ts.get_height()) // 2
        screen.blit(ts, (inner_x, ty))
    return field_rect


def draw_canvas(screen, layout, state, fonts, mouse_pos):
    """Render the central star canvas (grid, stars, edges, hover lines).

    Parameters:
        screen: pygame.Surface — the target display surface.
        layout: Layout — current panel geometry.
        state: EditorState — editor state with selected constellation.
        fonts: dict — font registry from `_make_fonts`.
        mouse_pos: tuple of (int, int) — current mouse coordinates.

    Returns:
        None: draws directly to `screen`.
    """
    co = layout.canvas_outer
    cv = layout.canvas
    pygame.draw.rect(screen, CANVAS_BG, co, border_radius=14)
    pygame.draw.rect(screen, PANEL_BORDER, co, 1, border_radius=14)
    pygame.draw.rect(screen, (10, 12, 28), cv, border_radius=10)
    pygame.draw.rect(screen, CANVAS_BORDER, cv, 1, border_radius=10)
    _draw_grid(screen, cv)
    c = state.current
    if c is None:
        msg = 'No constellation selected. Press Ctrl+N to make a new one.'
        surf = fonts['md'].render(msg, True, MUTED)
        screen.blit(surf, surf.get_rect(center=cv.center))
        return
    stars = c['display_stars']
    for a, b in c['edges']:
        if a < len(stars) and b < len(stars):
            p1 = norm_to_screen(cv, stars[a]['pos'])
            p2 = norm_to_screen(cv, stars[b]['pos'])
            pygame.draw.line(screen, EDGE_COLOR, p1, p2, 2)
            pygame.draw.aaline(screen, EDGE_COLOR, p1, p2)
    if (state.selected_star_idx is not None
            and not state.dragging
            and cv.collidepoint(mouse_pos)
            and state.selected_star_idx < len(stars)):
        p1 = norm_to_screen(cv, stars[state.selected_star_idx]['pos'])
        pygame.draw.line(screen, ACCENT_SOFT, p1, mouse_pos, 1)
    for i, s in enumerate(stars):
        sx, sy = norm_to_screen(cv, s['pos'])
        is_sel = (i == state.selected_star_idx)
        glow_color = STAR_SELECTED if is_sel else STAR_COLOR
        for r, alpha in [(11, 60), (8, 100)]:
            glow_surf = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*glow_color, alpha),
                               (r + 2, r + 2), r)
            screen.blit(glow_surf, (sx - r - 2, sy - r - 2))
        pygame.draw.circle(screen, glow_color, (sx, sy), 5)
        if is_sel:
            pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 2)
        label = fonts['xs'].render(s['name'], True, MUTED)
        screen.blit(label, (sx - label.get_width() // 2, sy + 9))
    if cv.collidepoint(mouse_pos):
        nx, ny = screen_to_norm(cv, mouse_pos)
        coord_text = f'pos: [{nx:.3f}, {ny:.3f}]'
        surf = fonts['xs'].render(coord_text, True, MUTED)
        screen.blit(surf, (cv.x + 6, cv.bottom - surf.get_height() - 4))


def draw_left_panel(screen, layout, state, fonts, mouse_pos, embedded):
    """Render the left-side constellation list panel.

    Parameters:
        screen: pygame.Surface — target display surface.
        layout: Layout — current panel geometry.
        state: EditorState — editor state.
        fonts: dict — font registry.
        mouse_pos: tuple of (int, int) — current mouse coordinates.
        embedded: bool — True when running inside the main game (adds a
            "Back to Game" button).

    Returns:
        None: draws directly to `screen` and updates `state` with the
        clickable rects needed by the event handlers.
    """
    rect = layout.left_panel
    _draw_panel(screen, rect)
    pad_x = 14
    y = rect.y + 14
    _draw_text(screen, 'Constellations', fonts['md'], ACCENT,
               rect.x + pad_x, y)
    y += fonts['md'].get_linesize() + 6
    arrow_w = rect.width - pad_x * 2
    arrow_h = 26
    up_btn = pygame.Rect(rect.x + pad_x, y, arrow_w, arrow_h)
    state._scroll_up_btn = up_btn
    _draw_arrow_button(screen, up_btn, 'up', state.can_scroll_up,
                       hover=up_btn.collidepoint(mouse_pos))
    y = up_btn.bottom + 6
    n_action_btns = 3 if embedded else 2
    bottom_reserved = 8 + n_action_btns * 38 + arrow_h + 6
    list_top = y
    list_bottom = rect.bottom - bottom_reserved
    row_h = 30
    visible_count = max(1, (list_bottom - list_top) // row_h)
    state._list_rects = []
    state._visible_count = visible_count
    end = min(state.list_scroll + visible_count, len(state.constellations))
    for i in range(state.list_scroll, end):
        c = state.constellations[i]
        row_rect = pygame.Rect(rect.x + pad_x,
                               list_top + (i - state.list_scroll) * row_h,
                               rect.width - pad_x * 2, row_h - 4)
        state._list_rects.append((row_rect, i))
        is_sel = (i == state.current_index)
        is_hover = row_rect.collidepoint(mouse_pos)
        if is_sel:
            pygame.draw.rect(screen, (60, 80, 160), row_rect, border_radius=6)
        elif is_hover:
            pygame.draw.rect(screen, (35, 45, 90), row_rect, border_radius=6)
        name = c.get('name', '?')
        n = len(c.get('display_stars', []))
        label = f'{name} ({n})'
        color = TEXT if is_sel else MUTED
        surf = fonts['sm'].render(label, True, color)
        screen.blit(surf, (row_rect.x + 8,
                          row_rect.y + (row_h - 4 - surf.get_height()) // 2))
    down_y = list_bottom + 2
    down_btn = pygame.Rect(rect.x + pad_x, down_y, arrow_w, arrow_h)
    state._scroll_down_btn = down_btn
    _draw_arrow_button(screen, down_btn, 'down', state.can_scroll_down,
                       hover=down_btn.collidepoint(mouse_pos))
    total = len(state.constellations)
    if total > visible_count:
        info = (f'{state.list_scroll + 1}–'
                f'{min(state.list_scroll + visible_count, total)} of {total}')
        info_surf = fonts['xs'].render(info, True, MUTED)
        screen.blit(info_surf, (rect.x + pad_x, down_btn.bottom + 4))
    btn_w = rect.width - pad_x * 2
    btn_h = 32
    base_y = rect.bottom - 8 - btn_h
    save_btn = pygame.Rect(rect.x + pad_x, base_y, btn_w, btn_h)
    state._save_btn = save_btn
    label = 'Save *' if state.dirty else 'Save'
    _draw_button(screen, save_btn, label, fonts['sm'],
                 hover=save_btn.collidepoint(mouse_pos))
    new_btn = pygame.Rect(rect.x + pad_x, base_y - btn_h - 6, btn_w, btn_h)
    state._new_btn = new_btn
    _draw_button(screen, new_btn, '+ New Constellation', fonts['sm'],
                 hover=new_btn.collidepoint(mouse_pos))
    if embedded:
        back_btn = pygame.Rect(rect.x + pad_x, base_y - (btn_h + 6) * 2,
                               btn_w, btn_h)
        state._back_btn = back_btn
        _draw_button(screen, back_btn, '← Back to Game', fonts['sm'],
                     hover=back_btn.collidepoint(mouse_pos))


def draw_right_panel(screen, layout, state, fonts, mouse_pos):
    """Render the right-side details panel with constellation/star fields.

    Parameters:
        screen: pygame.Surface — target display surface.
        layout: Layout — current panel geometry.
        state: EditorState — editor state.
        fonts: dict — font registry.
        mouse_pos: tuple of (int, int) — current mouse coordinates.

    Returns:
        None: draws directly to `screen` and updates `state._field_rects`
        with the clickable rects for each editable field.
    """
    rect = layout.right_panel
    _draw_panel(screen, rect)
    pad_x = 14
    x = rect.x + pad_x
    y = rect.y + 14
    fw = rect.width - pad_x * 2
    state._field_rects = {}
    _draw_text(screen, 'Details', fonts['md'], ACCENT, x, y)
    y += fonts['md'].get_linesize() + 6
    c = state.current
    if c is None:
        _draw_text(screen, 'No constellation selected.', fonts['sm'],
                   MUTED, x, y)
        return
    star_selected = (state.selected_star_idx is not None
                     and state.get_selected_star_record() is not None)
    desc_h = 80 if star_selected else 130
    name_rect = pygame.Rect(x, y, fw, 48)
    state._field_rects['name'] = _draw_field(
        screen, name_rect, 'Name', c.get('name', ''),
        fonts['md'], fonts['xs'],
        active=(state.active_field == 'name'),
        placeholder='Constellation name')
    y = name_rect.bottom + 8
    sub_rect = pygame.Rect(x, y, fw, 42)
    state._field_rects['subtitle'] = _draw_field(
        screen, sub_rect, 'Subtitle', c.get('subtitle', ''),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'subtitle'),
        placeholder='e.g. "The Hunter"')
    y = sub_rect.bottom + 8
    mo_rect = pygame.Rect(x, y, fw, 42)
    state._field_rects['months'] = _draw_field(
        screen, mo_rect, 'Best months', c.get('best_months', ''),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'months'),
        placeholder='e.g. "December – March"')
    y = mo_rect.bottom + 8
    desc_rect = pygame.Rect(x, y, fw, desc_h)
    state._field_rects['description'] = _draw_field(
        screen, desc_rect, 'Description', c.get('description', ''),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'description'),
        multiline=True,
        placeholder='What is special about this constellation?')
    y = desc_rect.bottom + 10
    n_stars = len(c.get('display_stars', []))
    n_edges = len(c.get('edges', []))
    _draw_text(screen, f'{n_stars} stars · {n_edges} edges', fonts['xs'],
               ACCENT_SOFT, x, y)
    y += fonts['xs'].get_linesize() + 8
    add_btn = pygame.Rect(x, y, fw, 30)
    state._add_star_btn = add_btn
    _draw_button(screen, add_btn, '+ Add Star', fonts['sm'],
                 hover=add_btn.collidepoint(mouse_pos))
    y = add_btn.bottom + 12
    if not star_selected:
        return
    pygame.draw.line(screen, DIVIDER, (x, y), (x + fw, y), 1)
    y += 8
    star = state.get_selected_star_record()
    ds_entry = c['display_stars'][state.selected_star_idx]
    hip = ds_entry.get('hip')
    _draw_text(screen, 'Selected Star', fonts['md'], WARN, x, y)
    y += fonts['md'].get_linesize() + 2
    hip_text = f'HIP {hip}' if hip else 'no HIP'
    _draw_text(screen, hip_text, fonts['xs'], MUTED, x, y)
    y += fonts['xs'].get_linesize() + 6
    note = "Renaming syncs to this constellation's star list."
    _draw_text(screen, note, fonts['xs'], MUTED, x, y)
    y += fonts['xs'].get_linesize() + 6

    def _field_value(field_key):
        """Return the display string for a star field, honoring buffers."""
        if (field_key == state.active_field
                and field_key in NUMERIC_STAR_FIELDS):
            return state._num_buffer
        sk = STAR_FIELD_TO_KEY[field_key]
        if field_key in NUMERIC_STAR_FIELDS:
            return _fmt_num(star.get(sk))
        return star.get(sk, '') or ''

    sn_rect = pygame.Rect(x, y, fw, 42)
    state._field_rects['star_name'] = _draw_field(
        screen, sn_rect, 'Star name', _field_value('star_name'),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'star_name'),
        placeholder='Star display name')
    y = sn_rect.bottom + 6
    sc_rect = pygame.Rect(x, y, fw, 42)
    state._field_rects['star_constellation'] = _draw_field(
        screen, sc_rect, 'Constellation', _field_value('star_constellation'),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'star_constellation'),
        placeholder=c.get('name', ''))
    y = sc_rect.bottom + 6
    half_w = (fw - 8) // 2
    mag_rect = pygame.Rect(x, y, half_w, 42)
    state._field_rects['star_magnitude'] = _draw_field(
        screen, mag_rect, 'Magnitude', _field_value('star_magnitude'),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'star_magnitude'),
        placeholder='e.g. 1.5')
    dist_rect = pygame.Rect(x + half_w + 8, y, half_w, 42)
    state._field_rects['star_distance'] = _draw_field(
        screen, dist_rect, 'Distance (ly)', _field_value('star_distance'),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'star_distance'),
        placeholder='e.g. 25')
    y = mag_rect.bottom + 6
    sp_rect = pygame.Rect(x, y, fw, 42)
    state._field_rects['star_spectral'] = _draw_field(
        screen, sp_rect, 'Spectral type', _field_value('star_spectral'),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'star_spectral'),
        placeholder='e.g. A0V')
    y = sp_rect.bottom + 6
    remaining = rect.bottom - y - 12
    sdesc_h = max(50, min(110, remaining))
    sd_rect = pygame.Rect(x, y, fw, sdesc_h)
    state._field_rects['star_description'] = _draw_field(
        screen, sd_rect, 'Star description', _field_value('star_description'),
        fonts['sm'], fonts['xs'],
        active=(state.active_field == 'star_description'),
        multiline=True,
        placeholder='What is special about this star?')


def draw_status_bar(screen, layout, state, fonts, embedded):
    """Render the bottom status bar with hints and dirty markers.

    Parameters:
        screen: pygame.Surface — target display surface.
        layout: Layout — current panel geometry.
        state: EditorState — editor state.
        fonts: dict — font registry.
        embedded: bool — adjusts hint text based on context.

    Returns:
        None: draws directly to `screen`.
    """
    rect = layout.status_bar
    _draw_panel(screen, rect)
    msg = state.status
    if state.dirty:
        parts = []
        if state.constellations_dirty:
            parts.append('constellations')
        if state.stars_dirty:
            parts.append('stars')
        msg = '● ' + msg + f'   (unsaved: {", ".join(parts)})'
    surf = fonts['sm'].render(msg, True, TEXT)
    screen.blit(surf, (rect.x + 12,
                       rect.y + (rect.height - surf.get_height()) // 2))
    if embedded:
        hint = 'Ctrl+S save · Ctrl+N new · Ctrl+Shift+E back to game'
    else:
        hint = ('Drag stars · click two for an edge · right-click removes · '
                'Ctrl+S save · Ctrl+N new')
    hint_surf = fonts['xs'].render(hint, True, MUTED)
    if hint_surf.get_width() + 24 < rect.width - surf.get_width():
        screen.blit(hint_surf, (
            rect.right - hint_surf.get_width() - 12,
            rect.y + (rect.height - hint_surf.get_height()) // 2))


def draw_search_modal(screen, layout, state, fonts, mouse_pos):
    """Render the "Add Star" search modal if it is open.

    Parameters:
        screen: pygame.Surface — target display surface.
        layout: Layout — current panel geometry.
        state: EditorState — editor state.
        fonts: dict — font registry.
        mouse_pos: tuple of (int, int) — current mouse coordinates.

    Returns:
        None: returns early if `state.search_open` is False.
    """
    if not state.search_open:
        return
    overlay = pygame.Surface((layout.w, layout.h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))
    mw, mh = 520, 460
    mrect = pygame.Rect((layout.w - mw) // 2, (layout.h - mh) // 2, mw, mh)
    pygame.draw.rect(screen, PANEL_FILL, mrect, border_radius=14)
    pygame.draw.rect(screen, FIELD_BORDER_ACTIVE, mrect, 2, border_radius=14)
    pad = 16
    x = mrect.x + pad
    y = mrect.y + pad
    _draw_text(screen, 'Add a star to this constellation',
               fonts['md'], ACCENT, x, y)
    y += fonts['md'].get_linesize() + 6
    _draw_text(screen,
               'Type to filter from stars_v2.json. '
               'Enter to add, Esc to cancel.',
               fonts['xs'], MUTED, x, y)
    y += fonts['xs'].get_linesize() + 8
    sb_rect = pygame.Rect(x, y, mrect.width - pad * 2, 36)
    pygame.draw.rect(screen, FIELD_BG_ACTIVE, sb_rect, border_radius=6)
    pygame.draw.rect(screen, FIELD_BORDER_ACTIVE, sb_rect, 2, border_radius=6)
    text = state.search_text or ''
    if not text:
        ph = fonts['sm'].render('Search...', True, MUTED)
        screen.blit(ph, (sb_rect.x + 10,
                         sb_rect.y + (sb_rect.height - ph.get_height()) // 2))
    else:
        ts = fonts['sm'].render(text, True, TEXT)
        screen.blit(ts, (sb_rect.x + 10,
                         sb_rect.y + (sb_rect.height - ts.get_height()) // 2))
    if (pygame.time.get_ticks() // 500) % 2 == 0:
        text_w = fonts['sm'].size(text)[0]
        cx = sb_rect.x + 10 + text_w + 1
        pygame.draw.line(screen, TEXT,
                         (cx, sb_rect.y + 8), (cx, sb_rect.bottom - 8), 2)
    y = sb_rect.bottom + 10
    results_rect = pygame.Rect(x, y, mrect.width - pad * 2,
                               mrect.bottom - y - pad)
    pygame.draw.rect(screen, (12, 16, 36), results_rect, border_radius=6)
    row_h = 28
    visible = max(1, results_rect.height // row_h)
    state._search_visible = visible
    state._search_result_rects = []
    end = min(state.search_scroll + visible, len(state.search_results))
    for i in range(state.search_scroll, end):
        s = state.search_results[i]
        rr = pygame.Rect(results_rect.x,
                         results_rect.y + (i - state.search_scroll) * row_h,
                         results_rect.width, row_h)
        state._search_result_rects.append((rr, i))
        is_sel = (i == state.search_selected)
        is_hover = rr.collidepoint(mouse_pos)
        if is_sel:
            pygame.draw.rect(screen, (60, 80, 160), rr, border_radius=4)
        elif is_hover:
            pygame.draw.rect(screen, (35, 45, 90), rr, border_radius=4)
        name = s.get('name', '?')
        const = s.get('constellation', '')
        mag = s.get('magnitude')
        bits = [name]
        if const:
            bits.append(f'· {const}')
        if mag is not None:
            bits.append(f'· mag {mag}')
        label = '  '.join(bits)
        ls = fonts['sm'].render(label, True, TEXT if is_sel else MUTED)
        screen.blit(ls, (rr.x + 10, rr.y + (row_h - ls.get_height()) // 2))
    if not state.search_results:
        msg = 'No matching stars. Use import_stars.py to add new ones first.'
        for i, line in enumerate(_wrap_text(msg, fonts['sm'],
                                            results_rect.width - 20)):
            ls = fonts['sm'].render(line, True, WARN)
            screen.blit(ls, (results_rect.x + 10,
                            results_rect.y + 10 + i
                            * fonts['sm'].get_linesize()))


# ---------------------------------------------------------------------------
# event handling
# ---------------------------------------------------------------------------
def handle_canvas_click(state, layout, pos, button):
    """Process a mouse click on the canvas.

    Parameters:
        state: EditorState — editor state to mutate.
        layout: Layout — current panel geometry.
        pos: tuple of (int, int) — click position in screen coordinates.
        button: int — pygame mouse button (1 = left, 3 = right).

    Returns:
        bool: True if the click was consumed by the canvas.
    """
    cv = layout.canvas
    if not cv.collidepoint(pos):
        return False
    c = state.current
    if c is None:
        return False
    state._commit_num_buffer()
    idx = hit_test_star(cv, c['display_stars'], pos)
    if button == 3:
        if idx is not None:
            state.remove_star_from_current(idx)
            return True
        return False
    if idx is None:
        state.selected_star_idx = None
        state.active_field = None
        return True
    if state.selected_star_idx is None or state.selected_star_idx == idx:
        state.selected_star_idx = idx
        state.active_field = None
        state.dragging = True
        sx, sy = norm_to_screen(cv, c['display_stars'][idx]['pos'])
        state.drag_offset = (sx - pos[0], sy - pos[1])
    else:
        state.toggle_edge(state.selected_star_idx, idx)
        state.selected_star_idx = idx
        state.active_field = None
    return True


def handle_canvas_drag(state, layout, pos):
    """Update the position of the currently dragged star.

    Parameters:
        state: EditorState — editor state to mutate.
        layout: Layout — current panel geometry.
        pos: tuple of (int, int) — current mouse position.

    Returns:
        bool: True if a star was successfully moved.
    """
    if not state.dragging or state.selected_star_idx is None:
        return False
    c = state.current
    if c is None:
        return False
    idx = state.selected_star_idx
    if idx >= len(c['display_stars']):
        return False
    cv = layout.canvas
    target = (pos[0] + state.drag_offset[0], pos[1] + state.drag_offset[1])
    nx, ny = screen_to_norm(cv, target)
    c['display_stars'][idx]['pos'] = [round(nx, 4), round(ny, 4)]
    state.mark_const_dirty()
    return True


def handle_text_input(state, event):
    """Route a key event to the currently focused editable field.

    Handles Tab cycling across constellation and star fields, Escape to
    blur, numeric input buffering for star magnitude and distance, and
    keeps the star-name field in sync with the display list and the
    `stars_by_name` index.

    Parameters:
        state: EditorState — editor state to mutate.
        event: pygame.event.Event — a KEYDOWN event.

    Returns:
        bool: True if the event was consumed.
    """
    if state.active_field is None or event.type != pygame.KEYDOWN:
        return False
    if event.key == pygame.K_TAB:
        order = list(CONST_FIELDS)
        if (state.selected_star_idx is not None
                and state.get_selected_star_record() is not None):
            order += list(STAR_FIELDS)
        try:
            i = order.index(state.active_field)
            state.set_active_field(order[(i + 1) % len(order)])
        except ValueError:
            pass
        return True
    if event.key == pygame.K_ESCAPE:
        state.set_active_field(None)
        return True
    if state.active_field in NUMERIC_STAR_FIELDS:
        if event.key == pygame.K_BACKSPACE:
            state._num_buffer = state._num_buffer[:-1]
            return True
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            state._commit_num_buffer()
            state.set_active_field(None)
            return True
        if event.unicode and event.unicode.isprintable():
            if event.unicode in '0123456789.-+eE':
                state._num_buffer += event.unicode
            return True
        return False
    if state.active_field in STAR_FIELDS:
        star = state.get_selected_star_record()
        if star is None:
            return False
        key = STAR_FIELD_TO_KEY[state.active_field]
        current_text = star.get(key, '') or ''
        if event.key == pygame.K_BACKSPACE:
            new_text = current_text[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if state.active_field == 'star_description':
                new_text = current_text + '\n'
            else:
                state.set_active_field(None)
                return True
        elif event.unicode and event.unicode.isprintable():
            new_text = current_text + event.unicode
        else:
            return False
        star[key] = new_text
        state.mark_star_dirty()
        if state.active_field == 'star_name':
            c = state.current
            old_name = None
            if c is not None and state.selected_star_idx is not None:
                ds = c['display_stars'][state.selected_star_idx]
                old_name = ds.get('name')
                ds['name'] = new_text
                state.mark_const_dirty()
            if old_name and old_name in state.stars_by_name:
                state.stars_by_name.pop(old_name, None)
            if new_text:
                state.stars_by_name[new_text] = star
        return True
    c = state.current
    if c is None:
        return False
    key_map = {'name': 'name', 'subtitle': 'subtitle',
               'months': 'best_months', 'description': 'description'}
    field_key = key_map.get(state.active_field)
    if field_key is None:
        return False
    current_text = c.get(field_key, '') or ''
    if event.key == pygame.K_BACKSPACE:
        c[field_key] = current_text[:-1]
        state.mark_const_dirty()
        return True
    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        if state.active_field == 'description':
            c[field_key] = current_text + '\n'
            state.mark_const_dirty()
        else:
            state.set_active_field(None)
        return True
    if event.unicode and event.unicode.isprintable():
        c[field_key] = current_text + event.unicode
        state.mark_const_dirty()
        return True
    return False


def handle_search_input(state, event):
    """Process a key event while the Add-Star search modal is open.

    Parameters:
        state: EditorState — editor state to mutate.
        event: pygame.event.Event — a KEYDOWN event.

    Returns:
        bool: True if the event was consumed.
    """
    if not state.search_open or event.type != pygame.KEYDOWN:
        return False
    if event.key == pygame.K_ESCAPE:
        state.search_open = False
        return True
    if event.key == pygame.K_BACKSPACE:
        state.search_text = state.search_text[:-1]
        state.update_search()
        return True
    if event.key == pygame.K_DOWN:
        if state.search_results:
            state.search_selected = min(state.search_selected + 1,
                                        len(state.search_results) - 1)
            visible = getattr(state, '_search_visible', 10)
            if state.search_selected >= state.search_scroll + visible:
                state.search_scroll = state.search_selected - visible + 1
        return True
    if event.key == pygame.K_UP:
        if state.search_results:
            state.search_selected = max(state.search_selected - 1, 0)
            if state.search_selected < state.search_scroll:
                state.search_scroll = state.search_selected
        return True
    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        if state.search_results:
            picked = state.search_results[state.search_selected]
            state.add_star_to_current(picked, pos=(0.5, 0.5))
            state.search_open = False
        return True
    if event.unicode and event.unicode.isprintable():
        state.search_text += event.unicode
        state.update_search()
        return True
    return False


# ---------------------------------------------------------------------------
# embeddable app
# ---------------------------------------------------------------------------
class EditorApp:
    """Wrap the editor for embedding inside the main game.

    Example usage::

        app = EditorApp(screen, constellations, stars, save_manager)
        for event in events:
            app.handle_event(event)
        app.render(screen)
        if app.want_exit:
            ...
    """

    def __init__(self, screen, constellations, stars, save_manager,
                 embedded=True):
        """Construct an EditorApp bound to a target surface and data.

        Parameters:
            screen: pygame.Surface — the surface to render into.
            constellations: list of dict — constellation records to edit.
            stars: list of dict — star records (stars_v2 format).
            save_manager: SaveManager — used to persist edits.
            embedded: bool — True when launched from inside the main game.
        """
        self.state = EditorState(constellations, stars, save_manager)
        self.layout = Layout(*screen.get_size())
        self.fonts = _make_fonts()
        self.embedded = embedded
        self.want_exit = False

    def on_resize(self, w, h):
        """Update internal layout on window resize.

        Parameters:
            w: int — new width in pixels.
            h: int — new height in pixels.

        Returns:
            None.
        """
        self.layout.update(w, h)

    def handle_event(self, event):
        """Dispatch a pygame event to the appropriate handler.

        Parameters:
            event: pygame.event.Event — any pygame event.

        Returns:
            bool: True if the event was consumed by the editor.
        """
        state = self.state
        layout = self.layout

        if event.type == pygame.KEYDOWN:
            ctrl = event.mod & pygame.KMOD_CTRL
            shift = event.mod & pygame.KMOD_SHIFT

            if self.embedded and ctrl and shift and event.key == pygame.K_e:
                self.want_exit = True
                return True

            if ctrl and event.key == pygame.K_s:
                state.save()
                return True

            if ctrl and event.key == pygame.K_n:
                state.new_constellation()
                return True

            if state.search_open:
                handle_search_input(state, event)
                return True

            if state.active_field is not None:
                handle_text_input(state, event)
                return True

            if event.key == pygame.K_DELETE:
                if state.selected_star_idx is not None:
                    state.remove_star_from_current(state.selected_star_idx)
                return True

            if event.key == pygame.K_ESCAPE:
                state.selected_star_idx = None
                state.set_active_field(None)
                return True

            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if state.search_open:
                for rr, i in getattr(state, '_search_result_rects', []):
                    if rr.collidepoint(event.pos):
                        picked = state.search_results[i]
                        state.add_star_to_current(picked, pos=(0.5, 0.5))
                        state.search_open = False
                        break
                return True

            if layout.left_panel.collidepoint(event.pos):
                if (hasattr(state, '_scroll_up_btn')
                        and state._scroll_up_btn.collidepoint(event.pos)):
                    state.scroll_up()
                    return True
                if (hasattr(state, '_scroll_down_btn')
                        and state._scroll_down_btn.collidepoint(event.pos)):
                    state.scroll_down()
                    return True
                for rr, i in getattr(state, '_list_rects', []):
                    if rr.collidepoint(event.pos):
                        state.select_constellation(i)
                        return True
                if (hasattr(state, '_new_btn')
                        and state._new_btn.collidepoint(event.pos)):
                    state.new_constellation()
                    return True
                if (hasattr(state, '_save_btn')
                        and state._save_btn.collidepoint(event.pos)):
                    state.save()
                    return True
                if (self.embedded and hasattr(state, '_back_btn')
                        and state._back_btn.collidepoint(event.pos)):
                    self.want_exit = True
                    return True
                return True

            if layout.right_panel.collidepoint(event.pos):
                state._commit_num_buffer()
                clicked_field = None
                for key, fr in getattr(state, '_field_rects', {}).items():
                    if fr.collidepoint(event.pos):
                        clicked_field = key
                        break
                if clicked_field is not None:
                    state.set_active_field(clicked_field)
                else:
                    state.set_active_field(None)
                if (hasattr(state, '_add_star_btn')
                        and state._add_star_btn.collidepoint(event.pos)):
                    if state.current is None:
                        state.status = 'Make a constellation first (Ctrl+N).'
                    else:
                        state.search_open = True
                        state.search_text = ''
                        state.update_search()
                return True

            if layout.canvas_outer.collidepoint(event.pos):
                state.set_active_field(None)
                handle_canvas_click(state, layout, event.pos, event.button)
                return True

            return False

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                state.dragging = False
            return True

        if event.type == pygame.MOUSEMOTION:
            if state.dragging:
                handle_canvas_drag(state, layout, event.pos)
            return True

        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            if layout.left_panel.collidepoint(mouse_pos):
                if event.y > 0:
                    state.scroll_up()
                elif event.y < 0:
                    state.scroll_down()
            if state.search_open:
                n = len(state.search_results)
                visible = getattr(state, '_search_visible', 1)
                max_scroll = max(0, n - visible)
                state.search_scroll = max(0, min(
                    max_scroll, state.search_scroll - event.y))
            return True

        return False

    def render(self, screen):
        """Draw the full editor UI for the current frame.

        Parameters:
            screen: pygame.Surface — the surface to render into.

        Returns:
            None.
        """
        mouse_pos = pygame.mouse.get_pos()
        screen.fill(BG)
        draw_left_panel(screen, self.layout, self.state, self.fonts,
                        mouse_pos, self.embedded)
        draw_canvas(screen, self.layout, self.state, self.fonts, mouse_pos)
        draw_right_panel(screen, self.layout, self.state, self.fonts,
                         mouse_pos)
        draw_status_bar(screen, self.layout, self.state, self.fonts,
                        self.embedded)
        draw_search_modal(screen, self.layout, self.state, self.fonts,
                          mouse_pos)


# ---------------------------------------------------------------------------
# standalone entry point
# ---------------------------------------------------------------------------
def main():
    """Launch the editor as a standalone desktop application.

    Loads constellations and stars from the master JSON files via the
    desktop `SaveManager` and runs an event loop until the window is
    closed.

    Returns:
        None.
    """
    pygame.init()
    pygame.key.set_repeat(450, 35)
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.RESIZABLE)
    pygame.display.set_caption('Constellation Editor (standalone)')
    clock = pygame.time.Clock()

    # standalone always uses desktop SaveManager
    from save_manager import SaveManager
    from config import CONSTELLATIONS_PATH, STARS_PATH
    sm = SaveManager(CONSTELLATIONS_PATH, STARS_PATH)
    constellations = sm.load_constellations()
    stars = sm.load_stars()

    app = EditorApp(screen, constellations, stars, sm, embedded=False)

    running = True
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode(
                    (event.w, event.h), pygame.RESIZABLE)
                app.on_resize(event.w, event.h)
            else:
                app.handle_event(event)
        app.render(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    # Input:  CONSTELLATIONS_PATH and STARS_PATH from config.py loaded
    #         from disk via SaveManager.
    # Expected: a resizable pygame window titled "Constellation Editor
    #         (standalone)" is opened. Ctrl+S saves edits, Ctrl+N creates
    #         a new (empty) constellation, and closing the window exits.
    main()
