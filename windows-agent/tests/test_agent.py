import sys
from pathlib import Path
import pytest

# Ensure windows-agent is in sys.path
agent_dir = Path(__file__).resolve().parent.parent
if str(agent_dir) not in sys.path:
    sys.path.insert(0, str(agent_dir))

from edith_agent.security.allowlist import ApplicationAllowlist
from edith_agent.capabilities.registry import CapabilityRegistry
from edith_agent.system.system_info import get_system_info
from edith_agent.system.battery import get_battery_status
from edith_agent.commands.dispatcher import CommandDispatcher
from edith_agent.security.credentials import CredentialStore


def test_application_allowlist_security():
    allowlist = ApplicationAllowlist()

    # 1. Valid allowlisted apps
    assert allowlist.resolve_application("vscode") == "Code.exe"
    assert allowlist.resolve_application("chrome") == "chrome.exe"
    assert allowlist.resolve_application("notepad") == "notepad.exe"
    assert allowlist.resolve_application("calculator") == "calc.exe"

    # 2. Case insensitivity and alias mapping
    assert allowlist.resolve_application("VS Code") == "Code.exe"
    assert allowlist.resolve_application("Visual Studio Code") == "Code.exe"
    assert allowlist.resolve_application("Google Chrome") == "chrome.exe"
    assert allowlist.resolve_application("calc") == "calc.exe"

    # 3. Disallowed / untrusted applications
    assert allowlist.resolve_application("malware.exe") is None
    assert allowlist.resolve_application("powershell") is None
    assert allowlist.resolve_application("cmd") is None
    assert allowlist.resolve_application("bash") is None

    # 4. Injection and shell character defense
    assert allowlist.resolve_application("vscode; rm -rf") is None
    assert allowlist.resolve_application("chrome && notepad") is None
    assert allowlist.resolve_application("calc.exe | powershell") is None
    assert allowlist.resolve_application("../../../evil.exe") is None
    assert allowlist.resolve_application("`whoami`") is None


def test_capability_discovery():
    caps = CapabilityRegistry.discover_capabilities()
    assert "system_info" in caps
    assert "open_application" in caps
    assert "close_application" in caps
    assert "screenshot" in caps


def test_system_telemetry():
    battery = get_battery_status()
    assert "has_battery" in battery
    assert "percentage" in battery

    info = get_system_info()
    assert "hostname" in info
    assert "cpu" in info
    assert "memory" in info
    assert "disk" in info
    assert info["cpu"]["cores"] > 0


@pytest.mark.anyio
async def test_command_dispatcher_routing():
    dispatcher = CommandDispatcher()

    # 1. System info execution
    success, data = await dispatcher.execute("system_info", {})
    assert success is True
    assert "hostname" in data

    # 2. Unallowlisted application rejection
    success, err = await dispatcher.execute("open_application", {"application": "untrusted_payload"})
    assert success is False
    assert err["code"] == "APPLICATION_NOT_ALLOWED"

    # 3. Missing application parameter
    success, err = await dispatcher.execute("open_application", {})
    assert success is False
    assert err["code"] == "MISSING_PARAMETER"

    # 4. Unsupported capability
    success, err = await dispatcher.execute("unsupported_future_cap", {})
    assert success is False
    assert err["code"] == "CAPABILITY_NOT_SUPPORTED"

    # 5. Volume control simulation
    success, data = await dispatcher.execute("volume_control", {"action": "up", "steps": 2})
    assert success is True

    # 6. Media control simulation
    success, data = await dispatcher.execute("media_control", {"action": "play_pause"})
    assert success is True


def test_credential_store(tmp_path):
    store_file = tmp_path / "creds.json"
    store = CredentialStore(storage_path=store_file)

    assert store.get_token() is None
    store.save_device_credentials("laptop-test", "sec_token_999")

    assert store.get_token() == "sec_token_999"
    assert store.get_device_id() == "laptop-test"

    store.clear()
    assert store.get_token() is None
