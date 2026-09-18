import logging
from typing import Dict, Any, Tuple
from edith_agent.system.system_info import get_system_info
from edith_agent.system.battery import get_battery_status
from edith_agent.system.volume import volume_up, volume_down, toggle_mute
from edith_agent.system.media import media_play_pause, media_next, media_previous
from edith_agent.system.apps import open_application, close_application
from edith_agent.system.power import lock_workstation, restart_system, shutdown_system
from edith_agent.system.screen import take_screenshot

logger = logging.getLogger("edith.agent.dispatcher")


class CommandDispatcher:
    def __init__(self):
        pass

    async def execute(self, capability: str, parameters: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Dispatches validated capability execution to concrete system implementations.
        Returns (success: bool, result_payload: dict).
        """
        logger.info(f"Executing capability: {capability} with params: {parameters}")
        try:
            # 1. System Telemetry
            if capability == "system_info":
                return True, get_system_info()

            elif capability == "battery_status":
                return True, get_battery_status()

            # 2. Application Control
            elif capability == "open_application":
                app_name = parameters.get("application") or parameters.get("app")
                if not app_name:
                    return False, {"code": "MISSING_PARAMETER", "message": "Parameter 'application' is required."}
                return open_application(app_name)

            elif capability == "close_application":
                app_name = parameters.get("application") or parameters.get("app")
                if not app_name:
                    return False, {"code": "MISSING_PARAMETER", "message": "Parameter 'application' is required."}
                return close_application(app_name)

            # 3. Audio & Volume
            elif capability in ("volume_up", "increase_volume"):
                steps = int(parameters.get("steps", 2))
                return True, volume_up(steps)

            elif capability in ("volume_down", "decrease_volume"):
                steps = int(parameters.get("steps", 2))
                return True, volume_down(steps)

            elif capability in ("mute", "toggle_mute"):
                return True, toggle_mute()

            elif capability == "volume_control":
                action = parameters.get("action", "up")
                steps = int(parameters.get("steps", 2))
                if action == "down":
                    return True, volume_down(steps)
                elif action in ("mute", "unmute"):
                    return True, toggle_mute()
                else:
                    return True, volume_up(steps)

            # 4. Media Controls
            elif capability in ("media_play_pause", "play_music", "pause_music"):
                return True, media_play_pause()

            elif capability in ("media_next", "next_track"):
                return True, media_next()

            elif capability in ("media_previous", "previous_track"):
                return True, media_previous()

            elif capability == "media_control":
                action = parameters.get("action", "play_pause")
                if action in ("next", "skip"):
                    return True, media_next()
                elif action in ("previous", "prev"):
                    return True, media_previous()
                else:
                    return True, media_play_pause()

            # 5. Screen Capture
            elif capability in ("screenshot", "take_screenshot"):
                return take_screenshot()

            # 6. Power & Security
            elif capability in ("lock", "lock_device"):
                return lock_workstation()

            elif capability in ("restart", "restart_device"):
                return restart_system()

            elif capability in ("shutdown", "shutdown_device"):
                return shutdown_system()

            else:
                return False, {
                    "code": "CAPABILITY_NOT_SUPPORTED",
                    "message": f"Windows Agent does not support capability '{capability}'."
                }

        except Exception as e:
            logger.error(f"Execution error for capability '{capability}': {e}", exc_info=True)
            return False, {
                "code": "EXECUTION_ERROR",
                "message": f"Unexpected error during '{capability}': {str(e)}"
            }


dispatcher = CommandDispatcher()
