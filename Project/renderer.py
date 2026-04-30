"""
renderer.py
This file draws everything on the screen.

It shows:
- panels
- text
- stars
- lines
- buttons
"""

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
# saved text
# -------------------------------
_text_cache = {}
_text_cache_version = -1


def _cached_text(layout, font, text, color):
    global _text_cache, _text_cache_version

    # clear old saved text if layout changed
    if layout.version != _text_cache_version:
        _text_cache.clear()
        _text_cache_version = layout.version

    key = (id(font), text, color)
    surf = _text_cache.get(key)

    # make the text only if it is not saved already
    if surf is None:
        surf = font.render(text, True, color).convert_alpha()
        _text_cache[key] = surf

    return surf


def _draw_text(screen, layout, text, font, color, x, y):
    # draw text on the screen
    surf = _cached_text(layout, font, text, color)
    screen.blit(surf, (x, y))
    return surf.get_rect(topleft=(x, y))


# -------------------------------
# saved wrapped text
# -------------------------------
_wrap_cache = {}
_wrap_cache_version = -1


def _cached_wrap(layout, text, font, width):
    global _wrap_cache, _wrap_cache_version

    # clear old wrapped text if layout changed
    if layout.version != _wrap_cache_version:
        _wrap_cache.clear()
        _wrap_cache_version = layout.version

    key = (text, id(font), width)
    lines = _wrap_cache.get(key)

    # wrap the text only if needed
    if lines is None:
        lines = wrap_text(text, font, width)
        _wrap_cache[key] = lines

    return lines


# -------------------------------
# small drawing helpers
# -------------------------------
def wrap_text(text, font, width):
    # break long text into lines so it fits the space
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
    # choose star size based on brightness
    for max_mag, radius, _glow, _alpha in STAR_TIERS:
        if mag <= max_mag:
            return radius
    return STAR_TIERS[-1][1]


def draw_star(screen, layout, x, y, radius=8,
              selected=False, shine=0.0, core_color=None):
    """
    Draw one star.
    It can also glow or look selected.
    """
    ix, iy = int(x), int(y)

    # draw glow first
    if shine > 0.01:
        frame = min(
            SHINE_FRAME_COUNT - 1,
            int((1.0 - shine) * SHINE_FRAME_COUNT)
        )
        shine_sprite = layout.shine_sprites.get((radius, frame))
        if shine_sprite is not None:
            screen.blit(
                shine_sprite,
                shine_sprite.get_rect(center=(ix, iy))
            )

    # draw the star itself
    if core_color is not None:
        sprite = layout.get_star_sprite(radius, core_color, selected)
    else:
        sprite = layout.star_sprites.get((radius, selected))

    if sprite is not None:
        screen.blit(sprite, sprite.get_rect(center=(ix, iy)))


def draw_button(screen, layout, rect, label, font, pressed=False):
    # draw a button and its text
    fill = (38, 44, 80) if pressed else (24, 28, 56)

    pygame.draw.rect(screen, fill, rect, border_radius=14)
    pygame.draw.rect(screen, PANEL_BORDER, rect, 2, border_radius=14)

    txt = _cached_text(layout, font, label, TEXT_COLOR)
    screen.blit(txt, txt.get_rect(center=rect.center))


