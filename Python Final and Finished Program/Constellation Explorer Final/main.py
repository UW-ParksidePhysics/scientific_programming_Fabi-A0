"""Run the Constellation Explorer game loop on desktop and in pygbag."""

__author__ = "Fabian Anguiano"

import asyncio
import sys

import pygame

from config import (
    FPS, CONSTELLATIONS_PATH, STARS_PATH,
    EDITOR_ACCESS_CODE, EDITOR_NO_CODE,
)
from save_manager import SaveManager
from data_manager import DataManager
from layout import Layout
from game_state import GameState
from renderer import render_frame, invalidate_text_caches
from editor import EditorApp


# -------------------------------
# small helpers
# -------------------------------
def finger_to_screen(screen, fx, fy):
    """Convert pygame finger-event coordinates into pixel positions.

    Parameters:
        screen: pygame.Surface
            The current display surface (used for its size).
        fx: float
            Normalized x coordinate from a touch event.
        fy: float
            Normalized y coordinate from a touch event.
    Returns:
        position: tuple of int
            ``(x, y)`` pixel coordinates on ``screen``.
    """
    w, h = screen.get_size()
    return int(fx * w), int(fy * h)


def handle_press(layout, state, pos):
    """Route a press or tap to the right click target.

    Parameters:
        layout: Layout
            The current layout.
        state: GameState
            The active game state; mutated in place.
        pos: tuple of int
            Pixel position of the press.
    Returns:
        consumed: bool
            ``True`` when the press triggered an action, ``False``
            when it landed on no target.
    """
    if layout.clear_btn.collidepoint(pos):
        state.clear()
        return True

    if state._scroll_up_rect.collidepoint(pos):
        state.scroll_up()
        return True

    if state._scroll_down_rect.collidepoint(pos):
        state.scroll_down()
        return True

    for rect, name in state._list_rects:
        if rect.collidepoint(pos):
            state.select_constellation(name)
            return True

    if layout.center_stage.collidepoint(pos) and state.constellation:
        idx = state.hit_star(pos, layout.center_stage)
        if idx is not None:
            if state.completed:
                state.tap_star_info(idx)
            else:
                state.begin_drag(idx)
            return True

    return False


def handle_release(state, layout, pos):
    """End an in-progress drag, snapping to a star at the release point.

    If the pointer is released directly over a star, that index is
    passed to :meth:`GameState.end_drag` so a final edge can be
    committed even when no motion event fired close enough to trigger
    a mid-drag snap.

    Parameters:
        state: GameState
            The active game state; mutated in place.
        layout: Layout
            Provides ``center_stage`` for the hit test.
        pos: tuple of int
            Pixel position of the pointer release.
    Returns:
        consumed: bool
            ``True`` when a drag was ended, ``False`` otherwise.
    """
    if state.drag_from_idx is not None:
        star_idx = state.hit_star(pos, layout.center_stage)
        state.end_drag(star_idx)
        return True
    return False


