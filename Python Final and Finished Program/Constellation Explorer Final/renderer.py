"""Render every frame of the Constellation Explorer game window."""

__author__ = "Fabian Anguiano"

import pygame

from config import (
    TEXT_COLOR, MUTED_TEXT, PANEL_BORDER, ACCENT, ACCENT_SOFT,
    SUCCESS, SCROLL_VISIBLE,
    STAR_TIERS, OBSERVER_LOCATION,
    GUIDE_LINE_GLOW, GUIDE_LINE_MID, GUIDE_LINE_CORE,
    EDGE_DONE_CORE, EDGE_DONE_MID, EDGE_DONE_GLOW,
    DRAG_LINE_CORE, DRAG_LINE_GLOW,
)
from layout import SHINE_FRAME_COUNT


# -------------------------------
# cached single-line text surfaces
# -------------------------------
_text_cache = {}
_text_cache_version = -1


def _cached_text(layout, font, text, color):
    """Render a string once and cache the resulting surface.

    Parameters:
        layout: Layout
            The current layout (used to detect resize events).
        font: pygame.font.Font
            The font to render with.
        text: str
            The string to render.
        color: tuple of int
            RGB color for the text.
    Returns:
        surface: pygame.Surface
            A reusable RGBA text surface.
    """
    global _text_cache, _text_cache_version

    # invalidate the cache when the layout has been rebuilt
    if layout.version != _text_cache_version:
        _text_cache.clear()
        _text_cache_version = layout.version

    key = (id(font), text, color)
    surf = _text_cache.get(key)

    if surf is None:
        surf = font.render(text, True, color).convert_alpha()
        _text_cache[key] = surf

    return surf


def _draw_text(screen, layout, text, font, color, x, y):
    """Draw a single-line string at a screen position.

    Parameters:
        screen: pygame.Surface
            The destination surface.
        layout: Layout
            Used for cache invalidation.
        text: str
            The string to draw.
        font: pygame.font.Font
            The font to render with.
        color: tuple of int
            RGB color for the text.
        x: int
            Left-edge pixel coordinate.
        y: int
            Top-edge pixel coordinate.
    Returns:
        rect: pygame.Rect
            The blitted text rectangle.
    """
    surf = _cached_text(layout, font, text, color)
    screen.blit(surf, (x, y))
    return surf.get_rect(topleft=(x, y))


# -------------------------------
# cached wrapped paragraphs
# -------------------------------
_wrap_cache = {}
_wrap_cache_version = -1


def _cached_wrap(layout, text, font, width):
    """Wrap a string into lines once and cache the result.

    Parameters:
        layout: Layout
            The current layout (used to detect resize events).
        text: str
            The full string to wrap.
        font: pygame.font.Font
            Font used to measure word widths.
        width: int
            Maximum line width in pixels.
    Returns:
        lines: list of str
            One string per visual line of wrapped text.
    """
    global _wrap_cache, _wrap_cache_version

    # invalidate the cache when the layout has been rebuilt
    if layout.version != _wrap_cache_version:
        _wrap_cache.clear()
        _wrap_cache_version = layout.version

    key = (text, id(font), width)
    lines = _wrap_cache.get(key)

    if lines is None:
        lines = wrap_text(text, font, width)
        _wrap_cache[key] = lines

    return lines


def invalidate_text_caches():
    """Force the renderer to rebuild its text caches.

    Call this after the editor changes data so renamed
    constellations or stars show up correctly on the next frame.
    """
    global _text_cache, _wrap_cache
    global _text_cache_version, _wrap_cache_version
    _text_cache.clear()
    _wrap_cache.clear()
    _text_cache_version = -1
    _wrap_cache_version = -1


# -------------------------------
# small drawing helpers
# -------------------------------
def wrap_text(text, font, width):
    """Break a string into lines that fit a maximum pixel width.

    Parameters:
        text: str
            The string to wrap.
        font: pygame.font.Font
            Font used to measure word widths.
        width: int
            Maximum line width in pixels.
    Returns:
        lines: list of str
            One entry per visual line.
    """
    words = text.split()
    lines = []
    current = ''

    for word in words:
        test = current + (' ' if current else '') + word
        if font.size(test)[0] <= width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def _radius_for_magnitude(mag):
    """Pick a star radius for a given apparent magnitude.

    Parameters:
        mag: float
            Apparent magnitude (lower is brighter).
    Returns:
        radius: int
            The pixel radius from ``STAR_TIERS`` matching ``mag``.
    """
    for max_mag, radius, _glow, _alpha in STAR_TIERS:
        if mag <= max_mag:
            return radius
    return STAR_TIERS[-1][1]


