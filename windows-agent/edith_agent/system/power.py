import sys
import subprocess
from typing import Dict, Any, Tuple


def lock_workstation() -> Tuple[bool, Dict[str, Any]]:
    """Locks the current Windows user workstation session."""
    if sys.platform != "win32":
        return False, {"code": "UNSUPPORTED_PLATFORM", "message": "Lock is only supported on Windows."}

    import ctypes
    result = ctypes.windll.user32.LockWorkStation()
    if result:
        return True, {"message": "Workstation locked successfully."}
    else:
        return False, {"code": "LOCK_FAILED", "message": "Failed to lock workstation."}


def restart_system() -> Tuple[bool, Dict[str, Any]]:
    """Schedules a safe Windows restart (5-second grace period)."""
    if sys.platform != "win32":
        return False, {"code": "UNSUPPORTED_PLATFORM", "message": "Restart is only supported on Windows."}

    try:
        subprocess.run(["shutdown.exe", "/r", "/t", "5"], check=True, capture_output=True)
        return True, {"message": "Windows restart initiated (in 5 seconds)."}
    except Exception as e:
        return False, {"code": "RESTART_FAILED", "message": str(e)}


def shutdown_system() -> Tuple[bool, Dict[str, Any]]:
    """Schedules a safe Windows shutdown (5-second grace period)."""
    if sys.platform != "win32":
        return False, {"code": "UNSUPPORTED_PLATFORM", "message": "Shutdown is only supported on Windows."}

    try:
        subprocess.run(["shutdown.exe", "/s", "/t", "5"], check=True, capture_output=True)
        return True, {"message": "Windows shutdown initiated (in 5 seconds)."}
    except Exception as e:
        return False, {"code": "SHUTDOWN_FAILED", "message": str(e)}
