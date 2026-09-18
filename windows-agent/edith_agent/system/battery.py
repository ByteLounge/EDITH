from typing import Dict, Any
import psutil


def get_battery_status() -> Dict[str, Any]:
    """Retrieves current battery telemetry."""
    battery = psutil.sensors_battery()
    if battery is None:
        return {
            "has_battery": False,
            "percentage": 100,
            "power_plugged": True,
            "status_text": "AC Power (No battery detected)"
        }

    plugged_str = "plugged in" if battery.power_plugged else "on battery"
    return {
        "has_battery": True,
        "percentage": round(battery.percent),
        "power_plugged": battery.power_plugged,
        "time_left_seconds": battery.secsleft if battery.secsleft != psutil.POWER_TIME_UNLIMITED else None,
        "status_text": f"{round(battery.percent)}% ({plugged_str})"
    }