def draw_star(screen, layout, x, y, radius=8,
              selected=False, shine=0.0, core_color=None):
    """Draw one star, optionally selected and/or glowing.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        layout: Layout
            Source of pre-built sprites.
        x: int
            Centre x coordinate in pixels.
        y: int
            Centre y coordinate in pixels.
        radius: int, optional
            Core radius in pixels. Defaults to ``8``.
        selected: bool, optional
            Draws a highlighted variant when ``True``.
        shine: float, optional
            Animation progress in ``[0.0, 1.0]``; values above
            ``0.01`` add a fading shine ring.
        core_color: tuple of int, optional
            Override RGB color for the star center.
    """
    ix, iy = int(x), int(y)

    # draw the shine animation first so it sits behind the star
    if shine > 0.01:
        frame = min(
            SHINE_FRAME_COUNT - 1,
            int((1.0 - shine) * SHINE_FRAME_COUNT),
        )
        shine_sprite = layout.shine_sprites.get((radius, frame))
        if shine_sprite is not None:
            screen.blit(
                shine_sprite,
                shine_sprite.get_rect(center=(ix, iy)),
            )

    # draw the star itself
    if core_color is not None:
        sprite = layout.get_star_sprite(radius, core_color, selected)
    else:
        sprite = layout.star_sprites.get((radius, selected))

    if sprite is not None:
        screen.blit(sprite, sprite.get_rect(center=(ix, iy)))


def draw_button(screen, layout, rect, label, font, pressed=False):
    """Draw a labelled rectangular button.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        layout: Layout
            Used for the cached text surface.
        rect: pygame.Rect
            Button rectangle.
        label: str
            Visible label text.
        font: pygame.font.Font
            Font used for the label.
        pressed: bool, optional
            Draws a brighter fill when ``True``.
    """
    fill = (38, 44, 80) if pressed else (24, 28, 56)

    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=14)

    txt = _cached_text(layout, font, label, TEXT_COLOR)
    screen.blit(txt, txt.get_rect(center=rect.center))


def draw_arrow_button(screen, rect, direction, enabled):
    """Draw an up or down arrow button.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        rect: pygame.Rect
            Button rectangle.
        direction: str
            ``'up'`` or ``'down'``.
        enabled: bool
            Renders in a dimmed style when ``False``.
    """
    fill = (38, 46, 88) if enabled else (20, 22, 42)
    pygame.draw.rect(screen, fill, rect, border_radius=8)

    pygame.draw.rect(
        screen,
        PANEL_BORDER if enabled else (70, 75, 105),
        rect,
        1,
        border_radius=8,
    )

    color = TEXT_COLOR if enabled else (90, 95, 120)
    cx, cy = rect.centerx, rect.centery
    sz = min(rect.width, rect.height) // 4

    if direction == 'up':
        pts = [(cx, cy - sz), (cx - sz, cy + sz), (cx + sz, cy + sz)]
    else:
        pts = [(cx, cy + sz), (cx - sz, cy - sz), (cx + sz, cy - sz)]

    pygame.draw.polygon(screen, color, pts)


# -------------------------------
# line drawing
# -------------------------------
def _draw_guide_edge(screen, p1, p2):
    """Draw a still-unfinished guide line between two stars.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        p1: tuple of int
            One endpoint in pixels.
        p2: tuple of int
            The other endpoint in pixels.
    """
    pygame.draw.line(screen, GUIDE_LINE_GLOW, p1, p2, 7)
    pygame.draw.line(screen, GUIDE_LINE_MID, p1, p2, 4)
    pygame.draw.line(screen, GUIDE_LINE_CORE, p1, p2, 2)
    pygame.draw.aaline(screen, GUIDE_LINE_CORE, p1, p2)


