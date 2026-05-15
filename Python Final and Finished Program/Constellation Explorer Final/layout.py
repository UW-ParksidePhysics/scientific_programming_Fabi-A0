"""Compute screen layout, fonts, and cached surfaces for the game."""

__author__ = "Fabian Anguiano"

import os
import sys

import pygame

from config import (
    BG_COLOR, BACKGROUND_PATH,
    PANEL_FILL, PANEL_BORDER, HIGHLIGHT_BG, SELECTED_BG,
    STAR_COLOR, SUCCESS, STAR_TIERS,
    SHINE_CORE, SHINE_GLOW,
)


# number of glow frames in a shine animation
SHINE_FRAME_COUNT = 6

# radii used in the program, derived from STAR_TIERS
STAR_RADII = tuple(t[1] for t in STAR_TIERS)

# radius used for stars drawn in the mini map
MINIMAP_RADIUS = 4

# threshold above which a "tall" screen counts as portrait
PORTRAIT_ASPECT = 1.05


def _allow_portrait():
    """Decide whether portrait layout is available on this platform.

    Returns:
        allowed: bool
            ``True`` on Android and iOS, where tall layouts are
            useful, and ``False`` on desktop and inside a browser
            (where the game always uses landscape).
    """
    if sys.platform == 'emscripten':
        return False
    if 'ANDROID_ARGUMENT' in os.environ:
        return True
    if sys.platform == 'ios':
        return True
    return False


ALLOW_PORTRAIT = _allow_portrait()


# -------------------------------
# small color helpers
# -------------------------------
def _lighten(rgb, amount):
    """Brighten an RGB color toward white by a given fraction.

    Parameters:
        rgb: tuple of int
            The base color. Only the first three channels are used.
        amount: float
            How far to push toward white, in the ``[0, 1]`` range.
    Returns:
        color: tuple of int, shape (3,)
            The lightened RGB color, clamped to ``[0, 255]``.
    """
    r, g, b = rgb[:3]
    return (
        min(255, int(r + (255 - r) * amount)),
        min(255, int(g + (255 - g) * amount)),
        min(255, int(b + (255 - b) * amount)),
    )


def _glow_color(core_rgb):
    """Derive a soft glow color from a core star color.

    Parameters:
        core_rgb: tuple of int
            The star's core RGB color.
    Returns:
        color: tuple of int, shape (3,)
            A lighter color suitable for the surrounding glow.
    """
    return _lighten(core_rgb, 0.35)


