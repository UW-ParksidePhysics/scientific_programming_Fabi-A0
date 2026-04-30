"""
main.py
This file runs the whole program.

It:
- starts the game
- checks for clicks, taps, and keys
- updates the screen

This version can run in a browser with pygbag
"""

import asyncio
import sys
import pygame

from config import FPS, CONSTELLATIONS_PATH, STARS_PATH
from data_manager import DataManager
from layout import Layout
from game_state import GameState
from renderer import render_frame


# -------------------------------
# small helper parts
# -------------------------------

def finger_to_screen(screen, fx, fy):
    # Change touch values into real screen positions
    w, h = screen.get_size()
    return int(fx * w), int(fy * h)


def handle_press(layout, state, pos):
    # Check what the player clicked or tapped
    # Return True if something happened

    # clear button
    if layout.clear_btn.collidepoint(pos):
        state.clear()
        return True

    # scroll up button
    if state._scroll_up_rect.collidepoint(pos):
        state.scroll_up()
        return True

    # scroll down button
    if state._scroll_down_rect.collidepoint(pos):
        state.scroll_down()
        return True

    # list of constellations
    for rect, name in state._list_rects:
        if rect.collidepoint(pos):
            state.select_constellation(name)
            return True

    # main drawing area
    if layout.center_stage.collidepoint(pos) and state.constellation:
        idx = state.hit_star(pos, layout.center_stage)

        if idx is not None:
            if state.completed:
                # if finished, show star details
                state.tap_star_info(idx)
            else:
                # if not finished, start drawing from this star
                state.begin_drag(idx)
            return True

    return False


def handle_release(state, pos):
    # Stop dragging when the player lets go
    if state.drag_from_idx is not None:
        state.end_drag()
        return True
    return False


# -------------------------------
# main game loop
# -------------------------------

async def main():
    # Start pygame
    pygame.init()

    # Try to make the window fill most of the screen at the start
    try:
        info = pygame.display.Info()
        if info.current_w >= 800 and info.current_h >= 600:
            default_w = int(info.current_w * 0.95)
            default_h = int(info.current_h * 0.90)
        else:
            default_w, default_h = 1400, 800
    except Exception:
        default_w, default_h = 1400, 800

    # Make the game window
    screen = pygame.display.set_mode((default_w, default_h), pygame.RESIZABLE)
    pygame.display.set_caption('Constellation Explorer')
    clock = pygame.time.Clock()

    # Keep track of fullscreen on or off
    fullscreen = False
    windowed_size = (default_w, default_h)

    # Load game data and setup
    data = DataManager(CONSTELLATIONS_PATH, STARS_PATH)
    layout = Layout()
    state = GameState(data)

    layout.update(screen, *screen.get_size())

    # Click areas used during drawing
    state._list_rects = []
    state._scroll_up_rect = pygame.Rect(0, 0, 0, 0)
    state._scroll_down_rect = pygame.Rect(0, 0, 0, 0)

    running = True
    mouse_dragging = False
    dirty = True   # draw the first screen right away

    # On web, this helps check if the browser size changed
    _IS_WEB = (sys.platform == 'emscripten')
    _resize_check_counter = 0

    while running:
        # Keep the game running at the chosen FPS
        clock.tick(FPS)

        # On web, check now and then if the screen size changed
        if _IS_WEB:
            _resize_check_counter += 1
            if _resize_check_counter >= 15:
                _resize_check_counter = 0
                try:
                    import platform as _web_platform
                    cw = int(_web_platform.window.innerWidth)
                    ch = int(_web_platform.window.innerHeight)
                    sw, sh = screen.get_size()

                    if cw > 0 and ch > 0 and (cw, ch) != (sw, sh):
                        screen = pygame.display.set_mode(
                            (cw, ch), pygame.RESIZABLE
                        )
                        layout.update(screen, cw, ch)
                        dirty = True
                except Exception:
                    pass

        for event in pygame.event.get():

            # Close window
            if event.type == pygame.QUIT:
                running = False

            # Resize window
            elif event.type == pygame.VIDEORESIZE:
                # Do not let the window get too small
                w = max(480, event.w)
                h = max(640, event.h)
                screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
                layout.update(screen, w, h)
                dirty = True

            # Keyboard controls
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    # clear current drawing
                    state.clear()
                    dirty = True

                elif event.key == pygame.K_ESCAPE:
                    # reset everything
                    state.full_reset()
                    dirty = True

                elif event.key == pygame.K_F11:
                    # switch fullscreen on or off
                    fullscreen = not fullscreen

                    if fullscreen:
                        windowed_size = screen.get_size()
                        screen = pygame.display.set_mode(
                            (0, 0), pygame.FULLSCREEN
                        )
                    else:
                        screen = pygame.display.set_mode(
                            windowed_size, pygame.RESIZABLE
                        )

                    layout.update(screen, *screen.get_size())
                    dirty = True

            # Mouse pressed
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_dragging = True
                if handle_press(layout, state, event.pos):
                    dirty = True

            # Mouse moving
            elif event.type == pygame.MOUSEMOTION:
                if mouse_dragging and state.drag_from_idx is not None:
                    # Keep updating the drawing line
                    state.update_drag(event.pos, layout.center_stage)
                    dirty = True

                elif layout.left_panel.collidepoint(event.pos):
                    # Redraw if mouse is over the left panel
                    dirty = True

            # Mouse released
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                mouse_dragging = False
                if handle_release(state, event.pos):
                    dirty = True

            # Touch started
            elif event.type == pygame.FINGERDOWN:
                if handle_press(
                    layout,
                    state,
                    finger_to_screen(screen, event.x, event.y)
                ):
                    dirty = True

            # Touch moving
            elif event.type == pygame.FINGERMOTION:
                if state.drag_from_idx is not None:
                    state.update_drag(
                        finger_to_screen(screen, event.x, event.y),
                        layout.center_stage
                    )
                    dirty = True

            # Touch ended
            elif event.type == pygame.FINGERUP:
                if handle_release(
                    state,
                    finger_to_screen(screen, event.x, event.y)
                ):
                    dirty = True

            # Mouse wheel scroll
            elif event.type == pygame.MOUSEWHEEL:
                if layout.left_panel.collidepoint(pygame.mouse.get_pos()):
                    if event.y > 0:
                        state.scroll_up()
                    elif event.y < 0:
                        state.scroll_down()
                    dirty = True

        # Keep updating while dragging or while star glow is still active
        if state.drag_from_idx is not None or state.has_active_shines():
            dirty = True

        # Only redraw when needed
        if dirty:
            render_frame(screen, layout, state)
            dirty = False

        # Very important for browser version so it does not freeze
        await asyncio.sleep(0)

    # Close pygame cleanly
    pygame.quit()


# Start the program
asyncio.run(main())