def _draw_completed_edge(screen, p1, p2):
    """Draw a finished line with a bright golden glow.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        p1: tuple of int
            One endpoint in pixels.
        p2: tuple of int
            The other endpoint in pixels.
    """
    pygame.draw.line(screen, EDGE_DONE_GLOW, p1, p2, 9)
    pygame.draw.line(screen, EDGE_DONE_MID, p1, p2, 5)
    pygame.draw.line(screen, EDGE_DONE_CORE, p1, p2, 2)
    pygame.draw.aaline(screen, EDGE_DONE_CORE, p1, p2)


def _draw_drag_line(screen, p1, p2):
    """Draw the live drag line that follows the pointer.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        p1: tuple of int
            Starting endpoint (the last visited star) in pixels.
        p2: tuple of int
            Current pointer position in pixels.
    """
    pygame.draw.line(screen, DRAG_LINE_GLOW, p1, p2, 6)
    pygame.draw.line(screen, DRAG_LINE_CORE, p1, p2, 2)
    pygame.draw.aaline(screen, DRAG_LINE_CORE, p1, p2)


# -------------------------------
# left side panel
# -------------------------------
def draw_left_panel(screen, layout, state):
    """Draw the constellation list, scroll arrows, and clear button.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        layout: Layout
            Current layout.
        state: GameState
            The active game state; updated in place with hit rects.
    """
    lp = layout.left_panel
    panel = layout.panel_surfaces.get('left')

    if panel:
        screen.blit(panel, lp.topleft)

    x = layout.list_x
    y = lp.y + int(lp.height * 0.04)
    mw = layout.list_mw

    _draw_text(
        screen, layout, 'Constellation',
        layout.font_xs, ACCENT, x, y,
    )
    y += layout.font_xs.get_linesize()

    _draw_text(
        screen, layout, 'Explorer',
        layout.font_xl, TEXT_COLOR, x, y,
    )
    y += layout.font_xl.get_linesize() + int(lp.height * 0.03)

    # up arrow button
    arrow_h = max(22, int(lp.height * 0.04))
    arrow_w = int(lp.width * 0.30)
    arrow_x = x + (mw - arrow_w) // 2

    state._scroll_up_rect = pygame.Rect(arrow_x, y, arrow_w, arrow_h)
    draw_arrow_button(
        screen, state._scroll_up_rect, 'up', state.can_scroll_up,
    )
    y += arrow_h + 4

    # list of constellation names
    row_h = layout.list_row_h
    names = state.data.constellation_names()
    state._list_rects = []
    mouse_pos = pygame.mouse.get_pos()

    for i in range(SCROLL_VISIBLE):
        idx = state.scroll_offset + i
        if idx >= len(names):
            break

        name = names[idx]
        row_rect = pygame.Rect(x, y, mw, row_h)
        state._list_rects.append((row_rect, name))

        is_selected = (name == state.selected_constellation_name)

        if is_selected and layout.row_selected_surf:
            screen.blit(layout.row_selected_surf, (x, y))
        elif row_rect.collidepoint(mouse_pos) and layout.row_hover_surf:
            screen.blit(layout.row_hover_surf, (x, y))

        label = f'{idx + 1}. {name}'
        color = SUCCESS if is_selected else TEXT_COLOR

        _draw_text(
            screen, layout, label, layout.font_sm, color,
            x + 10,
            y + (row_h - layout.font_sm.get_height()) // 2,
        )

        y += row_h + 2

    # down arrow button
    y += 2
    state._scroll_down_rect = pygame.Rect(arrow_x, y, arrow_w, arrow_h)
    draw_arrow_button(
        screen, state._scroll_down_rect, 'down', state.can_scroll_down,
    )
    y += arrow_h + int(lp.height * 0.03)

    # status text
    _draw_text(
        screen, layout, 'Status', layout.font_md, TEXT_COLOR, x, y,
    )
    y += layout.font_md.get_linesize()

    wrapped_status = _cached_wrap(
        layout, state.status, layout.font_xs, mw,
    )[:3]
    for line in wrapped_status:
        _draw_text(
            screen, layout, line, layout.font_xs, MUTED_TEXT, x, y,
        )
        y += layout.font_xs.get_linesize()

    # clear button
    draw_button(
        screen, layout, layout.clear_btn, 'Clear', layout.font_md,
    )