class Layout:
    """Hold all on-screen rectangles, fonts, and pre-rendered surfaces.

    The Layout object is rebuilt whenever the window size changes.
    It chooses between a wide landscape arrangement and a tall
    portrait arrangement (mobile only) and pre-renders panel
    backgrounds, list row highlights, and star sprites so per-frame
    drawing stays fast.
    """

    def __init__(self):
        """Create an empty layout with all rectangles at the origin."""
        # main screen sections
        self.left_panel = pygame.Rect(0, 0, 0, 0)
        self.center_outer = pygame.Rect(0, 0, 0, 0)
        self.center_stage = pygame.Rect(0, 0, 0, 0)
        self.right_panel = pygame.Rect(0, 0, 0, 0)
        self.bottom_panel = pygame.Rect(0, 0, 0, 0)
        self.clear_btn = pygame.Rect(0, 0, 0, 0)
        self.scroll_up = pygame.Rect(0, 0, 0, 0)
        self.scroll_down = pygame.Rect(0, 0, 0, 0)

        self.is_portrait = False

        # fonts (assigned in _update_fonts)
        self.font_xs = None
        self.font_sm = None
        self.font_md = None
        self.font_lg = None
        self.font_xl = None

        # background image (or generated starfield) for the window
        self.background = None

        # pre-rendered surfaces
        self.panel_surfaces = {}
        self.row_hover_surf = None
        self.row_selected_surf = None
        self.stage_bg_surf = None
        self.completion_flash = None

        # default star images keyed by (radius, selected)
        self.star_sprites = {}

        # star image cache keyed by (radius, color, selected)
        self._star_sprite_cache = {}

        # cached shine frames keyed by (radius, frame)
        self.shine_sprites = {}

        # list layout values used by the renderer
        self.list_x = 0
        self.list_mw = 0
        self.list_row_h = 0

        # cache the last screen size so we skip needless rebuilds
        self._last_size = (0, 0)
        self._bg_source_size = (0, 0)

        self.version = 0

    # -------------------------------
    # main update
    # -------------------------------
    def update(self, screen, w, h):
        """Rebuild every layout value for a new screen size.

        Parameters:
            screen: pygame.Surface
                The current display surface (not used directly here
                but kept for API compatibility).
            w: int
                New window width in pixels.
            h: int
                New window height in pixels.
        """
        # skip work if the screen size did not change
        if (w, h) == self._last_size and self.version > 0:
            return

        self._last_size = (w, h)

        self._update_fonts(w, h)

        # outer spacing around the four panels
        pad = max(6, int(min(w, h) * 0.022))
        gap = max(4, int(min(w, h) * 0.016))

        content = pygame.Rect(
            pad, pad,
            max(w - 2 * pad, 1),
            max(h - 2 * pad, 1),
        )

        # choose portrait or landscape based on aspect ratio
        if ALLOW_PORTRAIT:
            aspect = content.width / max(content.height, 1)
            self.is_portrait = aspect < PORTRAIT_ASPECT
        else:
            self.is_portrait = False

        if self.is_portrait:
            self._layout_portrait(content, gap)
        else:
            self._layout_landscape(content, gap)

        self._compute_list_and_button()

        # rebuild pre-rendered surfaces after resize
        self._load_background(w, h)
        self._build_panel_surfaces()
        self._build_row_highlights()
        self._build_stage_bg()
        self._build_star_sprites()

        self.version += 1

    # -------------------------------
    # screen layout
    # -------------------------------
    def _layout_landscape(self, content, gap):
        """Compute panel rectangles for a wide window.

        Parameters:
            content: pygame.Rect
                The area inside the outer padding.
            gap: int
                Pixel gap between panels.
        """
        left_w = max(220, int(content.width * 0.19))
        right_w = max(240, int(content.width * 0.21))
        middle_w = content.width - left_w - right_w - gap * 2

        top_h = int(
            content.height * (0.72 if content.height > 700 else 0.78)
        )
        bottom_h = content.height - top_h - gap

        self.left_panel = pygame.Rect(
            content.x, content.y, left_w, top_h
        )
        self.center_outer = pygame.Rect(
            self.left_panel.right + gap, content.y, middle_w, top_h
        )
        self.right_panel = pygame.Rect(
            self.center_outer.right + gap, content.y, right_w, top_h
        )
        self.bottom_panel = pygame.Rect(
            self.left_panel.right + gap,
            self.center_outer.bottom + gap,
            middle_w + gap + right_w, bottom_h,
        )

        self.center_stage = self._stage_inside(self.center_outer)

    def _layout_portrait(self, content, gap):
        """Compute panel rectangles for a tall window.

        Parameters:
            content: pygame.Rect
                The area inside the outer padding.
            gap: int
                Pixel gap between panels.
        """
        row1_h = int(content.height * 0.58)
        row2_h = int(content.height * 0.22)
        row3_h = content.height - row1_h - row2_h - 2 * gap

        left_w = max(
            int(content.width * 0.34),
            min(240, content.width // 2),
        )
        middle_w = content.width - left_w - gap

        self.left_panel = pygame.Rect(
            content.x, content.y, left_w, row1_h
        )
        self.center_outer = pygame.Rect(
            self.left_panel.right + gap, content.y, middle_w, row1_h
        )
        self.right_panel = pygame.Rect(
            content.x, self.left_panel.bottom + gap,
            content.width, row2_h,
        )
        self.bottom_panel = pygame.Rect(
            content.x, self.right_panel.bottom + gap,
            content.width, row3_h,
        )

        self.center_stage = self._stage_inside(self.center_outer)

    def _stage_inside(self, outer):
        """Shrink the center panel into a draw area with a small margin.

        Parameters:
            outer: pygame.Rect
                The center panel rectangle.
        Returns:
            stage: pygame.Rect
                The interior draw area for stars and lines.
        """
        return outer.inflate(
            -int(outer.width * 0.06),
            -int(outer.height * 0.10),
        )

    def _compute_list_and_button(self):
        """Compute the constellation list and clear-button geometry."""
        bw = max(100, int(self.left_panel.width * 0.38))
        bh = max(34, int(self.left_panel.height * 0.07))

        self.clear_btn = pygame.Rect(
            self.left_panel.x + int(self.left_panel.width * 0.08),
            self.left_panel.bottom - bh
            - int(self.left_panel.height * 0.04),
            bw, bh,
        )

        self.list_x = (
            self.left_panel.x + int(self.left_panel.width * 0.08)
        )
        self.list_mw = int(self.left_panel.width * 0.84)
        self.list_row_h = max(26, int(self.left_panel.height * 0.065))

    # -------------------------------
    # fonts
    # -------------------------------
    def _update_fonts(self, w, h):
        """Resize the cached fonts to match the new window size.

        Parameters:
            w: int
                Window width in pixels.
            h: int
                Window height in pixels.
        """
        ref = max(640, int((w * h) ** 0.5))

        self.font_xs = pygame.font.SysFont(
            'arial', max(13, int(ref * 0.013))
        )
        self.font_sm = pygame.font.SysFont(
            'arial', max(15, int(ref * 0.016))
        )
        self.font_md = pygame.font.SysFont(
            'arial', max(19, int(ref * 0.021))
        )
        self.font_lg = pygame.font.SysFont(
            'arial', max(24, int(ref * 0.028))
        )
        self.font_xl = pygame.font.SysFont(
            'arial', max(30, int(ref * 0.041))
        )

    @staticmethod
    def _fit_rect(container, target_ratio):
        """Centre a rectangle of a chosen aspect inside a container.

        Parameters:
            container: pygame.Rect
                The bounding rectangle.
            target_ratio: float
                Desired width-to-height ratio of the inner rect.
        Returns:
            inner: pygame.Rect
                A rectangle of the target aspect, centered inside
                ``container``.
        """
        cur = container.width / max(container.height, 1)

        if cur > target_ratio:
            h = container.height
            w = int(h * target_ratio)
        else:
            w = container.width
            h = int(w / target_ratio)

        x = container.x + (container.width - w) // 2
        y = container.y + (container.height - h) // 2

        return pygame.Rect(x, y, w, h)

    # -------------------------------
    # cached surfaces
    # -------------------------------
    def _build_panel_surfaces(self):
        """Pre-render rounded-rect backgrounds for each panel."""
        self.panel_surfaces = {}

        specs = [
            ('left',   self.left_panel,   PANEL_FILL[3]),
            ('center', self.center_outer, 200),
            ('right',  self.right_panel,  PANEL_FILL[3]),
            ('bottom', self.bottom_panel, PANEL_FILL[3]),
        ]

        for key, rect, alpha in specs:
            if rect.width <= 0 or rect.height <= 0:
                continue

            s = pygame.Surface(
                (rect.width, rect.height), pygame.SRCALPHA
            )

            pygame.draw.rect(
                s,
                (PANEL_FILL[0], PANEL_FILL[1], PANEL_FILL[2], alpha),
                s.get_rect(),
                border_radius=20,
            )
            pygame.draw.rect(
                s,
                PANEL_BORDER,
                s.get_rect(),
                width=2,
                border_radius=20,
            )

            self.panel_surfaces[key] = s.convert_alpha()

    def _build_row_highlights(self):
        """Pre-render hover and selection highlight surfaces."""
        if self.list_mw <= 0 or self.list_row_h <= 0:
            self.row_hover_surf = None
            self.row_selected_surf = None
            return

        hover = pygame.Surface(
            (self.list_mw, self.list_row_h), pygame.SRCALPHA
        )
        pygame.draw.rect(
            hover,
            (*HIGHLIGHT_BG, 150),
            hover.get_rect(),
            border_radius=10,
        )
        self.row_hover_surf = hover.convert_alpha()

        sel = pygame.Surface(
            (self.list_mw, self.list_row_h), pygame.SRCALPHA
        )
        pygame.draw.rect(
            sel,
            (*SELECTED_BG, 220),
            sel.get_rect(),
            border_radius=10,
        )
        self.row_selected_surf = sel.convert_alpha()

    def _build_stage_bg(self):
        """Pre-render the center stage background and finish flash."""
        cs = self.center_stage

        if cs.width <= 0 or cs.height <= 0:
            self.stage_bg_surf = None
            self.completion_flash = None
            return

        stage = pygame.Surface(cs.size, pygame.SRCALPHA)
        pygame.draw.rect(
            stage, (12, 14, 32, 185),
            stage.get_rect(), border_radius=26,
        )
        pygame.draw.rect(
            stage, (185, 200, 255),
            stage.get_rect(), 2, border_radius=26,
        )
        self.stage_bg_surf = stage.convert_alpha()

        # flash overlay shown when a constellation is finished
        flash = pygame.Surface(cs.size, pygame.SRCALPHA)
        pygame.draw.rect(
            flash, (255, 230, 120, 28),
            flash.get_rect(), border_radius=26,
        )
        self.completion_flash = flash.convert_alpha()

    # -------------------------------
    # star sprites
    # -------------------------------
    def _build_star_sprite(self, radius, core_color, selected):
        """Build a single star sprite at one size and color.

        Parameters:
            radius: int
                Core radius in pixels.
            core_color: tuple of int
                The RGB color of the bright center.
            selected: bool
                When ``True``, draw a slightly larger and brighter
                version of the sprite.
        Returns:
            surface: pygame.Surface
                A pre-rendered RGBA surface ready to blit.
        """
        # find matching glow size and alpha for this radius
        glow_r, alpha = radius + 8, 220
        for _mag, r, gr, a in STAR_TIERS:
            if r == radius:
                glow_r, alpha = gr, a
                break

        sel_glow = glow_r + (5 if selected else 0)
        sel_core = radius + (2 if selected else 0)
        size = (sel_glow + 4) * 2

        glow = _glow_color(core_color)

        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        c = size // 2

        # outer glow
        pygame.draw.circle(
            surf, (*glow, alpha // 3), (c, c), sel_glow,
        )

        # middle glow
        inner = _lighten(glow, 0.25)
        pygame.draw.circle(
            surf, (*inner, alpha // 2), (c, c),
            max(1, sel_glow - 3),
        )

        # bright halo near the center
        bright = _lighten(core_color, 0.35)
        pygame.draw.circle(
            surf, (*bright, min(255, alpha)), (c, c),
            max(1, sel_core + 1),
        )

        # solid center
        pygame.draw.circle(surf, core_color, (c, c), sel_core)

        # small white core dot when selected
        if selected:
            pygame.draw.circle(
                surf, (255, 255, 255), (c, c),
                max(1, sel_core // 2),
            )

        return surf.convert_alpha()

    def get_star_sprite(self, radius, core_color, selected=False):
        """Return a cached star sprite, building it on first request.

        Parameters:
            radius: int
                Core radius in pixels.
            core_color: tuple of int
                The RGB color of the bright center.
            selected: bool, optional
                Whether to return the highlighted variant.
        Returns:
            surface: pygame.Surface
                A pre-rendered star sprite.
        """
        key = (radius, core_color, selected)
        sprite = self._star_sprite_cache.get(key)
        if sprite is None:
            sprite = self._build_star_sprite(radius, core_color, selected)
            self._star_sprite_cache[key] = sprite
        return sprite

    def _build_star_sprites(self):
        """Build the default star and shine sprite caches."""
        # clear old cached surfaces
        self.star_sprites = {}
        self._star_sprite_cache = {}
        self.shine_sprites = {}

        # base sizes from STAR_TIERS plus the mini-map radius
        entries = [
            (r, glow, alpha) for _mag, r, glow, alpha in STAR_TIERS
        ]
        entries.append((MINIMAP_RADIUS, MINIMAP_RADIUS + 5, 200))

        for radius, glow_r, alpha in entries:
            for selected in (False, True):
                core = SUCCESS if selected else STAR_COLOR
                sprite = self._build_star_sprite(radius, core, selected)

                # store default star sprite and pre-warm the cache
                self.star_sprites[(radius, selected)] = sprite
                self._star_sprite_cache[
                    (radius, core, selected)
                ] = sprite

            # build the golden shine animation frames
            for frame in range(SHINE_FRAME_COUNT):
                shine = 1.0 - (frame / (SHINE_FRAME_COUNT - 1))

                # the ring grows as it fades out
                ring_r = radius + 6 + int((1.0 - shine) * 26)
                size = (ring_r + 3) * 2

                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                c = size // 2

                # outer glow ring
                outer_a = int(150 * shine)
                pygame.draw.circle(
                    surf, (*SHINE_GLOW, outer_a),
                    (c, c), ring_r, max(2, ring_r // 4),
                )

                # middle ring
                mid_a = int(210 * shine)
                pygame.draw.circle(
                    surf, (*SHINE_GLOW, mid_a),
                    (c, c), max(1, ring_r - 2), 3,
                )

                # bright center ring
                core_a = int(255 * shine)
                pygame.draw.circle(
                    surf, (*SHINE_CORE, core_a),
                    (c, c), max(1, ring_r - 4), 2,
                )

                self.shine_sprites[(radius, frame)] = surf.convert_alpha()

    def _load_background(self, w, h):
        """Load and scale the background image, or build a fallback.

        Parameters:
            w: int
                Window width in pixels.
            h: int
                Window height in pixels.
        """
        # skip work if the background is already the right size
        if self._bg_source_size == (w, h) and self.background is not None:
            return

        try:
            if os.path.exists(BACKGROUND_PATH):
                bg = pygame.image.load(BACKGROUND_PATH).convert()
                self.background = pygame.transform.smoothscale(
                    bg, (w, h)
                )
                self._bg_source_size = (w, h)
                return
        except Exception:
            pass

        # generate a simple background if image load fails
        self.background = self._make_star_bg(w, h)
        self._bg_source_size = (w, h)

    @staticmethod
    def _make_star_bg(w, h):
        """Generate a simple procedural starfield background.

        Parameters:
            w: int
                Window width in pixels.
            h: int
                Window height in pixels.
        Returns:
            surface: pygame.Surface
                A solid background with scattered stars and a faint
                nebula overlay.
        """
        surf = pygame.Surface((w, h)).convert()
        surf.fill(BG_COLOR)

        count = max(140, (w * h) // 9000)

        for i in range(count):
            x = (i * 137) % w
            y = (i * 89 + i * 13) % h
            r = 1 + (i % 3)
            c = 150 + (i * 7) % 90
            pygame.draw.circle(
                surf, (c, c, min(255, c + 20)), (x, y), r,
            )

        neb = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(
            neb,
            (70, 50, 170, 60),
            (w * 0.18, h * 0.12, w * 0.45, h * 0.30),
        )
        pygame.draw.ellipse(
            neb,
            (35, 90, 220, 40),
            (w * 0.42, h * 0.35, w * 0.38, h * 0.25),
        )

        surf.blit(neb, (0, 0))
        return surf.convert()


if __name__ == '__main__':
    print('Input: a hidden 800x600 pygame window and a Layout instance.')
    print('Expected: panel rects are non-empty and consistent with the size.')

    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    test_screen = pygame.display.set_mode((800, 600))
    test_layout = Layout()
    test_layout.update(test_screen, 800, 600)
    print(f'left_panel    = {test_layout.left_panel}')
    print(f'center_outer  = {test_layout.center_outer}')
    print(f'right_panel   = {test_layout.right_panel}')
    print(f'bottom_panel  = {test_layout.bottom_panel}')
    pygame.quit()
