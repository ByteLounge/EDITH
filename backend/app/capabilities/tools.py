from enum import Enum
from typing import Dict, Any, List


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


CAPABILITY_RISK_MAP = {
    "system_info": RiskLevel.LOW,
    "battery_status": RiskLevel.LOW,
    "open_application": RiskLevel.LOW,
    "volume_control": RiskLevel.LOW,
    "volume_up": RiskLevel.LOW,
    "volume_down": RiskLevel.LOW,
    "mute": RiskLevel.LOW,
    "media_control": RiskLevel.LOW,
    "media_play_pause": RiskLevel.LOW,
    "media_next": RiskLevel.LOW,
    "media_previous": RiskLevel.LOW,
    "screenshot": RiskLevel.MEDIUM,
    "take_screenshot": RiskLevel.MEDIUM,
    "close_application": RiskLevel.MEDIUM,
    "lock": RiskLevel.HIGH,
    "lock_device": RiskLevel.HIGH,
    "restart": RiskLevel.HIGH,
    "restart_device": RiskLevel.HIGH,
    "shutdown": RiskLevel.HIGH,
    "shutdown_device": RiskLevel.HIGH
}

# Standardized AI Tool Definitions
TOOL_DEFINITIONS = [
    {
        "name": "get_battery_status",
        "description": "Check current battery percentage and charging status of a device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID or name (e.g. laptop)"}
            },
            "required": ["device_id"]
        },
        "capability": "battery_status",
        "risk": RiskLevel.LOW
    },
    {
        "name": "get_system_info",
        "description": "Retrieve hardware specifications, CPU, memory, and disk usage of a device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID or name"}
            },
            "required": ["device_id"]
        },
        "capability": "system_info",
        "risk": RiskLevel.LOW
    },
    {
        "name": "open_application",
        "description": "Launch an allowlisted application (e.g., vscode, chrome, notepad, calculator, spotify) on the target device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"},
                "application": {"type": "string", "description": "Allowlisted application name (e.g. vscode, chrome)"}
            },
            "required": ["device_id", "application"]
        },
        "capability": "open_application",
        "risk": RiskLevel.LOW
    },
    {
        "name": "close_application",
        "description": "Close a running application on the target device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"},
                "application": {"type": "string", "description": "Application name to close"}
            },
            "required": ["device_id", "application"]
        },
        "capability": "close_application",
        "risk": RiskLevel.MEDIUM
    },
    {
        "name": "control_volume",
        "description": "Control audio volume (increase, decrease, mute/unmute) on the device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"},
                "action": {"type": "string", "enum": ["up", "down", "mute"], "description": "Volume action"},
                "steps": {"type": "integer", "description": "Number of volume steps (default: 2)"}
            },
            "required": ["device_id", "action"]
        },
        "capability": "volume_control",
        "risk": RiskLevel.LOW
    },
    {
        "name": "media_control",
        "description": "Control media playback (play/pause, next track, previous track) on the device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"},
                "action": {"type": "string", "enum": ["play_pause", "next", "previous"], "description": "Media action"}
            },
            "required": ["device_id", "action"]
        },
        "capability": "media_control",
        "risk": RiskLevel.LOW
    },
    {
        "name": "take_screenshot",
        "description": "Capture a screenshot of the target computer screen",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"}
            },
            "required": ["device_id"]
        },
        "capability": "screenshot",
        "risk": RiskLevel.MEDIUM
    },
    {
        "name": "lock_device",
        "description": "Lock the target computer's user session/workstation",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"}
            },
            "required": ["device_id"]
        },
        "capability": "lock",
        "risk": RiskLevel.HIGH
    },
    {
        "name": "restart_device",
        "description": "Safely restart the target device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"}
            },
            "required": ["device_id"]
        },
        "capability": "restart",
        "risk": RiskLevel.HIGH
    },
    {
        "name": "shutdown_device",
        "description": "Safely shut down the target device",
        "parameters": {
            "type": "object",
            "properties": {
                "device_id": {"type": "string", "description": "Target device ID"}
            },
            "required": ["device_id"]
        },
        "capability": "shutdown",
        "risk": RiskLevel.HIGH
    }
]


def get_tool_for_capability(capability: str) -> Dict[str, Any]:
    for tool in TOOL_DEFINITIONS:
        if tool["capability"] == capability or tool["name"] == capability:
            return tool
    return {}