# -------------------------------
# center panel
# -------------------------------
def draw_center_panel(screen, layout, state):
    """Draw the active constellation's stars, edges, and drag line.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        layout: Layout
            Current layout.
        state: GameState
            The active game state.
    """
    co = layout.center_outer
    cs = layout.center_stage

    panel = layout.panel_surfaces.get('center')
    if panel:
        screen.blit(panel, co.topleft)

    if layout.stage_bg_surf:
        screen.blit(layout.stage_bg_surf, cs.topleft)

    _draw_text(
        screen, layout, 'Draw Zone', layout.font_sm, ACCENT,
        co.x + 18, co.y + 14,
    )

    c = state.constellation
    if not c:
        msg = 'Select a constellation from the list to begin.'
        wrapped = _cached_wrap(
            layout, msg, layout.font_sm, int(cs.width * 0.8),
        )
        for i, line in enumerate(wrapped):
            _draw_text(
                screen, layout, line, layout.font_sm, MUTED_TEXT,
                cs.x + int(cs.width * 0.1),
                cs.y + cs.height // 2 - 20 + i * 24,
            )
        return

    pts = state.star_positions(cs)
    required = state.required_edges()

    # draw the lines still needed
    for (a, b) in required:
        if (a, b) in state.drawn_edges:
            continue
        if a < len(pts) and b < len(pts):
            _draw_guide_edge(screen, pts[a], pts[b])

    # draw the finished lines on top of the guides
    for (a, b) in state.drawn_edges:
        if a < len(pts) and b < len(pts):
            _draw_completed_edge(screen, pts[a], pts[b])

    # draw the live drag line
    if (
        state.last_visited_idx is not None
        and state.drag_pos
        and state.last_visited_idx < len(pts)
    ):
        _draw_drag_line(
            screen, pts[state.last_visited_idx], state.drag_pos,
        )

    # draw all stars
    for i, item in enumerate(c['display_stars']):
        star = state.data.get_star(item['name'])
        is_sel = (
            state.selected_star and star
            and state.selected_star['name'] == star['name']
        )
        is_trail_head = (state.last_visited_idx == i)
        shine = state.shine_level(i)
        radius = _radius_for_magnitude(state.star_magnitude(i))

        core_color = state.data.get_star_color(item['name'])

        draw_star(
            screen, layout, pts[i][0], pts[i][1], radius,
            selected=(is_sel or is_trail_head),
            shine=shine,
            core_color=core_color,
        )

    # progress counter
    done = len(state.drawn_edges)
    total = len(required)

    _draw_text(
        screen, layout, f'{done}/{total}', layout.font_sm, ACCENT,
        co.right - 70, co.y + 14,
    )

    # finish flash overlay
    if state.completed and layout.completion_flash:
        screen.blit(layout.completion_flash, cs.topleft)


