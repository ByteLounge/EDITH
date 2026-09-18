import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional, Tuple
from app.capabilities.tools import RiskLevel, CAPABILITY_RISK_MAP


class ConfirmationManager:
    def __init__(self):
        # Maps token -> PendingConfirmation
        self.pending: Dict[str, dict] = {}

    def get_risk_level(self, capability: str) -> RiskLevel:
        return CAPABILITY_RISK_MAP.get(capability, RiskLevel.LOW)

    def requires_confirmation(self, capability: str) -> bool:
        return self.get_risk_level(capability) == RiskLevel.HIGH

    def create_confirmation_request(
        self,
        user_id: str,
        device_id: str,
        device_name: str,
        capability: str,
        parameters: Dict[str, Any]
    ) -> Tuple[str, str]:
        """Creates a pending high-risk confirmation request and token."""
        token = f"conf_{secrets.token_urlsafe(16)}"
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=2)

        prompt = self._build_confirmation_prompt(capability, device_name)

        self.pending[token] = {
            "token": token,
            "user_id": user_id,
            "device_id": device_id,
            "device_name": device_name,
            "capability": capability,
            "parameters": parameters,
            "prompt": prompt,
            "expires_at": expires_at
        }
        return token, prompt

    def consume_confirmation(self, token: str, user_id: str) -> Optional[dict]:
        """Validates and retrieves the pending command, consuming the token."""
        entry = self.pending.pop(token, None)
        if not entry:
            return None

        now = datetime.now(timezone.utc)
        if now > entry["expires_at"]:
            return None

        if entry["user_id"] != user_id:
            return None

        return entry

    def _build_confirmation_prompt(self, capability: str, device_name: str) -> str:
        if capability in ("shutdown", "shutdown_device"):
            return f"Shutting down your {device_name} will close all running applications and end your session. Do you want me to continue?"
        elif capability in ("restart", "restart_device"):
            return f"Restarting your {device_name} will temporarily reboot the computer. Do you want me to continue?"
        elif capability in ("lock", "lock_device"):
            return f"Locking your {device_name} will lock the screen. Continue?"
        else:
            return f"Are you sure you want to execute '{capability}' on {device_name}?"


confirmation_manager = ConfirmationManager()
