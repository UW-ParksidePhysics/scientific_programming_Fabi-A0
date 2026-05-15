# Final Project Revision Plan

## Project: Constellation Explorer

The Constellation Explorer is a pygame educational app where users trace constellations across a star field, with companion star data including magnitude, distance, and spectral type. Reviewer feedback identified four areas for revision: expanding the constellation library beyond the original ten, adding richer metadata, supporting dynamic content updates without a code rebuild, and clarifying the mobile/web deployment story.

## Main Feedback Received

Reviewers noted that ten curated constellations limit the app's educational reach and that the codebase included no tooling for non-developers to extend the content. They also asked how end-users would interact with custom data on shared hosting (itch.io) without overwriting the master content for other visitors. Additional feedback emphasized clearer per-star metadata and a tighter platform-aware save behavior so a desktop user has full file control while a browser user does not damage the shared content.

## Changes Required

**Code:** Build Two tools — `import_constellations.py` (Stellarium importer supporting both legacy `.fab` and current `index.json` formats), and `editor.py` (a visual pygame editor). Integrate the editor into the running game behind a hidden Ctrl+Shift+E access prompt. Introduce `save_manager.py` so the same code paths handle desktop file writes and browser localStorage saves. Refresh in-game caches when the editor exits so edits appear without a restart.

**Documentation:** Update the README to describe the new tooling, the editor access flow, the localStorage save model for itch.io, and the difference between desktop master files and per-browser private saves.

**Visualizations:** Use B-V color data so each star renders in its correct astrophysical color. The editor exposes magnitude and spectral type for tuning.

**Workflow:** Stellarium's `index.json` is the source of truth for the 88 IAU constellations; SIMBAD fills missing star metadata; `editor.py` handles polish.

## Highest Priority for Community Partner

Expanding to all 88 IAU constellations and ensuring itch.io visitors get private saves are the highest community-partner items, since both directly affect end-user experience and protect content integrity for everyone visiting the published page.

## Highest Priority for Functionality and Readability

The in-game editor unlock flow and the platform-aware save manager are highest for functionality. For readability, refactoring `editor.py` into an embeddable `EditorApp` class and consolidating all save logic into `save_manager.py` removed duplicated I/O code across modules.

## Changes Not Being Made

I am not adding remote/cloud sync for browser saves. It is currently out of scope for the time needed for the educational tool and would require backend infrastructure inconsistent with the project's static-hosting target. I am also not enforcing stronger-than-plaintext access control on the editor code, since this is obscurity-level protection intended to prevent casual tampering, not real security — the README states this plainly.
