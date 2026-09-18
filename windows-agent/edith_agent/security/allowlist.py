import json
import re
from pathlib import Path
from typing import Dict, Optional

CONFIG_FILE = Path(__file__).parent.parent / "config" / "allowed_apps.json"

# Common friendly aliases mapped to keys
ALIASES = {
    "vs code": "vscode",
    "visual studio code": "vscode",
    "google chrome": "chrome",
    "browser": "chrome",
    "calc": "calculator",
    "windows terminal": "terminal",
    "file explorer": "explorer",
    "microsoft edge": "edge"
}

# Dangerous characters disallowed in application names
DISALLOWED_CHARS_PATTERN = re.compile(r"[\s;&|`$><\r\n\x00]")


class ApplicationAllowlist:
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or CONFIG_FILE
        self._allowed_apps: Dict[str, str] = {}
        self.load_allowlist()

    def load_allowlist(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._allowed_apps = json.load(f)
            except Exception:
                self._allowed_apps = self._default_allowlist()
        else:
            self._allowed_apps = self._default_allowlist()

    def _default_allowlist(self) -> Dict[str, str]:
        return {
            "vscode": "Code.exe",
            "chrome": "chrome.exe",
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "spotify": "Spotify.exe",
            "terminal": "wt.exe",
            "explorer": "explorer.exe",
            "edge": "msedge.exe"
        }

    def resolve_application(self, requested_app: str) -> Optional[str]:
        """
        Validates and resolves an application name to an allowlisted executable.
        Returns executable string if valid and allowlisted, otherwise None.
        CRITICAL: Never allows arbitrary paths or shell commands.
        """
        if not requested_app:
            return None

        clean_name = requested_app.lower().strip()

        # Check for friendly aliases
        if clean_name in ALIASES:
            clean_name = ALIASES[clean_name]

        # Check for shell metacharacters
        if DISALLOWED_CHARS_PATTERN.search(clean_name):
            return None

        # Must exist directly in allowed list
        return self._allowed_apps.get(clean_name)

    def list_allowed(self) -> list:
        return list(self._allowed_apps.keys())


allowlist = ApplicationAllowlist()