# -------------------------------
# unlock prompt (hidden editor access)
# -------------------------------
class UnlockPrompt:
    """A modal that asks the user for the editor access code.

    The modal is rendered on top of the game without flipping the
    display, then receives keyboard events directly. Each call to
    :meth:`handle_event` returns ``'unlock'``, ``'cancel'``, or
    ``None``, allowing the main loop to advance between modes.
    """

    def __init__(self):
        """Create an empty unlock prompt with no entered text."""
        self.text = ''
        self.message = 'Enter editor access code:'
        self.is_error = False
        self.cursor_blink = 0

    def handle_event(self, event):
        """Process one keyboard event and return an action token.

        Parameters:
            event: pygame.event.Event
                A single event from ``pygame.event.get``.
        Returns:
            action: str or None
                ``'unlock'`` if the entered code matched,
                ``'cancel'`` if Escape was pressed, otherwise
                ``None``.
        """
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_ESCAPE:
            return 'cancel'

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.text == EDITOR_ACCESS_CODE:
                return 'unlock'
            self.text = ''
            self.message = (
                'Incorrect — try again or press Esc to cancel.'
            )
            self.is_error = True
            return None

        if event.key == pygame.K_BACKSPACE:
            self.text = self.text[:-1]
            return None

        if event.unicode and event.unicode.isprintable():
            self.text += event.unicode
            self.is_error = False
            return None

        return None

    def render(self, screen, w, h):
        """Draw the modal on top of the existing game frame.

        Parameters:
            screen: pygame.Surface
                Destination surface.
            w: int
                Window width in pixels.
            h: int
                Window height in pixels.
        """
        # darken everything behind the modal
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        # modal box
        mw, mh = 460, 220
        mrect = pygame.Rect((w - mw) // 2, (h - mh) // 2, mw, mh)
        pygame.draw.rect(screen, (20, 24, 50), mrect, border_radius=14)
        pygame.draw.rect(
            screen, (200, 220, 255), mrect, 2, border_radius=14,
        )

        title_font = pygame.font.SysFont('arial', 22, bold=True)
        text_font = pygame.font.SysFont('arial', 16)
        small_font = pygame.font.SysFont('arial', 13)

        pad = 22
        x = mrect.x + pad
        y = mrect.y + pad

        title = title_font.render(
            'Editor Access', True, (220, 230, 255),
        )
        screen.blit(title, (x, y))
        y += title.get_height() + 6

        msg_color = (255, 180, 180) if self.is_error else (200, 210, 230)
        msg = text_font.render(self.message, True, msg_color)
        screen.blit(msg, (x, y))
        y += msg.get_height() + 14

        # input field — entered text is masked with dots
        input_rect = pygame.Rect(x, y, mw - pad * 2, 38)
        pygame.draw.rect(
            screen, (36, 44, 86), input_rect, border_radius=6,
        )
        pygame.draw.rect(
            screen, (200, 220, 255), input_rect, 2, border_radius=6,
        )

        dots = '•' * len(self.text)
        dot_surf = text_font.render(dots, True, (250, 250, 255))
        screen.blit(
            dot_surf,
            (
                input_rect.x + 10,
                input_rect.y
                + (input_rect.height - dot_surf.get_height()) // 2,
            ),
        )

        # blinking caret
        if (pygame.time.get_ticks() // 500) % 2 == 0:
            cx = input_rect.x + 10 + dot_surf.get_width() + 1
            cy1 = input_rect.y + 8
            cy2 = input_rect.bottom - 8
            pygame.draw.line(
                screen, (250, 250, 255), (cx, cy1), (cx, cy2), 2,
            )

        y = input_rect.bottom + 12

        hint = small_font.render(
            'Enter to confirm · Esc to cancel',
            True, (180, 190, 220),
        )
        screen.blit(hint, (x, y))


# -------------------------------
# main game loop
# -------------------------------
async def main():
    """Initialise pygame and run the main event/render loop.

    The loop is an ``async`` function because the pygbag/browser
    build needs ``await asyncio.sleep(0)`` once per frame to yield
    back to the event loop. On desktop it behaves like an ordinary
    blocking loop.
    """
    pygame.init()

    # size the initial window to most of the desktop
    try:
        info = pygame.display.Info()
        if info.current_w >= 800 and info.current_h >= 600:
            default_w = int(info.current_w * 0.95)
            default_h = int(info.current_h * 0.90)
        else:
            default_w, default_h = 1400, 800
    except Exception:
        default_w, default_h = 1400, 800

    screen = pygame.display.set_mode(
        (default_w, default_h), pygame.RESIZABLE,
    )
    pygame.display.set_caption('Constellation Explorer')
    clock = pygame.time.Clock()

    # track fullscreen state
    fullscreen = False
    windowed_size = (default_w, default_h)

    # platform-aware save manager drives both load and save
    save_manager = SaveManager(CONSTELLATIONS_PATH, STARS_PATH)
    data = DataManager(
        CONSTELLATIONS_PATH, STARS_PATH,
        save_manager=save_manager,
    )

    layout = Layout()
    state = GameState(data)
    layout.update(screen, *screen.get_size())

    # click areas updated during drawing
    state._list_rects = []
    state._scroll_up_rect = pygame.Rect(0, 0, 0, 0)
    state._scroll_down_rect = pygame.Rect(0, 0, 0, 0)

    # mode tracking:
    #   'game'    -> normal play
    #   'unlock'  -> editor access prompt over the game
    #   'editor'  -> embedded editor running
    mode = 'game'

    # once unlocked in this session, do not prompt again until restart
    session_unlocked = bool(EDITOR_NO_CODE)

    unlock_prompt = None
    editor_app = None

    running = True
    mouse_dragging = False
    dirty = True

    is_web = (sys.platform == 'emscripten')
    resize_check_counter = 0

    while running:
        clock.tick(FPS)

        # web build: poll the browser window size periodically
        if is_web:
            resize_check_counter += 1
            if resize_check_counter >= 15:
                resize_check_counter = 0
                try:
                    import platform as web_platform
                    cw = int(web_platform.window.innerWidth)
                    ch = int(web_platform.window.innerHeight)
                    sw, sh = screen.get_size()
                    if cw > 0 and ch > 0 and (cw, ch) != (sw, sh):
                        screen = pygame.display.set_mode(
                            (cw, ch), pygame.RESIZABLE,
                        )
                        layout.update(screen, cw, ch)
                        if editor_app is not None:
                            editor_app.on_resize(cw, ch)
                        dirty = True
                except Exception:
                    pass

        for event in pygame.event.get():
            # -------------------------------
            # always-handled events
            # -------------------------------
            if event.type == pygame.QUIT:
                running = False
                continue

            if event.type == pygame.VIDEORESIZE:
                w = max(480, event.w)
                h = max(640, event.h)
                screen = pygame.display.set_mode(
                    (w, h), pygame.RESIZABLE,
                )
                layout.update(screen, w, h)
                if editor_app is not None:
                    editor_app.on_resize(w, h)
                invalidate_text_caches()
                dirty = True
                continue

            # global toggle for the editor (Ctrl+Shift+E)
            if (event.type == pygame.KEYDOWN
                    and event.key == pygame.K_e
                    and (event.mod & pygame.KMOD_CTRL)
                    and (event.mod & pygame.KMOD_SHIFT)):
                if mode == 'game':
                    if session_unlocked:
                        # already unlocked this session — open directly
                        editor_app = EditorApp(
                            screen,
                            data.constellations,
                            data.stars,
                            save_manager,
                            embedded=True,
                        )
                        mode = 'editor'
                    else:
                        unlock_prompt = UnlockPrompt()
                        mode = 'unlock'
                    dirty = True
                    continue

                if mode == 'editor':
                    # exit back to the game
                    editor_app = None
                    mode = 'game'
                    data.refresh_caches()
                    invalidate_text_caches()
                    state.full_reset()
                    dirty = True
                    continue

                if mode == 'unlock':
                    # dismiss the prompt
                    unlock_prompt = None
                    mode = 'game'
                    dirty = True
                    continue

            # -------------------------------
            # editor mode
            # -------------------------------
            if mode == 'editor':
                if editor_app is not None:
                    editor_app.handle_event(event)
                    if editor_app.want_exit:
                        editor_app = None
                        mode = 'game'
                        data.refresh_caches()
                        invalidate_text_caches()
                        state.full_reset()
                        dirty = True
                continue

            # -------------------------------
            # unlock prompt mode
            # -------------------------------
            if mode == 'unlock':
                if unlock_prompt is not None:
                    result = unlock_prompt.handle_event(event)
                    if result == 'unlock':
                        session_unlocked = True
                        unlock_prompt = None
                        editor_app = EditorApp(
                            screen,
                            data.constellations,
                            data.stars,
                            save_manager,
                            embedded=True,
                        )
                        mode = 'editor'
                        dirty = True
                    elif result == 'cancel':
                        unlock_prompt = None
                        mode = 'game'
                        dirty = True
                continue

            # -------------------------------
            # normal game events
            # -------------------------------
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:
                    state.clear()
                    dirty = True
                elif event.key == pygame.K_ESCAPE:
                    state.full_reset()
                    dirty = True
                elif event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        windowed_size = screen.get_size()
                        screen = pygame.display.set_mode(
                            (0, 0), pygame.FULLSCREEN,
                        )
                    else:
                        screen = pygame.display.set_mode(
                            windowed_size, pygame.RESIZABLE,
                        )
                    layout.update(screen, *screen.get_size())
                    invalidate_text_caches()
                    dirty = True

            elif (event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1):
                mouse_dragging = True
                if handle_press(layout, state, event.pos):
                    dirty = True

            elif event.type == pygame.MOUSEMOTION:
                if mouse_dragging and state.drag_from_idx is not None:
                    state.update_drag(event.pos, layout.center_stage)
                    dirty = True
                elif layout.left_panel.collidepoint(event.pos):
                    dirty = True

            elif (event.type == pygame.MOUSEBUTTONUP
                    and event.button == 1):
                mouse_dragging = False
                if handle_release(state, layout, event.pos):
                    dirty = True

            elif event.type == pygame.FINGERDOWN:
                if handle_press(
                    layout, state,
                    finger_to_screen(screen, event.x, event.y),
                ):
                    dirty = True

            elif event.type == pygame.FINGERMOTION:
                if state.drag_from_idx is not None:
                    state.update_drag(
                        finger_to_screen(screen, event.x, event.y),
                        layout.center_stage,
                    )
                    dirty = True

            elif event.type == pygame.FINGERUP:
                if handle_release(
                    state, layout,
                    finger_to_screen(screen, event.x, event.y),
                ):
                    dirty = True

            elif event.type == pygame.MOUSEWHEEL:
                if layout.left_panel.collidepoint(
                        pygame.mouse.get_pos()):
                    if event.y > 0:
                        state.scroll_up()
                    elif event.y < 0:
                        state.scroll_down()
                    dirty = True

        # keep redrawing while dragging or while a star is still glowing
        if mode == 'game':
            if (state.drag_from_idx is not None
                    or state.has_active_shines()):
                dirty = True

        # -------------------------------
        # render
        # -------------------------------
        if mode == 'editor':
            if editor_app is not None:
                editor_app.render(screen)
            pygame.display.flip()

        elif mode == 'unlock':
            # draw the game behind the prompt (without flipping)
            render_frame(screen, layout, state, flip=False)
            if unlock_prompt is not None:
                unlock_prompt.render(screen, *screen.get_size())
            pygame.display.flip()

        else:  # game
            if dirty:
                render_frame(screen, layout, state)
                dirty = False

        await asyncio.sleep(0)

    pygame.quit()


if __name__ == '__main__':
    asyncio.run(main())
