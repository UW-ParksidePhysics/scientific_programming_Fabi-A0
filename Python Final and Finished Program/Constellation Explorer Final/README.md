# Constellation Explorer

An educational pygame app where you trace the night sky's most famous
constellations one star at a time and learn about each star — its
magnitude, distance, spectral type, and the color it actually shines
in the sky. Runs on desktop and in the browser via
[pygbag](https://github.com/pygame-web/pygbag).


---

## Table of Contents

1. [What's in this Project](#whats-in-this-project)
2. [Install](#install)
3. [Run on Desktop](#run-on-desktop)
4. [Build for the Browser (itch.io)](#build-for-the-browser-itchio)
5. [In-Game Controls](#in-game-controls)
6. [The Hidden In-Game Editor](#the-hidden-in-game-editor)
7. [Save Behavior: Desktop vs. Browser](#save-behavior-desktop-vs-browser)
8. [Companion Tool](#companion-tool)
9. [Project Structure](#project-structure)
10. [Configuration](#configuration)
11. [Credits and License](#credits-and-license)

---

## What's in this Project

- **A pygame game** that displays a star field and lets the player drag
  across stars to trace constellation lines. Finishing a constellation
  unlocks tap-for-details on every star in it.
- **A hidden in-game editor** behind a `Ctrl+Shift+E` access prompt.
  Lets non-developers add, rename, or correct constellations and star
  data without touching code.
- **A cross-platform save manager** that writes JSON files on the
  desktop and uses browser `localStorage` when the game is running in
  pygbag — so an itch.io visitor can save their own edits without
  overwriting the master content for everyone else.

---

## Install

Requires Python 3.10 or newer.

```bash
git clone <https://github.com/UW-ParksidePhysics/scientific_programming_Fabi-A0/tree/a4105de99dfe796bdfd8fa035077cf97a0b28ea8/Python%20Final%20and%20Finished%20Program/Constellation%20Explorer%20Final> constellation-explorer
cd constellation-explorer
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

`requirements.txt` lists:

- `pygame` — the game itself
- `pygbag` — only needed if you want to build the
  browser version

---

## Run on Desktop

From the project root:

```bash
python main.py
```

The window is resizable. Press `F11` to toggle fullscreen.

---

## Build for the Browser (itch.io)

First install pygbag:

```bash
pip install pygbag
```

Then, from the directory *above* the project folder:

```bash
python -m pygbag --width 1400 --height 800 constellation-explorer
```

pygbag will package the project and serve it locally at
`http://localhost:8000`. When you're happy with the build, zip the
contents of the generated `build/web/` folder and upload that zip to
itch.io as an HTML5 project.

> **Note:** Inside the browser build, edits made in the in-game editor
> are saved to that visitor's `localStorage` only — they do **not**
> modify the bundled JSON files in the zip you uploaded. See
> [Save Behavior](#save-behavior-desktop-vs-browser) below.

---

## In-Game Controls

| Action                              | Key / Gesture                |
|-------------------------------------|------------------------------|
| Select a constellation              | Click or tap a name in the list |
| Trace a constellation               | Click and drag across the stars |
| View a star's details (after done)  | Tap a star                   |
| Scroll the list                     | Mouse wheel, or up/down arrows |
| Clear the current drawing           | `C` or the Clear button      |
| Full reset (back to list view)      | `Esc`                        |
| Toggle fullscreen                   | `F11`                        |
| Open the hidden editor              | `Ctrl+Shift+E`               |
| Quit                                | Close the window             |

---

## The Hidden In-Game Editor

The editor lets you add, rename, edit, or remove constellations and
stars without leaving the game.

**To open it:**

1. Start the game (`python main.py`).
2. Press `Ctrl+Shift+E`.
3. Type the access code at the prompt and press Enter.
   (Default: `stardust`. Press `Esc` to cancel.)
4. The editor takes over the window. Press `Ctrl+S` to save, then
   click **Back to Game** when you're done.

Once you unlock the editor once in a session, `Ctrl+Shift+E` jumps
straight back in without re-asking for the code.

**Before sharing the game publicly**, change the access code:

```python
# config.py
EDITOR_ACCESS_CODE = 'stardust'
EDITOR_NO_CODE = False    # leave this False for public builds
```

`EDITOR_NO_CODE = True` skips the prompt entirely — convenient while
developing, but you almost certainly want this off in any build you
share.

> The access code is plain text in `config.py`. This is
> obscurity-level protection meant to keep casual visitors from
> tampering with content. It is **not** real security — anyone with
> access to the source can read the code.

---

## Save Behavior: Desktop vs. Browser

The same editor and save code work on both platforms, but they save
to different places. The status bar at the top of the editor shows
which mode you're in.

### Desktop — master JSON files

- Saving overwrites `constellations_v2.json` and `stars_v2.json` in
  the project folder.
- Each save first copies the current file to a timestamped backup
  (e.g. `constellations_v2.json.20251114_182301.bak`) in the same
  folder, so you can roll back if you make a mistake.
- The status bar reads: `(desktop)`.

### Browser (itch.io) — per-visitor localStorage

- Saving writes to two `localStorage` keys
  (`constellation_explorer__constellations_v2` and
  `constellation_explorer__stars_v2`) belonging to that browser
  profile only.
- The bundled JSON files inside the zip you uploaded are **never**
  modified, so every other visitor still sees the master content.
- When that visitor reloads the page, their edits load back from
  localStorage automatically.
- Clearing site data in the browser restores the master content.
- The status bar reads: `(browser (private local save))`.

This split is intentional: a desktop user has full file control,
while an itch.io visitor cannot damage the shared content for anyone
else.

---

## Companion Tool

### `editor.py`

The visual editor as a standalone tool, in case you'd rather edit
the data without launching the full game first.

```bash
python editor.py
```

This is the same `EditorApp` that the in-game `Ctrl+Shift+E` flow
uses, just bootstrapped on its own window. Saving from here writes to
the master JSON files directly (it's a desktop-only entry point).

---

## Project Structure

```
constellation-explorer/
├── main.py                    # game loop, event routing, editor unlock
├── config.py                  # colors, sizes, paths, editor access code
├── data_manager.py            # loads constellations, stars, B-V colors
├── save_manager.py            # desktop file writes vs. browser localStorage
├── layout.py                  # panel layout, fonts, cached surfaces
├── renderer.py                # draws panels, stars, lines, buttons
├── game_state.py              # tracks selection, drag, drawn edges
├── editor.py                  # in-game visual editor (EditorApp)
├── constellations_v2.json     # master constellation data
├── stars_v2.json              # master star data
├── Space.png                  # background image
└──

```

Module imports are non-circular: `save_manager` is imported by
`data_manager`, `editor`, and `main`; nothing imports `main`.

---

## Configuration

Most knobs live at the top of `config.py`:

| Setting                | What it does                                          |
|------------------------|-------------------------------------------------------|
| `FPS`                  | Frame rate cap (default 60)                          |
| `STAR_HIT_RADIUS`      | How close a tap needs to be to register on a star    |
| `STAR_SNAP_RADIUS`     | How close a drag needs to come to snap to a star     |
| `SCROLL_VISIBLE`       | How many constellations show in the list at once     |
| `OBSERVER_LOCATION`    | Label shown in the "Best viewing" section            |
| `EDITOR_ACCESS_CODE`   | Editor unlock code        |
| `EDITOR_NO_CODE`       | Skip the unlock prompt entirely if `True`            |
| `STAR_TIERS`           | Star size and glow by magnitude band                 |

File paths (`CONSTELLATIONS_PATH`, `STARS_PATH`, `BACKGROUND_PATH`,
`BV_CSV_PATH`) are resolved through `resolve_path()`, which checks the
project folder first and then `SEARCH_PATHS` — handy for running the
game from a phone storage location during testing.

---

## Credits and License

- Constellation line data adapted from the
  [Stellarium](https://stellarium.org/) project.
- Star metadata sourced from
  [SIMBAD](http://simbad.u-strasbg.fr/simbad/) via `astroquery`.
- B-V color index used to color each star to its real astrophysical
  color (blue, white, yellow, orange, red).
- Background art: `Space.png` (included).

This project is built with [pygame](https://www.pygame.org/) and runs
in the browser via [pygbag](https://github.com/pygame-web/pygbag).

Author: Fabian Anguiano.
