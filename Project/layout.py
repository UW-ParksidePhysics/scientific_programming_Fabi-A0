"""
layout.py
This file sets up how everything is arranged on the screen.

It also handles:
- screen sections
- font sizes
- saved surfaces

It can switch layouts depending on screen shape:
- landscape for wide screens
- portrait for tall screens
"""

import os
import sys
import pygame
from config import (
    BG_COLOR, BACKGROUND_PATH,
    PANEL_FILL, PANEL_BORDER, HIGHLIGHT_BG, SELECTED_BG,
    STAR_COLOR, STAR_GLOW, SUCCESS, STAR_TIERS,
    SHINE_CORE, SHINE_GLOW,
)

# number of glow frames
SHINE_FRAME_COUNT = 6

# star sizes used in the program
STAR_RADII = tuple(t[1] for t in STAR_TIERS)

# small star size used in the mini map
MINIMAP_RADIUS = 4

# only switch to portrait if the screen is clearly tall
PORTRAIT_ASPECT = 1.05


def _allow_portrait():
    """
    Check if this version is allowed to use portrait mode.
    Phones and tablets can use it.
    Desktop and browser versions stay landscape.
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
    # make a color lighter
    r, g, b = rgb[:3]
    return (
        min(255, int(r + (255 - r) * amount)),
        min(255, int(g + (255 - g) * amount)),
        min(255, int(b + (255 - b) * amount)),
    )


def _glow_color(core_rgb):
    # make a glow color that matches the star color
    return _lighten(core_rgb, 0.35)


class Layout:
    def __init__(self):
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

        # fonts
        self.font_xs = None
        self.font_sm = None
        self.font_md = None
        self.font_lg = None
        self.font_xl = None

        # background
        self.background = None

        # saved surfaces
        self.panel_surfaces = {}
        self.row_hover_surf = None
        self.row_selected_surf = None
        self.stage_bg_surf = None
        self.completion_flash = None

        # default star images
        self.star_sprites = {}

        # saved star images by size, color, and state
        self._star_sprite_cache = {}

        # saved shine images
        self.shine_sprites = {}

        # list layout values
        self.list_x = 0
        self.list_mw = 0
        self.list_row_h = 0

        # keep last screen size so it does not rebuild for no reason
        self._last_size = (0, 0)
        self._bg_source_size = (0, 0)

        self.version = 0

    # -------------------------------
    # main update
    # -------------------------------
    def update(self, screen, w, h):
        # skip extra work if screen size did not change
        if (w, h) == self._last_size and self.version > 0:
            return

        self._last_size = (w, h)

        self._update_fonts(w, h)

        # spacing around panels
        pad = max(6, int(min(w, h) * 0.022))
        gap = max(4, int(min(w, h) * 0.016))

        content = pygame.Rect(
            pad, pad,
            max(w - 2 * pad, 1),
            max(h - 2 * pad, 1)
        )

        # choose portrait or landscape
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

        # rebuild saved parts after resize
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
        """Set the layout for wide screens."""
        left_w = max(220, int(content.width * 0.19))
        right_w = max(240, int(content.width * 0.21))
        middle_w = content.width - left_w - right_w - gap * 2

        top_h = int(content.height * (0.72 if content.height > 700 else 0.78))
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
            middle_w + gap + right_w, bottom_h
        )

        self.center_stage = self._stage_inside(self.center_outer)

    def _layout_portrait(self, content, gap):
        """Set the layout for tall screens."""
        row1_h = int(content.height * 0.58)
        row2_h = int(content.height * 0.22)
        row3_h = content.height - row1_h - row2_h - 2 * gap

        left_w = max(int(content.width * 0.34),
                     min(240, content.width // 2))
        middle_w = content.width - left_w - gap

        self.left_panel = pygame.Rect(
            content.x, content.y, left_w, row1_h
        )
        self.center_outer = pygame.Rect(
            self.left_panel.right + gap, content.y, middle_w, row1_h
        )
        self.right_panel = pygame.Rect(
            content.x, self.left_panel.bottom + gap,
            content.width, row2_h
        )
        self.bottom_panel = pygame.Rect(
            content.x, self.right_panel.bottom + gap,
            content.width, row3_h
        )

        self.center_stage = self._stage_inside(self.center_outer)

    def _stage_inside(self, outer):
        """
        Make the drawing area fit inside the center panel.
        """
        return outer.inflate(
            -int(outer.width * 0.06),
            -int(outer.height * 0.10)
        )

    def _compute_list_and_button(self):
        # figure out size and place for the button and list
        bw = max(100, int(self.left_panel.width * 0.38))
        bh = max(34, int(self.left_panel.height * 0.07))

        self.clear_btn = pygame.Rect(
            self.left_panel.x + int(self.left_panel.width * 0.08),
            self.left_panel.bottom - bh - int(self.left_panel.height * 0.04),
            bw, bh
        )

        self.list_x = self.left_panel.x + int(self.left_panel.width * 0.08)
        self.list_mw = int(self.left_panel.width * 0.84)
        self.list_row_h = max(26, int(self.left_panel.height * 0.065))

    # -------------------------------
    # fonts
    # -------------------------------
    def _update_fonts(self, w, h):
        """Change font size based on screen size."""
        ref = max(640, int((w * h) ** 0.5))

        self.font_xs = pygame.font.SysFont('arial', max(13, int(ref * 0.013)))
        self.font_sm = pygame.font.SysFont('arial', max(15, int(ref * 0.016)))
        self.font_md = pygame.font.SysFont('arial', max(19, int(ref * 0.021)))
        self.font_lg = pygame.font.SysFont('arial', max(24, int(ref * 0.028)))
        self.font_xl = pygame.font.SysFont('arial', max(30, int(ref * 0.041)))

    @staticmethod
    def _fit_rect(container, target_ratio):
        # make a box fit inside another box
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
    # saved surfaces
    # -------------------------------
    def _build_panel_surfaces(self):
        # build panel background surfaces
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

            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

            pygame.draw.rect(
                s,
                (PANEL_FILL[0], PANEL_FILL[1], PANEL_FILL[2], alpha),
                s.get_rect(),
                border_radius=20
            )
            pygame.draw.rect(
                s,
                PANEL_BORDER,
                s.get_rect(),
                width=2,
                border_radius=20
            )

            self.panel_surfaces[key] = s.convert_alpha()

    def _build_row_highlights(self):
        # build hover and selected row backgrounds
        if self.list_mw <= 0 or self.list_row_h <= 0:
            self.row_hover_surf = None
            self.row_selected_surf = None
            return

        hover = pygame.Surface((self.list_mw, self.list_row_h), pygame.SRCALPHA)
        pygame.draw.rect(
            hover,
            (*HIGHLIGHT_BG, 150),
            hover.get_rect(),
            border_radius=10
        )
        self.row_hover_surf = hover.convert_alpha()

        sel = pygame.Surface((self.list_mw, self.list_row_h), pygame.SRCALPHA)
        pygame.draw.rect(
            sel,
            (*SELECTED_BG, 220),
            sel.get_rect(),
            border_radius=10
        )
        self.row_selected_surf = sel.convert_alpha()

    def _build_stage_bg(self):
        # build the draw zone background
        cs = self.center_stage

        if cs.width <= 0 or cs.height <= 0:
            self.stage_bg_surf = None
            self.completion_flash = None
            return

        stage = pygame.Surface(cs.size, pygame.SRCALPHA)
        pygame.draw.rect(
            stage, (12, 14, 32, 185), stage.get_rect(), border_radius=26
        )
        pygame.draw.rect(
            stage, (185, 200, 255), stage.get_rect(), 2, border_radius=26
        )
        self.stage_bg_surf = stage.convert_alpha()

        # build the flash shown when finished
        flash = pygame.Surface(cs.size, pygame.SRCALPHA)
        pygame.draw.rect(
            flash, (255, 230, 120, 28), flash.get_rect(), border_radius=26
        )
        self.completion_flash = flash.convert_alpha()

    # -------------------------------
    # star sprites
    # -------------------------------
    def _build_star_sprite(self, radius, core_color, selected):
        """
        Build one star image for a certain size and color.
        """
        # find matching glow size and strength
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
            surf, (*glow, alpha // 3), (c, c), sel_glow
        )

        # middle glow
        inner = _lighten(glow, 0.25)
        pygame.draw.circle(
            surf, (*inner, alpha // 2), (c, c), max(1, sel_glow - 3)
        )

        # bright area near center
        bright = _lighten(core_color, 0.35)
        pygame.draw.circle(
            surf, (*bright, min(255, alpha)), (c, c), max(1, sel_core + 1)
        )

        # solid center
        pygame.draw.circle(surf, core_color, (c, c), sel_core)

        # tiny white dot if selected
        if selected:
            pygame.draw.circle(surf, (255, 255, 255), (c, c), max(1, sel_core // 2))

        return surf.convert_alpha()

    def get_star_sprite(self, radius, core_color, selected=False):
        """
        Get a saved star image.
        If it does not exist yet, make it first.
        """
        key = (radius, core_color, selected)
        sprite = self._star_sprite_cache.get(key)
        if sprite is None:
            sprite = self._build_star_sprite(radius, core_color, selected)
            self._star_sprite_cache[key] = sprite
        return sprite

    def _build_star_sprites(self):
        """
        Build the default star images and shine rings.
        """
        # clear old saved images
        self.star_sprites = {}
        self._star_sprite_cache = {}
        self.shine_sprites = {}

        # list of star sizes to build
        entries = [(r, glow, alpha) for _mag, r, glow, alpha in STAR_TIERS]

        # also add the small mini map size
        entries.append((MINIMAP_RADIUS, MINIMAP_RADIUS + 5, 200))

        for radius, glow_r, alpha in entries:
            for selected in (False, True):
                core = SUCCESS if selected else STAR_COLOR
                sprite = self._build_star_sprite(radius, core, selected)

                # save default stars
                self.star_sprites[(radius, selected)] = sprite
                self._star_sprite_cache[(radius, core, selected)] = sprite

            # build golden shine frames
            for frame in range(SHINE_FRAME_COUNT):
                shine = 1.0 - (frame / (SHINE_FRAME_COUNT - 1))

                # ring gets bigger as it fades out
                ring_r = radius + 6 + int((1.0 - shine) * 26)
                size = (ring_r + 3) * 2

                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                c = size // 2

                # outer glow ring
                outer_a = int(150 * shine)
                pygame.draw.circle(
                    surf, (*SHINE_GLOW, outer_a),
                    (c, c), ring_r, max(2, ring_r // 4)
                )

                # middle ring
                mid_a = int(210 * shine)
                pygame.draw.circle(
                    surf, (*SHINE_GLOW, mid_a),
                    (c, c), max(1, ring_r - 2), 3
                )

                # bright center ring
                core_a = int(255 * shine)
                pygame.draw.circle(
                    surf, (*SHINE_CORE, core_a),
                    (c, c), max(1, ring_r - 4), 2
                )

                self.shine_sprites[(radius, frame)] = surf.convert_alpha()

    def _load_background(self, w, h):
        # skip work if the background is already the right size
        if self._bg_source_size == (w, h) and self.background is not None:
            return

        try:
            if os.path.exists(BACKGROUND_PATH):
                bg = pygame.image.load(BACKGROUND_PATH).convert()
                self.background = pygame.transform.smoothscale(bg, (w, h))
                self._bg_source_size = (w, h)
                return
        except Exception:
            pass

        # make a simple background if image load fails
        self.background = self._make_star_bg(w, h)
        self._bg_source_size = (w, h)

    @staticmethod
    def _make_star_bg(w, h):
        # make a starry background
        surf = pygame.Surface((w, h)).convert()
        surf.fill(BG_COLOR)

        count = max(140, (w * h) // 9000)

        for i in range(count):
            x = (i * 137) % w
            y = (i * 89 + i * 13) % h
            r = 1 + (i % 3)
            c = 150 + (i * 7) % 90
            pygame.draw.circle(surf, (c, c, min(255, c + 20)), (x, y), r)

        neb = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(
            neb,
            (70, 50, 170, 60),
            (w * 0.18, h * 0.12, w * 0.45, h * 0.30)
        )
        pygame.draw.ellipse(
            neb,
            (35, 90, 220, 40),
            (w * 0.42, h * 0.35, w * 0.38, h * 0.25)
        )

        surf.blit(neb, (0, 0))
        return surf.convert()