"""
layout.py
This file handles the screen layout, fonts, and cached surfaces.

It also changes the layout depending on the screen shape:
- landscape for wider screens
- portrait for taller screens
"""

import os
import pygame
from config import (
    BG_COLOR, CENTER_RATIO, BACKGROUND_PATH,
    PANEL_FILL, PANEL_BORDER, HIGHLIGHT_BG, SELECTED_BG,
    STAR_COLOR, STAR_GLOW, SUCCESS
)

# how many shine frames to make
SHINE_FRAME_COUNT = 6

# star sizes used by the renderer
STAR_RADII = (4, 8)

# switch to portrait if screen is more narrow/tall
PORTRAIT_ASPECT = 1.20


class Layout:
    def __init__(self):
        self.left_panel = pygame.Rect(0, 0, 0, 0)
        self.center_outer = pygame.Rect(0, 0, 0, 0)
        self.center_stage = pygame.Rect(0, 0, 0, 0)
        self.right_panel = pygame.Rect(0, 0, 0, 0)
        self.bottom_panel = pygame.Rect(0, 0, 0, 0)
        self.clear_btn = pygame.Rect(0, 0, 0, 0)
        self.scroll_up = pygame.Rect(0, 0, 0, 0)
        self.scroll_down = pygame.Rect(0, 0, 0, 0)

        self.is_portrait = False

        self.font_xs = None
        self.font_sm = None
        self.font_md = None
        self.font_lg = None
        self.font_xl = None
        self.background = None

        self.panel_surfaces = {}
        self.row_hover_surf = None
        self.row_selected_surf = None
        self.stage_bg_surf = None
        self.completion_flash = None
        self.star_sprites = {}
        self.shine_sprites = {}

        self.list_x = 0
        self.list_mw = 0
        self.list_row_h = 0

        # save screen size so we do not rebuild everything for no reason
        self._last_size = (0, 0)
        self._bg_source_size = (0, 0)

        self.version = 0

    # -------------------------------
    # main update
    # -------------------------------
    def update(self, screen, w, h):
        # skip if the size did not change
        if (w, h) == self._last_size and self.version > 0:
            return

        self._last_size = (w, h)

        self._update_fonts(w, h)

        pad = max(6, int(min(w, h) * 0.022))
        gap = max(4, int(min(w, h) * 0.016))

        content = pygame.Rect(
            pad, pad,
            max(w - 2 * pad, 1),
            max(h - 2 * pad, 1)
        )

        aspect = content.width / max(content.height, 1)
        self.is_portrait = aspect < PORTRAIT_ASPECT

        # choose layout style
        if self.is_portrait:
            self._layout_portrait(content, gap)
        else:
            self._layout_landscape(content, gap)

        self._compute_list_and_button()

        # rebuild cached surfaces after resize
        self._load_background(w, h)
        self._build_panel_surfaces()
        self._build_row_highlights()
        self._build_stage_bg()
        self._build_star_sprites()

        self.version += 1

    # -------------------------------
    # layout shapes
    # -------------------------------
    def _layout_landscape(self, content, gap):
        """Layout for wider screens."""
        left_w = int(content.width * 0.22)
        right_w = int(content.width * 0.24)
        middle_w = content.width - left_w - right_w - gap * 2
        top_h = int(content.height * 0.76)
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
        """Layout for taller screens."""
        row1_h = int(content.height * 0.58)
        row2_h = int(content.height * 0.22)
        row3_h = content.height - row1_h - row2_h - 2 * gap

        # keep the list panel wide enough to use
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
        """Fit the drawing area inside the center panel."""
        return self._fit_rect(
            outer.inflate(
                -int(outer.width * 0.05),
                -int(outer.height * 0.07)
            ),
            CENTER_RATIO
        )

    def _compute_list_and_button(self):
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
        """Update font sizes based on screen size."""
        ref = max(640, int((w * h) ** 0.5))

        self.font_xs = pygame.font.SysFont('arial', max(13, int(ref * 0.013)))
        self.font_sm = pygame.font.SysFont('arial', max(15, int(ref * 0.016)))
        self.font_md = pygame.font.SysFont('arial', max(19, int(ref * 0.021)))
        self.font_lg = pygame.font.SysFont('arial', max(24, int(ref * 0.028)))
        self.font_xl = pygame.font.SysFont('arial', max(30, int(ref * 0.041)))

    @staticmethod
    def _fit_rect(container, target_ratio):
        # fit a rectangle inside another rectangle with a certain ratio
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
        self.panel_surfaces = {}

        specs = [
            ('left', self.left_panel, 210),
            ('center', self.center_outer, 170),
            ('right', self.right_panel, 210),
            ('bottom', self.bottom_panel, 210),
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
        if self.list_mw <= 0 or self.list_row_h <= 0:
            self.row_hover_surf = None
            self.row_selected_surf = None
            return

        hover = pygame.Surface((self.list_mw, self.list_row_h), pygame.SRCALPHA)
        pygame.draw.rect(
            hover,
            (*HIGHLIGHT_BG, 130),
            hover.get_rect(),
            border_radius=10
        )
        self.row_hover_surf = hover.convert_alpha()

        sel = pygame.Surface((self.list_mw, self.list_row_h), pygame.SRCALPHA)
        pygame.draw.rect(
            sel,
            (*SELECTED_BG, 200),
            sel.get_rect(),
            border_radius=10
        )
        self.row_selected_surf = sel.convert_alpha()

    def _build_stage_bg(self):
        cs = self.center_stage

        if cs.width <= 0 or cs.height <= 0:
            self.stage_bg_surf = None
            self.completion_flash = None
            return

        stage = pygame.Surface(cs.size, pygame.SRCALPHA)
        pygame.draw.rect(
            stage, (9, 10, 24, 170), stage.get_rect(), border_radius=26
        )
        pygame.draw.rect(
            stage, (160, 180, 255), stage.get_rect(), 2, border_radius=26
        )
        self.stage_bg_surf = stage.convert_alpha()

        flash = pygame.Surface(cs.size, pygame.SRCALPHA)
        pygame.draw.rect(
            flash, (180, 220, 255, 18), flash.get_rect(), border_radius=26
        )
        self.completion_flash = flash.convert_alpha()

    def _build_star_sprites(self):
        self.star_sprites = {}
        self.shine_sprites = {}

        for radius in STAR_RADII:
            for selected in (False, True):
                glow_r = radius + (8 if selected else 5)
                core_r = radius + (2 if selected else 0)
                size = (glow_r + 2) * 2

                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                c = size // 2

                pygame.draw.circle(surf, STAR_GLOW, (c, c), glow_r)

                core_color = SUCCESS if selected else STAR_COLOR
                pygame.draw.circle(surf, core_color, (c, c), core_r)

                self.star_sprites[(radius, selected)] = surf.convert_alpha()

            for frame in range(SHINE_FRAME_COUNT):
                shine = 1.0 - (frame / (SHINE_FRAME_COUNT - 1))
                elapsed = 1.0 - shine
                ring_r = radius + 6 + int(elapsed * 24)
                col = int(130 + 125 * shine)
                size = (ring_r + 2) * 2

                surf = pygame.Surface((size, size), pygame.SRCALPHA)
                c = size // 2

                pygame.draw.circle(surf, (col, col, 255), (c, c), ring_r, 2)
                self.shine_sprites[(radius, frame)] = surf.convert_alpha()

    def _load_background(self, w, h):
        # skip reloading if the background is already the right size
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

        self.background = self._make_star_bg(w, h)
        self._bg_source_size = (w, h)

    @staticmethod
    def _make_star_bg(w, h):
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