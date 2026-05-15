# TODO

## Community Partner Feedback

- [ ] Run `python import_constellations.py --file index.json --fetch-missing --overwrite` to import all 88 IAU constellations from the Stellarium dataset
- [ ] Verify all 88 constellations appear in the left-panel list and that the up/down scroll arrows page through them correctly
- [ ] Walk through the in-game editor unlock flow end-to-end (Ctrl+Shift+E → access code → editor opens → edit → save → exit → game shows the change)
- [ ] Change `EDITOR_ACCESS_CODE` in `config.py` from the default `'stardust'` to a private code before publishing
- [ ] Set `EDITOR_NO_CODE = False` in `config.py` before publishing the public build
- [ ] Build the pygbag browser version and confirm that editing inside the in-game editor saves to localStorage only and does NOT modify the bundled JSON files
- [ ] Open the itch.io build in a clean browser profile (incognito or a different browser) and confirm it shows the master 88-constellation set, not another visitor's edits
- [ ] Confirm clearing browser site data restores the master constellation set on next load

## Instructor Feedback

- [ ] Add a `requirements.txt` listing pygame, astroquery, and requests (the two import tools need astroquery; the game itself only needs pygame)
- [ ] Add sample commands to the README showing how to use each import tool
- [ ] Document the save behavior difference between desktop (master JSON files with `.bak` backups) and itch.io browser (per-visitor localStorage) in a clearly labeled README section
- [ ] Submit the final repository link with all eight updated module files in place (`main.py`, `editor.py`, `data_manager.py`,`layout.py`, `renderer.py`, `config.py`,`game_state.py`, `save_manager.py`),

## Functionality

- [ ] Test desktop save: open editor in-game, edit a constellation's description, Ctrl+S, verify timestamped `.bak` files appear and `constellations_v2.json` reflects the change
- [ ] Test browser save: build with pygbag, open in browser, edit a constellation, save, reload the page, confirm the edit persists in that browser
- [ ] Verify cache refresh after exiting editor: rename a constellation in the editor, click Back to Game, confirm the new name appears immediately in the game's left list
- [ ] Test star detail editing: change a magnitude in the editor, save, confirm the star renders at the new size when viewing that constellation in the game
- [ ] Test that the magnitude/distance fields accept only numeric input and reject `abc` without crashing
- [ ] Verify Tab key cycles through constellation fields, then star fields when a star is selected
- [ ] Verify renaming a star in the editor updates both `display_stars` (in the constellation) and the `stars_by_name` lookup
- [ ] Confirm that pressing Ctrl+Shift+E a second time during a session jumps straight to the editor without re-prompting for the code
- [ ] Confirm pressing Esc inside the unlock prompt cancels cleanly and returns to the game

## Visualizations and Communication

- [ ] Verify B-V color data renders five well-known stars in plausible colors (Vega blue-white, Betelgeuse orange-red, Aldebaran orange, Rigel blue-white, Antares red)
- [ ] Check that the mini-map in the game's bottom panel shows star colors and edges correctly
- [ ] Confirm the editor's right panel cleanly switches between "constellation only" and "constellation + star details" when a star is selected/deselected
- [ ] Confirm the editor status bar displays the platform mode label (`(desktop)` vs `(browser (private local save))`) on open so the user knows what saving will do
- [ ] Verify the unlock prompt's dot-masked input is readable and the blinking caret renders correctly

## Documentation and Reproducibility

- [ ] Update README.md with a project overview, install steps, and instructions for running on desktop vs building for itch.io with pygbag
- [ ] Document the editor unlock flow including how to change the access code and what `EDITOR_NO_CODE` does
- [ ] Add a section explaining the localStorage save model: master files are read-only on itch.io, each browser keeps its own private save
- [ ] Document each of the three companion tools (`import_stars.py`, `import_constellations.py`, `editor.py`) with at least one example command
- [ ] Include one or two screenshots in the README: the game view and the in-game editor

## Code Readability and Standards

- [ ] Run a final pass to remove any unused imports across all six updated modules
- [ ] Confirm every public function and class has a docstring explaining its purpose
- [ ] Verify consistent naming (snake_case for functions and variables, PascalCase for classes, UPPER_SNAKE for constants)
- [ ] Verify no debug `print()` calls remain in production code paths
- [ ] Confirm that `python editor.py` still works as a standalone desktop tool in addition to the in-game embedded mode
- [ ] Confirm imports between modules are non-circular (`save_manager` is imported by `data_manager`, `editor`, and `main`; nothing imports `main`)
