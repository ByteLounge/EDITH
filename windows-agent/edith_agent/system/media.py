import sys
from typing import Dict, Any

VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_KEYUP = 0x0002


def _send_key_press(vk_code: int):
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
        ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def media_play_pause() -> Dict[str, Any]:
    """Toggles media playback play/pause."""
    _send_key_press(VK_MEDIA_PLAY_PAUSE)
    return {"message": "Media play/pause toggled"}


def media_next() -> Dict[str, Any]:
    """Skips to next media track."""
    _send_key_press(VK_MEDIA_NEXT_TRACK)
    return {"message": "Skipped to next track"}


def media_previous() -> Dict[str, Any]:
    """Returns to previous media track."""
    _send_key_press(VK_MEDIA_PREV_TRACK)
    return {"message": "Returned to previous track"}
