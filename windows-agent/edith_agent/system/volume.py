import sys
from typing import Dict, Any

VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
KEYEVENTF_KEYUP = 0x0002


def _send_key_press(vk_code: int):
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def volume_up(steps: int = 2) -> Dict[str, Any]:
    """Increases system master volume."""
    for _ in range(max(1, min(steps, 10))):
        _send_key_press(VK_VOLUME_UP)
    return {"message": "Volume increased", "steps": steps}


def volume_down(steps: int = 2) -> Dict[str, Any]:
    """Decreases system master volume."""
    for _ in range(max(1, min(steps, 10))):
        _send_key_press(VK_VOLUME_DOWN)
    return {"message": "Volume decreased", "steps": steps}


def toggle_mute() -> Dict[str, Any]:
    """Toggles master volume mute."""
    _send_key_press(VK_VOLUME_MUTE)
    return {"message": "Mute toggled"}