def draw_arrow_button(screen, rect, direction, enabled):
    # draw a small up or down button
    fill = (38, 46, 88) if enabled else (20, 22, 42)
    pygame.draw.rect(screen, fill, rect, border_radius=8)

    pygame.draw.rect(
        screen,
        PANEL_BORDER if enabled else (70, 75, 105),
        rect,
        1,
        border_radius=8
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
    """
    Draw a line the player still needs to complete.
    """
    pygame.draw.line(screen, GUIDE_LINE_GLOW, p1, p2, 7)
    pygame.draw.line(screen, GUIDE_LINE_MID,  p1, p2, 4)
    pygame.draw.line(screen, GUIDE_LINE_CORE, p1, p2, 2)
    pygame.draw.aaline(screen, GUIDE_LINE_CORE, p1, p2)


def _draw_completed_edge(screen, p1, p2):
    """
    Draw a finished line with a bright glow.
    """
    pygame.draw.line(screen, EDGE_DONE_GLOW, p1, p2, 9)
    pygame.draw.line(screen, EDGE_DONE_MID,  p1, p2, 5)
    pygame.draw.line(screen, EDGE_DONE_CORE, p1, p2, 2)
    pygame.draw.aaline(screen, EDGE_DONE_CORE, p1, p2)


def _draw_drag_line(screen, p1, p2):
    # draw the moving line while the player drags
    pygame.draw.line(screen, DRAG_LINE_GLOW, p1, p2, 6)
    pygame.draw.line(screen, DRAG_LINE_CORE, p1, p2, 2)
    pygame.draw.aaline(screen, DRAG_LINE_CORE, p1, p2)


# -------------------------------
# left side panel
# -------------------------------
def draw_left_panel(screen, layout, state):
    lp = layout.left_panel
    panel = layout.panel_surfaces.get('left')

    # draw panel background
    if panel:
        screen.blit(panel, lp.topleft)

    x = layout.list_x
    y = lp.y + int(lp.height * 0.04)
    mw = layout.list_mw

    _draw_text(screen, layout, 'Constellation', layout.font_xs, ACCENT, x, y)
    y += layout.font_xs.get_linesize()

    _draw_text(screen, layout, 'Explorer', layout.font_xl, TEXT_COLOR, x, y)
    y += layout.font_xl.get_linesize() + int(lp.height * 0.03)

    # up button
    arrow_h = max(22, int(lp.height * 0.04))
    arrow_w = int(lp.width * 0.30)
    arrow_x = x + (mw - arrow_w) // 2

    state._scroll_up_rect = pygame.Rect(arrow_x, y, arrow_w, arrow_h)
    draw_arrow_button(screen, state._scroll_up_rect, 'up', state.can_scroll_up)
    y += arrow_h + 4

    # list of constellations
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
            x + 10, y + (row_h - layout.font_sm.get_height()) // 2
        )

        y += row_h + 2

    # down button
    y += 2
    state._scroll_down_rect = pygame.Rect(arrow_x, y, arrow_w, arrow_h)
    draw_arrow_button(
        screen, state._scroll_down_rect, 'down', state.can_scroll_down
    )
    y += arrow_h + int(lp.height * 0.03)

    # status text
    _draw_text(screen, layout, 'Status', layout.font_md, TEXT_COLOR, x, y)
    y += layout.font_md.get_linesize()

    for line in _cached_wrap(layout, state.status, layout.font_xs, mw)[:3]:
        _draw_text(screen, layout, line, layout.font_xs, MUTED_TEXT, x, y)
        y += layout.font_xs.get_linesize()

    # clear button
    draw_button(screen, layout, layout.clear_btn, 'Clear', layout.font_md)


