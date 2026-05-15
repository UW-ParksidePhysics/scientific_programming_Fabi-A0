# Requirements

## Third-Party Packages (must install)

| Package | Version | Used By |
|---------|---------|---------|
| pygame | >=2.5.0 | Game runtime — all modules |
| pygbag | >=0.9.0 | Browser build for itch.io only (optional) |

## Standard Library (already included with Python)

| Package | Used By |
|---------|---------|
| asyncio | `main.py` — async game loop for pygbag compatibility |
| csv | `data_manager.py` — reads the B-V color index |
| json | `data_manager.py`, `save_manager.py` — loads/saves constellation and star data |
| math | `game_state.py` — distance calculations for star hit detection |
| os | `config.py`, `data_manager.py`, `save_manager.py` — file path resolution |
| shutil | `save_manager.py` — creates `.bak` backup files before saving |
| sys | `main.py`, `layout.py`, `save_manager.py` — platform detection |
| datetime | `save_manager.py` — timestamps backup filenames |

## Install


```bash
# Game only
pip install pygame

# Game + browser build
pip install pygame pygbag
```
