import re
from typing import Dict, Any, List, Optional
from app.ai.base import IntentResult, SpeechTextResponse


class FallbackParser:
    """Deterministic natural language intent parser when external LLM is offline or unreachable."""

    def parse(self, query: str, available_devices: List[Dict[str, Any]]) -> Optional[IntentResult]:
        q = query.lower().strip()
        # Remove common wake prefix
        q = re.sub(r"^(hey\s+)?edith[,\s]*", "", q).strip()

        # Extract device hint
        device_hint = None
        for hint in ["laptop", "computer", "phone", "pc", "desktop", "workstation"]:
            if hint in q:
                device_hint = hint
                break

        # 1. Battery queries
        if "battery" in q:
            return IntentResult(
                tool_name="get_battery_status",
                capability="battery_status",
                device_hint=device_hint,
                parameters={}
            )

        # 2. System info queries
        if any(term in q for term in ["system info", "cpu", "ram", "memory", "specs", "hardware"]):
            return IntentResult(
                tool_name="get_system_info",
                capability="system_info",
                device_hint=device_hint,
                parameters={}
            )

        # 3. Screenshot
        if "screenshot" in q or "screen capture" in q:
            return IntentResult(
                tool_name="take_screenshot",
                capability="screenshot",
                device_hint=device_hint,
                parameters={}
            )

        # 4. Lock
        if "lock" in q:
            return IntentResult(
                tool_name="lock_device",
                capability="lock",
                device_hint=device_hint,
                parameters={}
            )

        # 5. Restart
        if "restart" in q or "reboot" in q:
            return IntentResult(
                tool_name="restart_device",
                capability="restart",
                device_hint=device_hint,
                parameters={}
            )

        # 6. Shutdown
        if "shut down" in q or "shutdown" in q or "turn off" in q or "power off" in q:
            return IntentResult(
                tool_name="shutdown_device",
                capability="shutdown",
                device_hint=device_hint,
                parameters={}
            )

        # 7. Volume controls
        if "volume up" in q or "increase volume" in q or "turn up" in q:
            return IntentResult(
                tool_name="control_volume",
                capability="volume_control",
                device_hint=device_hint,
                parameters={"action": "up", "steps": 2}
            )
        if "volume down" in q or "decrease volume" in q or "turn down" in q:
            return IntentResult(
                tool_name="control_volume",
                capability="volume_control",
                device_hint=device_hint,
                parameters={"action": "down", "steps": 2}
            )
        if "mute" in q or "unmute" in q:
            return IntentResult(
                tool_name="control_volume",
                capability="volume_control",
                device_hint=device_hint,
                parameters={"action": "mute"}
            )

        # 8. Media controls
        if any(term in q for term in ["play", "pause", "music"]):
            return IntentResult(
                tool_name="media_control",
                capability="media_control",
                device_hint=device_hint,
                parameters={"action": "play_pause"}
            )
        if "next track" in q or "skip track" in q or "next song" in q:
            return IntentResult(
                tool_name="media_control",
                capability="media_control",
                device_hint=device_hint,
                parameters={"action": "next"}
            )
        if "previous track" in q or "prev track" in q or "previous song" in q:
            return IntentResult(
                tool_name="media_control",
                capability="media_control",
                device_hint=device_hint,
                parameters={"action": "previous"}
            )

        # 9. Open application
        open_match = re.search(r"(?:open|launch|start)\s+([a-zA-Z0-9_\s]+?)(?:\s+(?:on|in)\s+.*)?$", q)
        if open_match:
            app_raw = open_match.group(1).strip()
            # Clean up target device words from app name
            for hint in ["laptop", "computer", "phone", "pc"]:
                app_raw = re.sub(rf"\b(my\s+)?{hint}\b", "", app_raw).strip()
            if app_raw:
                return IntentResult(
                    tool_name="open_application",
                    capability="open_application",
                    device_hint=device_hint,
                    parameters={"application": app_raw}
                )

        # 10. Close application
        close_match = re.search(r"(?:close|exit|terminate|kill)\s+([a-zA-Z0-9_\s]+?)(?:\s+(?:on|in)\s+.*)?$", q)
        if close_match:
            app_raw = close_match.group(1).strip()
            for hint in ["laptop", "computer", "phone", "pc"]:
                app_raw = re.sub(rf"\b(my\s+)?{hint}\b", "", app_raw).strip()
            if app_raw:
                return IntentResult(
                    tool_name="close_application",
                    capability="close_application",
                    device_hint=device_hint,
                    parameters={"application": app_raw}
                )

        return None

    def format_response(
        self,
        capability: str,
        device_name: str,
        result: Dict[str, Any],
        success: bool
    ) -> SpeechTextResponse:
        """Deterministic response formatter."""
        if not success:
            err_msg = result.get("message") or result.get("code") or "Operation failed"
            return SpeechTextResponse(
                speech_text=f"Sorry, {err_msg} on {device_name}.",
                display_text=f"Command failed on {device_name}: {err_msg}"
            )

        if capability == "battery_status":
            pct = result.get("percentage", 100)
            plugged = result.get("power_plugged", False)
            charging_str = "charging" if plugged else "discharging"
            speech = f"Your {device_name} battery is at {pct} percent and {charging_str}."
            display = f"{device_name} battery: {pct}% ({charging_str})"
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability == "open_application":
            app = result.get("application", "Application")
            speech = f"{app} is open on your {device_name}."
            display = f"Launched {app} on {device_name}."
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability == "close_application":
            speech = f"Closed the application on your {device_name}."
            display = result.get("message", f"Closed application on {device_name}.")
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability in ("volume_control", "volume_up", "volume_down", "mute"):
            speech = f"Adjusted volume on your {device_name}."
            display = result.get("message", f"Volume updated on {device_name}.")
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability == "media_control":
            speech = f"Media playback updated on your {device_name}."
            display = result.get("message", f"Media updated on {device_name}.")
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability in ("screenshot", "take_screenshot"):
            speech = f"Screenshot taken on your {device_name}."
            display = f"Screenshot captured from {device_name}."
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability in ("lock", "lock_device"):
            speech = f"Your {device_name} is now locked."
            display = f"Workstation locked on {device_name}."
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability in ("restart", "restart_device"):
            speech = f"Restarting your {device_name} now."
            display = f"Restart command delivered to {device_name}."
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability in ("shutdown", "shutdown_device"):
            speech = f"Shutting down your {device_name} now."
            display = f"Shutdown command delivered to {device_name}."
            return SpeechTextResponse(speech_text=speech, display_text=display)

        elif capability == "system_info":
            hostname = result.get("hostname", device_name)
            cpu = result.get("cpu", {}).get("usage_percent", 0)
            mem = result.get("memory", {}).get("usage_percent", 0)
            speech = f"{device_name} CPU is at {cpu} percent, memory at {mem} percent."
            display = f"{hostname} — CPU: {cpu}%, RAM: {mem}%"
            return SpeechTextResponse(speech_text=speech, display_text=display)

        return SpeechTextResponse(
            speech_text=f"Action completed on {device_name}.",
            display_text=f"Completed on {device_name}."
        )