# -------------------------------
# center panel
# -------------------------------
def draw_center_panel(screen, layout, state):
    co = layout.center_outer
    cs = layout.center_stage

    # draw panel background
    panel = layout.panel_surfaces.get('center')
    if panel:
        screen.blit(panel, co.topleft)

    if layout.stage_bg_surf:
        screen.blit(layout.stage_bg_surf, cs.topleft)

    _draw_text(screen, layout, 'Draw Zone', layout.font_sm, ACCENT,
               co.x + 18, co.y + 14)

    c = state.constellation
    if not c:
        msg = 'Select a constellation from the list to begin.'
        for i, line in enumerate(_cached_wrap(layout, msg, layout.font_sm,
                                              int(cs.width * 0.8))):
            _draw_text(
                screen, layout, line, layout.font_sm, MUTED_TEXT,
                cs.x + int(cs.width * 0.1),
                cs.y + cs.height // 2 - 20 + i * 24
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

    # draw finished lines
    for (a, b) in state.drawn_edges:
        if a < len(pts) and b < len(pts):
            _draw_completed_edge(screen, pts[a], pts[b])

    # draw live drag line
    if (
        state.last_visited_idx is not None
        and state.drag_pos
        and state.last_visited_idx < len(pts)
    ):
        _draw_drag_line(screen, pts[state.last_visited_idx], state.drag_pos)

    # draw all stars
    for i, item in enumerate(c['display_stars']):
        star = state.data.get_star(item['name'])
        is_sel = (
            state.selected_star and star and
            state.selected_star['name'] == star['name']
        )
        is_trail_head = (state.last_visited_idx == i)
        shine = state.shine_level(i)
        radius = _radius_for_magnitude(state.star_magnitude(i))

        # get the star color
        core_color = state.data.get_star_color(item['name'])

        draw_star(
            screen, layout, pts[i][0], pts[i][1], radius,
            selected=(is_sel or is_trail_head),
            shine=shine,
            core_color=core_color,
        )

    # show progress
    done = len(state.drawn_edges)
    total = len(required)

    _draw_text(screen, layout, f'{done}/{total}', layout.font_sm, ACCENT,
               co.right - 70, co.y + 14)

    # show finish flash
    if state.completed and layout.completion_flash:
        screen.blit(layout.completion_flash, cs.topleft)


# -------------------------------
# right side panel
# -------------------------------
def draw_right_panel(screen, layout, state):
    rp = layout.right_panel
    panel = layout.panel_surfaces.get('right')

    # draw panel background
    if panel:
        screen.blit(panel, rp.topleft)

    x = rp.x + int(rp.width * 0.08)
    y = rp.y + int(rp.height * 0.06)
    mw = int(rp.width * 0.82)

    c = state.constellation

    if not c:
        _draw_text(screen, layout, 'Details', layout.font_lg, TEXT_COLOR, x, y)
        y += layout.font_lg.get_linesize() + int(rp.height * 0.02)

        msg = (
            'Select a constellation from the list, then sweep across '
            'its stars to connect them.'
        )

        for line in _cached_wrap(layout, msg, layout.font_sm, mw)[:6]:
            _draw_text(screen, layout, line, layout.font_sm, MUTED_TEXT, x, y)
            y += layout.font_sm.get_linesize()

        return

    # constellation name
    _draw_text(screen, layout, c['name'], layout.font_xl, TEXT_COLOR, x, y)
    y += layout.font_xl.get_linesize()

    # small subtitle
    _draw_text(screen, layout, c.get('subtitle', ''),
               layout.font_md, ACCENT, x, y)
    y += layout.font_md.get_linesize() + int(rp.height * 0.03)

   
# best viewing months
    best_viewing_text = f'Best viewing — {OBSERVER_LOCATION}'

    for line in _cached_wrap(layout, best_viewing_text, layout.font_xs, mw)[:2]:
        _draw_text(screen, layout, line, layout.font_xs, MUTED_TEXT, x, y)
        y += layout.font_xs.get_linesize()

    for line in _cached_wrap(layout, c.get('best_months', '?'),
                             layout.font_md, mw)[:2]:
        _draw_text(screen, layout, line, layout.font_md, SUCCESS, x, y)
        y += layout.font_md.get_linesize()

    y += int(rp.height * 0.025)

    _draw_text(screen, layout, 'About', layout.font_md, TEXT_COLOR, x, y)
    y += layout.font_md.get_linesize()

    reserved = layout.font_sm.get_linesize() * 2 + int(rp.height * 0.04)
    avail = max(0, rp.bottom - y - reserved)
    max_lines = max(2, min(12, avail // max(1, layout.font_sm.get_linesize())))

    # description text
    for line in _cached_wrap(layout, c.get('description', ''),
                             layout.font_sm, mw)[:max_lines]:
        _draw_text(screen, layout, line, layout.font_sm, MUTED_TEXT, x, y)
        y += layout.font_sm.get_linesize()

    y += int(rp.height * 0.02)

    n_stars = len(c.get('display_stars', []))
    n_edges = len(state.required_edges())

    _draw_text(screen, layout, f'{n_stars} stars · {n_edges} edges',
               layout.font_sm, ACCENT_SOFT, x, y)
    y += layout.font_sm.get_linesize() + int(rp.height * 0.02)

    # progress message
    if state.completed:
        _draw_text(screen, layout, 'Tap a star for details.', layout.font_sm,
                   SUCCESS, x, y)
    elif state.drawn_edges:
        remaining = n_edges - len(state.drawn_edges)
        _draw_text(screen, layout, f'{remaining} edges remaining',
                   layout.font_sm, ACCENT, x, y)


# -------------------------------
# bottom panel
# -------------------------------
def draw_bottom_panel(screen, layout, state):
    bp = layout.bottom_panel
    panel = layout.panel_surfaces.get('bottom')

    # draw panel background
    if panel:
        screen.blit(panel, bp.topleft)

    x = bp.x + int(bp.width * 0.04)
    y_title = bp.y + int(bp.height * 0.12)

    if not state.completed or not state.selected_star:
        _draw_text(screen, layout, 'Star Details', layout.font_md,
                   TEXT_COLOR, x, y_title)

        y = y_title + layout.font_md.get_linesize() + int(bp.height * 0.03)

        if state.completed:
            msg = 'Constellation complete! Tap any star above to see its details here.'
        elif state.constellation:
            msg = 'Sweep across the stars to connect them, then tap one for details.'
        else:
            msg = 'Select a constellation to get started.'

        for line in _cached_wrap(layout, msg, layout.font_sm,
                                 int(bp.width * 0.90))[:3]:
            _draw_text(screen, layout, line, layout.font_sm, MUTED_TEXT, x, y)
            y += layout.font_sm.get_linesize()

        return

    star = state.selected_star
    c = state.constellation

    # small map area
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

        # fit the star points into the small map
        for px, py in pts:
            nx = (px - min_x) / rw
            ny = (py - min_y) / rh
            mapped.append((
                strip_x + pad_x + int(nx * usable_w),
                strip_y + pad_y + int(ny * usable_h)
            ))

        # draw finished lines in the mini map
        for (a, b) in state.drawn_edges:
            if a < len(mapped) and b < len(mapped):
                pygame.draw.line(screen, EDGE_DONE_MID,
                                 mapped[a], mapped[b], 2)
                pygame.draw.aaline(screen, EDGE_DONE_CORE,
                                   mapped[a], mapped[b])

        # draw stars in the mini map
        for i, item in enumerate(c['display_stars']):
            is_sel = (star and item['name'] == star['name'])
            core_color = state.data.get_star_color(item['name'])
            draw_star(screen, layout, mapped[i][0], mapped[i][1], 4,
                      selected=is_sel, core_color=core_color)

    # star info section
    info_x = strip_rect.right + int(bp.width * 0.03)
    y = y_title

    _draw_text(screen, layout, star.get('name', '?'), layout.font_lg,
               TEXT_COLOR, info_x, y)
    y += layout.font_lg.get_linesize() + int(bp.height * 0.02)

    labels_values = [
        ('Constellation', star.get('constellation', '?')),
        ('Magnitude',     f"{star.get('magnitude', '?')}"),
        ('Distance',      f"{star.get('distance_ly', '?')} light-years"),
        ('Spectral type', star.get('spectral_type', '?')),
    ]

    label_w = max(layout.font_xs.size(lbl)[0] for lbl, _ in labels_values) + 14

    # draw label and value lines
    for lbl, val in labels_values:
        _draw_text(screen, layout, lbl, layout.font_xs, MUTED_TEXT, info_x, y)
        _draw_text(screen, layout, val, layout.font_xs, TEXT_COLOR,
                   info_x + label_w, y)
        y += layout.font_xs.get_linesize() + 2

    y += 4

    desc_w = bp.right - info_x - int(bp.width * 0.04)

    # draw star description
    if desc_w > 60:
        for line in _cached_wrap(layout, star.get('description', ''),
                                 layout.font_xs, desc_w)[:3]:
            _draw_text(screen, layout, line, layout.font_xs, MUTED_TEXT,
                       info_x, y)
            y += layout.font_xs.get_linesize()


# -------------------------------
# draw the full screen
# -------------------------------
def render_frame(screen, layout, state):
    # draw background
    if layout.background:
        screen.blit(layout.background, (0, 0))
    else:
        screen.fill((6, 7, 18))

    # draw each section
    draw_left_panel(screen, layout, state)
    draw_center_panel(screen, layout, state)
    draw_right_panel(screen, layout, state)
    draw_bottom_panel(screen, layout, state)

    # show everything on screen
    pygame.display.flip()