# -------------------------------
# right side panel
# -------------------------------
def draw_right_panel(screen, layout, state):
    """Draw the description and best-viewing info for the active constellation.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        layout: Layout
            Current layout.
        state: GameState
            The active game state.
    """
    rp = layout.right_panel
    panel = layout.panel_surfaces.get('right')

    if panel:
        screen.blit(panel, rp.topleft)

    x = rp.x + int(rp.width * 0.08)
    y = rp.y + int(rp.height * 0.06)
    mw = int(rp.width * 0.82)

    c = state.constellation

    if not c:
        _draw_text(
            screen, layout, 'Details',
            layout.font_lg, TEXT_COLOR, x, y,
        )
        y += layout.font_lg.get_linesize() + int(rp.height * 0.02)

        msg = (
            'Select a constellation from the list, then sweep across '
            'its stars to connect them.'
        )

        for line in _cached_wrap(layout, msg, layout.font_sm, mw)[:6]:
            _draw_text(
                screen, layout, line, layout.font_sm, MUTED_TEXT, x, y,
            )
            y += layout.font_sm.get_linesize()

        return

    # constellation name
    _draw_text(
        screen, layout, c['name'], layout.font_xl, TEXT_COLOR, x, y,
    )
    y += layout.font_xl.get_linesize()

    # short subtitle
    _draw_text(
        screen, layout, c.get('subtitle', ''),
        layout.font_md, ACCENT, x, y,
    )
    y += layout.font_md.get_linesize() + int(rp.height * 0.03)

    # best viewing months
    best_viewing_text = f'Best viewing — {OBSERVER_LOCATION}'

    wrapped_loc = _cached_wrap(
        layout, best_viewing_text, layout.font_xs, mw,
    )[:2]
    for line in wrapped_loc:
        _draw_text(
            screen, layout, line, layout.font_xs, MUTED_TEXT, x, y,
        )
        y += layout.font_xs.get_linesize()

    wrapped_months = _cached_wrap(
        layout, c.get('best_months', '?'), layout.font_md, mw,
    )[:2]
    for line in wrapped_months:
        _draw_text(
            screen, layout, line, layout.font_md, SUCCESS, x, y,
        )
        y += layout.font_md.get_linesize()

    y += int(rp.height * 0.025)

    _draw_text(
        screen, layout, 'About', layout.font_md, TEXT_COLOR, x, y,
    )
    y += layout.font_md.get_linesize()

    reserved = layout.font_sm.get_linesize() * 2 + int(rp.height * 0.04)
    avail = max(0, rp.bottom - y - reserved)
    max_lines = max(
        2, min(12, avail // max(1, layout.font_sm.get_linesize())),
    )

    # description text
    wrapped_desc = _cached_wrap(
        layout, c.get('description', ''), layout.font_sm, mw,
    )[:max_lines]
    for line in wrapped_desc:
        _draw_text(
            screen, layout, line, layout.font_sm, MUTED_TEXT, x, y,
        )
        y += layout.font_sm.get_linesize()

    y += int(rp.height * 0.02)

    n_stars = len(c.get('display_stars', []))
    n_edges = len(state.required_edges())

    _draw_text(
        screen, layout, f'{n_stars} stars · {n_edges} edges',
        layout.font_sm, ACCENT_SOFT, x, y,
    )
    y += layout.font_sm.get_linesize() + int(rp.height * 0.02)

    # progress message
    if state.completed:
        _draw_text(
            screen, layout, 'Tap a star for details.',
            layout.font_sm, SUCCESS, x, y,
        )
    elif state.drawn_edges:
        remaining = n_edges - len(state.drawn_edges)
        _draw_text(
            screen, layout, f'{remaining} edges remaining',
            layout.font_sm, ACCENT, x, y,
        )


# -------------------------------
# bottom panel
# -------------------------------
def draw_bottom_panel(screen, layout, state):
    """Draw the star-details card and mini-map of the constellation.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        layout: Layout
            Current layout.
        state: GameState
            The active game state.
    """
    bp = layout.bottom_panel
    panel = layout.panel_surfaces.get('bottom')

    if panel:
        screen.blit(panel, bp.topleft)

    x = bp.x + int(bp.width * 0.04)
    y_title = bp.y + int(bp.height * 0.12)

    if not state.completed or not state.selected_star:
        _draw_text(
            screen, layout, 'Star Details',
            layout.font_md, TEXT_COLOR, x, y_title,
        )

        y = y_title + layout.font_md.get_linesize() + int(bp.height * 0.03)

        if state.completed:
            msg = (
                'Constellation complete! Tap any star above to see '
                'its details here.'
            )
        elif state.constellation:
            msg = (
                'Sweep across the stars to connect them, '
                'then tap one for details.'
            )
        else:
            msg = 'Select a constellation to get started.'

        wrapped = _cached_wrap(
            layout, msg, layout.font_sm, int(bp.width * 0.90),
        )[:3]
        for line in wrapped:
            _draw_text(
                screen, layout, line, layout.font_sm, MUTED_TEXT, x, y,
            )
            y += layout.font_sm.get_linesize()

        return

    star = state.selected_star
    c = state.constellation

    # small mini-map area
    strip_w = int(bp.width * 0.32)
    strip_h = int(bp.height * 0.70)
    strip_x = bp.x + int(bp.width * 0.03)
    strip_y = bp.y + int(bp.height * 0.15)

    strip_rect = pygame.Rect(strip_x, strip_y, strip_w, strip_h)
    pygame.draw.rect(screen, (22, 26, 50), strip_rect, border_radius=12)
    pygame.draw.rect(screen, PANEL_BORDER, strip_rect, 1, border_radius=12)

    pts = state.star_positions(layout.center_stage)

    if pts:
        min_x = min(p[0] for p in pts)
        max_x = max(p[0] for p in pts)
        min_y = min(p[1] for p in pts)
        max_y = max(p[1] for p in pts)

        rw = max(max_x - min_x, 1)
        rh = max(max_y - min_y, 1)

        mapped = []
        pad_x = int(strip_w * 0.12)
        pad_y = int(strip_h * 0.12)
        usable_w = strip_w - 2 * pad_x
        usable_h = strip_h - 2 * pad_y

        # fit star points into the mini-map area
        for px, py in pts:
            nx = (px - min_x) / rw
            ny = (py - min_y) / rh
            mapped.append((
                strip_x + pad_x + int(nx * usable_w),
                strip_y + pad_y + int(ny * usable_h),
            ))

        # finished edges in the mini-map
        for (a, b) in state.drawn_edges:
            if a < len(mapped) and b < len(mapped):
                pygame.draw.line(
                    screen, EDGE_DONE_MID, mapped[a], mapped[b], 2,
                )
                pygame.draw.aaline(
                    screen, EDGE_DONE_CORE, mapped[a], mapped[b],
                )

        # stars in the mini-map
        for i, item in enumerate(c['display_stars']):
            is_sel = (star and item['name'] == star['name'])
            core_color = state.data.get_star_color(item['name'])
            draw_star(
                screen, layout, mapped[i][0], mapped[i][1], 4,
                selected=is_sel, core_color=core_color,
            )

    # star info card
    info_x = strip_rect.right + int(bp.width * 0.03)
    y = y_title

    _draw_text(
        screen, layout, star.get('name', '?'),
        layout.font_lg, TEXT_COLOR, info_x, y,
    )
    y += layout.font_lg.get_linesize() + int(bp.height * 0.02)

    labels_values = [
        ('Constellation', star.get('constellation', '?')),
        ('Magnitude', f"{star.get('magnitude', '?')}"),
        ('Distance', f"{star.get('distance_ly', '?')} light-years"),
        ('Spectral type', star.get('spectral_type', '?')),
    ]

    label_w = max(
        layout.font_xs.size(lbl)[0] for lbl, _ in labels_values
    ) + 14

    # label / value lines
    for lbl, val in labels_values:
        _draw_text(
            screen, layout, lbl, layout.font_xs, MUTED_TEXT, info_x, y,
        )
        _draw_text(
            screen, layout, val, layout.font_xs, TEXT_COLOR,
            info_x + label_w, y,
        )
        y += layout.font_xs.get_linesize() + 2

    y += 4

    desc_w = bp.right - info_x - int(bp.width * 0.04)

    # star description
    if desc_w > 60:
        wrapped = _cached_wrap(
            layout, star.get('description', ''),
            layout.font_xs, desc_w,
        )[:3]
        for line in wrapped:
            _draw_text(
                screen, layout, line, layout.font_xs, MUTED_TEXT,
                info_x, y,
            )
            y += layout.font_xs.get_linesize()


# -------------------------------
# top-level frame renderer
# -------------------------------
def render_frame(screen, layout, state, flip=True):
    """Draw a complete game frame.

    Parameters:
        screen: pygame.Surface
            Destination surface.
        layout: Layout
            Current layout.
        state: GameState
            The active game state.
        flip: bool, optional
            When ``True`` (the default), the display is flipped at
            the end. Pass ``False`` when an overlay (such as the
            editor unlock prompt) will be drawn on top first.
    """
    # draw background
    if layout.background:
        screen.blit(layout.background, (0, 0))
    else:
        screen.fill((6, 7, 18))

    # draw each panel
    draw_left_panel(screen, layout, state)
    draw_center_panel(screen, layout, state)
    draw_right_panel(screen, layout, state)
    draw_bottom_panel(screen, layout, state)

    # present
    if flip:
        pygame.display.flip()


if __name__ == '__main__':
    print('Input: a synthetic font and a 220 pixel column.')
    print('Expected: wrap_text returns several lines, none too wide.')

    import os as _os
    _os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    pygame.display.set_mode((1, 1))

    test_font = pygame.font.SysFont('arial', 16)
    sample = (
        'Constellation Explorer is a small educational app that '
        'lets the player trace constellations on a star field.'
    )
    test_lines = wrap_text(sample, test_font, 220)
    for test_line in test_lines:
        width_px = test_font.size(test_line)[0]
        print(f'{width_px:>3}px  {test_line}')

    pygame.quit()
