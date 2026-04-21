"""
main.py
This is the main file that runs the program.
It handles the event loop, input, and drawing the screen.
"""

import pygame
from config import FPS, CONSTELLATIONS_PATH, STARS_PATH
from data_manager import DataManager
from layout import Layout
from game_state import GameState
from renderer import render_frame

pygame.init()

# -------------------------------
# setup
# -------------------------------
screen = pygame.display.set_mode((1400, 800), pygame.RESIZABLE)
pygame.display.set_caption('Constellation Explorer')
clock = pygame.time.Clock()

data = DataManager(CONSTELLATIONS_PATH, STARS_PATH)
layout = Layout()
state = GameState(data)

layout.update(screen, *screen.get_size())

# these are temporary rectangles used for clicking
state._list_rects = []
state._scroll_up_rect = pygame.Rect(0, 0, 0, 0)
state._scroll_down_rect = pygame.Rect(0, 0, 0, 0)


def finger_to_screen(fx, fy):
    # turn touch values into screen coordinates
    w, h = screen.get_size()
    return int(fx * w), int(fy * h)


def handle_press(pos):
    """Handle a click or tap."""
    # clear button
    if layout.clear_btn.collidepoint(pos):
        state.clear()
        return True

    # scroll buttons
    if state._scroll_up_rect.collidepoint(pos):
        state.scroll_up()
        return True

    if state._scroll_down_rect.collidepoint(pos):
        state.scroll_down()
        return True

    # constellation list
    for rect, name in state._list_rects:
        if rect.collidepoint(pos):
            state.select_constellation(name)
            return True

    # center area
    if layout.center_stage.collidepoint(pos) and state.constellation:
        idx = state.hit_star(pos, layout.center_stage)

        if idx is not None:
            if state.completed:
                state.tap_star_info(idx)
            else:
                state.begin_drag(idx)
            return True

    return False


def handle_release(pos):
    # stop dragging when mouse or finger is released
    if state.drag_from_idx is not None:
        state.end_drag()
        return True
    return False


# -------------------------------
# main loop
# -------------------------------
running = True
mouse_dragging = False
dirty = True   # draw the first frame

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.VIDEORESIZE:
            # keep the window from getting too small
            w = max(540, event.w)
            h = max(540, event.h)
            screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
            layout.update(screen, w, h)
            dirty = True

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                state.clear()
                dirty = True
            elif event.key == pygame.K_ESCAPE:
                state.full_reset()
                dirty = True

        # mouse events
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_dragging = True
            if handle_press(event.pos):
                dirty = True

        elif event.type == pygame.MOUSEMOTION:
            if mouse_dragging and state.drag_from_idx is not None:
                state.update_drag(event.pos, layout.center_stage)
                dirty = True
            elif layout.left_panel.collidepoint(event.pos):
                # redraw for hover effect
                dirty = True

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_dragging = False
            if handle_release(event.pos):
                dirty = True

        # touch events
        elif event.type == pygame.FINGERDOWN:
            if handle_press(finger_to_screen(event.x, event.y)):
                dirty = True

        elif event.type == pygame.FINGERMOTION:
            if state.drag_from_idx is not None:
                state.update_drag(
                    finger_to_screen(event.x, event.y),
                    layout.center_stage
                )
                dirty = True

        elif event.type == pygame.FINGERUP:
            if handle_release(finger_to_screen(event.x, event.y)):
                dirty = True

        # mouse wheel for scrolling the list
        elif event.type == pygame.MOUSEWHEEL:
            if layout.left_panel.collidepoint(pygame.mouse.get_pos()):
                if event.y > 0:
                    state.scroll_up()
                elif event.y < 0:
                    state.scroll_down()
                dirty = True

    # keep drawing while dragging or while stars are still glowing
    if state.drag_from_idx is not None or state.has_active_shines():
        dirty = True

    if dirty:
        render_frame(screen, layout, state)
        dirty = False

pygame.quit()