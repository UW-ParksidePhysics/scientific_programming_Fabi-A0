"""Cross-platform load and save manager for the game's JSON data."""

__author__ = "Fabian Anguiano"

import json
import os
import shutil
import sys
from datetime import datetime


# detect environment
IS_BROWSER = (sys.platform == 'emscripten')

# browser localStorage keys (namespaced so nothing else collides)
LS_CONSTELLATIONS = 'constellation_explorer__constellations_v2'
LS_STARS = 'constellation_explorer__stars_v2'


def _now_stamp():
    """Return a filesystem-safe timestamp suitable for backup filenames.

    Returns:
        stamp: str
            A timestamp of the form ``YYYYMMDD_HHMMSS``.
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def _strip_private(data):
    """Recursively drop dict keys that start with an underscore.

    The game's DataManager attaches private fields like ``_edge_set``
    (a Python set used for fast edge lookups) to each constellation.
    Those are caches, not data — they are not JSON-serializable, so
    they must be removed before any save operation.

    Parameters:
        data: object
            Any JSON-like structure of dicts, lists, and scalars.
    Returns:
        cleaned: object
            A new copy of ``data`` with all underscore-prefixed dict
            keys removed. The original input is not modified.
    """
    if isinstance(data, dict):
        return {
            k: _strip_private(v) for k, v in data.items()
            if not (isinstance(k, str) and k.startswith('_'))
        }
    if isinstance(data, list):
        return [_strip_private(item) for item in data]
    return data


def _ls_get(key):
    """Read a string from browser localStorage.

    Parameters:
        key: str
            The localStorage key to read.
    Returns:
        value: str or None
            The stored string, or ``None`` if the key is missing,
            the value is ``'null'``, or any error occurs (including
            running outside a browser).
    """
    if not IS_BROWSER:
        return None
    try:
        import platform as web_platform
        val = web_platform.window.localStorage.getItem(key)
        if val is None or val == 'null':
            return None
        return val
    except Exception:
        return None


def _ls_set(key, value):
    """Write a string to browser localStorage.

    Parameters:
        key: str
            The localStorage key to write.
        value: str
            The string value to store.
    Returns:
        success: bool
            ``True`` when the write completed; ``False`` when running
            outside a browser or any error occurs (for example, when
            the browser storage quota is exhausted).
    """
    if not IS_BROWSER:
        return False
    try:
        import platform as web_platform
        web_platform.window.localStorage.setItem(key, value)
        return True
    except Exception:
        return False


def _ls_remove(key):
    """Remove a key from browser localStorage if present.

    Parameters:
        key: str
            The localStorage key to delete. No effect outside the
            browser environment or when the key is absent.
    """
    if not IS_BROWSER:
        return
    try:
        import platform as web_platform
        web_platform.window.localStorage.removeItem(key)
    except Exception:
        pass


class SaveManager:
    """Unified load and save layer for the game's JSON data files.

    On desktop the manager reads and writes the master JSON files
    directly and produces timestamped ``.bak`` backups before each
    save. On the browser (pygbag/itch.io) the manager reads the
    master files as read-only defaults and writes user edits to
    localStorage, so each visitor keeps a private save while the
    shipped master files remain untouched.

    Save calls never raise: any failure is reported as a status
    string starting with ``'WARN:'`` so the editor can surface it
    instead of crashing the asyncio loop powering the pygbag build.
    """

    def __init__(self, constellations_path, stars_path):
        """Set the on-disk locations of the master JSON files.

        Parameters:
            constellations_path: str
                Path to the constellations JSON file on disk.
            stars_path: str
                Path to the stars JSON file on disk.
        """
        self.constellations_path = constellations_path
        self.stars_path = stars_path

    @property
    def is_browser(self):
        """bool: True when running inside a pygbag/browser build."""
        return IS_BROWSER

    @property
    def mode_label(self):
        """str: Short human-readable label for the active save mode."""
        if IS_BROWSER:
            return 'browser (private local save)'
        return 'desktop'

    # -------------------------------
    # loading
    # -------------------------------
    def load_constellations(self):
        """Load the constellations list.

        On the browser, a localStorage override takes priority over
        the shipped master file when present.

        Returns:
            constellations: list of dict
                The constellation records, or an empty list when
                neither source provides usable data.
        """
        if IS_BROWSER:
            override = self._load_ls(LS_CONSTELLATIONS)
            if override is not None:
                return override

        return self._load_master(self.constellations_path)

    def load_stars(self):
        """Load the stars list.

        On the browser, a localStorage override takes priority over
        the shipped master file when present.

        Returns:
            stars: list of dict
                The star records, or an empty list when neither
                source provides usable data.
        """
        if IS_BROWSER:
            override = self._load_ls(LS_STARS)
            if override is not None:
                return override

        return self._load_master(self.stars_path)

    def _load_master(self, path):
        """Load and parse a JSON list from disk, tolerating errors.

        Parameters:
            path: str
                Filesystem path of the JSON file to read.
        Returns:
            records: list
                The parsed list, or an empty list when the file is
                missing, unreadable, or does not contain a list.
        """
        if not os.path.exists(path):
            return []
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (OSError, json.JSONDecodeError):
            pass
        return []

    def _load_ls(self, key):
        """Load and parse a JSON list from localStorage.

        Parameters:
            key: str
                The localStorage key holding a JSON list.
        Returns:
            records: list or None
                The parsed list, or ``None`` when the key is missing
                or the stored value is not a JSON list.
        """
        raw = _ls_get(key)
        if raw is None:
            return None
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return parsed
        except (json.JSONDecodeError, ValueError):
            pass
        return None

    # -------------------------------
    # saving
    # -------------------------------
    def save_constellations(self, data):
        """Persist the constellations list to the active storage.

        Parameters:
            data: list of dict
                Constellation records to save.
        Returns:
            message: str
                A short status line, beginning with ``'WARN:'`` when
                the save did not complete successfully.
        """
        return self._save(
            data, LS_CONSTELLATIONS, self.constellations_path,
            'constellations',
        )

    def save_stars(self, data):
        """Persist the stars list to the active storage.

        Parameters:
            data: list of dict
                Star records to save.
        Returns:
            message: str
                A short status line, beginning with ``'WARN:'`` when
                the save did not complete successfully.
        """
        return self._save(
            data, LS_STARS, self.stars_path, 'stars',
        )

    def _save(self, data, ls_key, path, label):
        """Dispatch a save to either localStorage or the master file.

        Parameters:
            data: list
                The records to save (private cache keys are removed
                before serialization).
            ls_key: str
                The localStorage key used on the browser.
            path: str
                The master file path used on the desktop.
            label: str
                Short human-readable name used in the returned
                status message.
        Returns:
            message: str
                A short status line.
        """
        # strip private cache fields like _edge_set before anything else
        try:
            cleaned = _strip_private(data)
        except Exception as exc:
            return f'WARN: {label} could not be cleaned for save: {exc}'

        if IS_BROWSER:
            # serialize first; failure here means the data shape is bad
            try:
                payload = json.dumps(cleaned)
            except (TypeError, ValueError) as exc:
                return f'WARN: {label} could not be serialized: {exc}'

            ok = _ls_set(ls_key, payload)
            if ok:
                return f'{label} saved to your browser'
            return f'WARN: browser save for {label} failed (storage full?)'

        # desktop path
        return self._save_master(path, cleaned, label)

    def _save_master(self, path, data, label):
        """Atomically write JSON to ``path`` and back up the old file.

        Parameters:
            path: str
                Destination file path.
            data: object
                JSON-serializable payload.
            label: str
                Short name used in the returned status message.
        Returns:
            message: str
                A short status line. On failure the message starts
                with ``'WARN:'`` and the original file is preserved.
        """
        bp = self._backup(path)
        try:
            # write to a temp file first, then rename, so a crash
            # mid-save cannot corrupt the existing file
            tmp = f'{path}.tmp'
            with open(tmp, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)
        except (OSError, TypeError, ValueError) as exc:
            return f'WARN: {label} save failed: {exc}'

        if bp:
            return f'{label} saved (backup: {os.path.basename(bp)})'
        return f'{label} saved'

    def _backup(self, path):
        """Copy ``path`` to a timestamped backup file if it exists.

        Parameters:
            path: str
                The file to back up.
        Returns:
            backup_path: str or None
                The path of the backup, or ``None`` when the source
                does not exist or the copy fails.
        """
        if not os.path.exists(path):
            return None
        bp = f'{path}.{_now_stamp()}.bak'
        try:
            shutil.copy2(path, bp)
            return bp
        except OSError:
            return None

    # -------------------------------
    # browser-only utilities
    # -------------------------------
    def reset_browser_overrides(self):
        """Wipe browser local saves so the master files take over.

        Returns:
            cleared: bool
                ``True`` when running in a browser and the keys were
                removed; ``False`` on the desktop where no overrides
                exist.
        """
        if not IS_BROWSER:
            return False
        _ls_remove(LS_CONSTELLATIONS)
        _ls_remove(LS_STARS)
        return True

    def has_browser_overrides(self):
        """Check whether any browser-local overrides are currently set.

        Returns:
            present: bool
                ``True`` when at least one override key holds a
                value; always ``False`` on the desktop.
        """
        if not IS_BROWSER:
            return False
        return (_ls_get(LS_CONSTELLATIONS) is not None
                or _ls_get(LS_STARS) is not None)


if __name__ == '__main__':
    print('Input: a SaveManager pointed at temp paths, with a tiny payload.')
    print('Expected: save and load round-trip works, message mentions backup.')

    import tempfile
    with tempfile.TemporaryDirectory() as tmp_dir:
        consts_path = os.path.join(tmp_dir, 'constellations_v2.json')
        stars_path = os.path.join(tmp_dir, 'stars_v2.json')

        manager = SaveManager(consts_path, stars_path)
        sample = [{'name': 'Orion', '_edge_set': {(0, 1)}}]
        first_save = manager.save_constellations(sample)
        second_save = manager.save_constellations(sample)
        loaded = manager.load_constellations()

        print(f'mode_label   = {manager.mode_label}')
        print(f'first save   = {first_save}')
        print(f'second save  = {second_save}')
        print(f'loaded back  = {loaded}')
