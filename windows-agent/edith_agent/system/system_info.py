import platform
import socket
from typing import Dict, Any
import psutil
from edith_agent.system.battery import get_battery_status


def get_system_info() -> Dict[str, Any]:
    """Collects comprehensive Windows system metrics."""
    cpu_count = psutil.cpu_count(logical=True)
    cpu_percent = psutil.cpu_percent(interval=0.1)

    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    battery = get_battery_status()

    return {
        "hostname": socket.gethostname(),
        "platform": "Windows",
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "cpu": {
            "cores": cpu_count,
            "usage_percent": cpu_percent
        },
        "memory": {
            "total_gb": round(mem.total / (1024 ** 3), 1),
            "used_gb": round(mem.used / (1024 ** 3), 1),
            "usage_percent": mem.percent
        },
        "disk": {
            "total_gb": round(disk.total / (1024 ** 3), 1),
            "free_gb": round(disk.free / (1024 ** 3), 1),
            "usage_percent": disk.percent
        },
        "battery": battery
    }
