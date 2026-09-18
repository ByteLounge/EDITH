import sys
from typing import List
import psutil


class CapabilityRegistry:
    @staticmethod
    def discover_capabilities() -> List[str]:
        """Discovers capabilities supported by the current Windows host."""
        capabilities = [
            "system_info",
            "open_application",
            "close_application",
            "screenshot"
        ]

        # Battery check
        try:
            battery = psutil.sensors_battery()
            if battery is not None:
                capabilities.append("battery_status")
        except Exception:
            pass

        # Windows-specific capabilities
        if sys.platform == "win32":
            capabilities.extend([
                "volume_control",
                "media_control",
                "lock",
                "restart",
                "shutdown"
            ])

        return capabilities
