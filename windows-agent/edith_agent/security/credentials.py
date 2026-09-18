import json
import os
from pathlib import Path
from typing import Optional
from edith_agent.config.settings import agent_settings

CREDENTIALS_FILE = Path(agent_settings.CONFIG_DIR) / "credentials.json"


class CredentialStore:
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or CREDENTIALS_FILE
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)

    def save_device_credentials(self, device_id: str, device_token: str):
        """Saves device credentials securely."""
        data = {
            "device_id": device_id,
            "device_token": device_token
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_device_credentials(self) -> dict:
        """Loads saved device credentials if available."""
        # 1. Environment variable override
        if agent_settings.DEVICE_TOKEN:
            return {
                "device_id": agent_settings.DEVICE_ID,
                "device_token": agent_settings.DEVICE_TOKEN
            }

        # 2. Local credential file
        if self.storage_path.exists():
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get_token(self) -> Optional[str]:
        creds = self.load_device_credentials()
        return creds.get("device_token")

    def get_device_id(self) -> str:
        creds = self.load_device_credentials()
        return creds.get("device_id", agent_settings.DEVICE_ID)

    def clear(self):
        if self.storage_path.exists():
            try:
                os.remove(self.storage_path)
            except Exception:
                pass


credentials_store = CredentialStore()
