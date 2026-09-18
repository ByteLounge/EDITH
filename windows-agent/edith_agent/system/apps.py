import os
import sys
import subprocess
from typing import Dict, Any, Tuple
import psutil
from edith_agent.security.allowlist import allowlist


def open_application(app_name: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Safely launches an allowlisted application.
    NEVER allows raw shell commands or arbitrary executable paths.
    """
    executable = allowlist.resolve_application(app_name)
    if not executable:
        return False, {
            "code": "APPLICATION_NOT_ALLOWED",
            "message": f"Application '{app_name}' is not allowed or unrecognized. Allowed: {allowlist.list_allowed()}"
        }

    try:
        if sys.platform == "win32":
            os.startfile(executable)
        else:
            subprocess.Popen([executable], shell=False)

        return True, {
            "message": f"Successfully launched '{app_name}'.",
            "application": app_name,
            "executable": executable
        }
    except Exception as e:
        return False, {
            "code": "LAUNCH_FAILED",
            "message": f"Failed to launch '{app_name}': {str(e)}"
        }


def close_application(app_name: str) -> Tuple[bool, Dict[str, Any]]:
    """
    Terminates processes corresponding to an allowlisted application.
    """
    executable = allowlist.resolve_application(app_name)
    if not executable:
        return False, {
            "code": "APPLICATION_NOT_ALLOWED",
            "message": f"Application '{app_name}' is not in allowlist."
        }

    target_process = executable.lower()
    terminated_count = 0

    for proc in psutil.process_iter(["pid", "name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == target_process:
                proc.terminate()
                terminated_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    if terminated_count > 0:
        return True, {
            "message": f"Terminated {terminated_count} instance(s) of '{app_name}'.",
            "instances_terminated": terminated_count
        }
    else:
        return False, {
            "code": "PROCESS_NOT_RUNNING",
            "message": f"No running instance of '{app_name}' found."
        }
