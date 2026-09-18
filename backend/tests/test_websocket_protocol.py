import os
import json
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import WebSocketDisconnect

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-32chars-minimum-test"

from app.database.session import init_db, async_session_factory
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.device_repository import DeviceRepository
from app.websocket.connection_manager import ConnectionManager, manager
from app.api.v1.websocket import websocket_device_endpoint, websocket_client_endpoint
from app.auth.security import create_access_token


@pytest.mark.anyio
async def test_connection_manager_command_lifecycle():
    mgr = ConnectionManager()

    # 1. Command to offline device returns DEVICE_OFFLINE
    success, err = await mgr.send_command("offline-dev", "get_battery")
    assert not success
    assert err["code"] == "DEVICE_OFFLINE"

    # 2. Simulate connected device with mock websocket
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    mock_ws.send_text = AsyncMock()

    await mgr.connect_device(
        device_id="laptop-1",
        owner_id="usr-123",
        websocket=mock_ws,
        capabilities=["battery_status", "open_application"]
    )
    assert mgr.is_device_online("laptop-1")
    assert "battery_status" in mgr.get_device_capabilities("laptop-1")

    # 3. Dynamic capability update
    mgr.update_device_capabilities("laptop-1", ["battery_status", "open_application", "screenshot"])
    assert "screenshot" in mgr.get_device_capabilities("laptop-1")

    # 4. Command dispatch & correlation
    async def simulate_device_response():
        await asyncio.sleep(0.02)
        assert len(mgr.pending_commands) == 1
        req_id = list(mgr.pending_commands.keys())[0]
        mgr.handle_command_result(req_id, {
            "success": True,
            "data": {"battery": 92, "charging": False}
        })

    loop = asyncio.get_running_loop()
    loop.create_task(simulate_device_response())

    cmd_success, cmd_data = await mgr.send_command(
        device_id="laptop-1",
        capability="battery_status",
        parameters={},
        timeout=2.0
    )
    assert cmd_success is True
    assert cmd_data["battery"] == 92
    assert cmd_data["charging"] is False

    # 5. Command timeout handling
    t_success, t_data = await mgr.send_command(
        device_id="laptop-1",
        capability="battery_status",
        parameters={},
        timeout=0.05
    )
    assert t_success is False
    assert t_data["code"] == "COMMAND_TIMEOUT"

    # 6. Disconnect device
    await mgr.disconnect_device("laptop-1")
    assert not mgr.is_device_online("laptop-1")


@pytest.mark.anyio
async def test_device_websocket_endpoint_flow():
    await init_db()

    # Create user and device in database
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.create("ws_dev_user@example.com", "hash_123", "WS User")

        dev_repo = DeviceRepository(session)
        device = await dev_repo.create(
            device_id="laptop-real-ws",
            owner_id=user.id,
            name="Laptop Real",
            type="computer",
            platform="windows",
            device_token="tok_real_123",
            capabilities=["battery_status"]
        )
        await session.commit()

    # 1. Test rejected on invalid token
    mock_bad_ws = AsyncMock()
    mock_bad_ws.close = AsyncMock()
    await websocket_device_endpoint(mock_bad_ws, token="invalid_token")
    mock_bad_ws.close.assert_called_once()

    # 2. Test valid connection, register frame, heartbeat, and disconnect
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()
    sent_messages = []

    async def mock_send_text(msg):
        sent_messages.append(json.loads(msg))

    mock_ws.send_text = AsyncMock(side_effect=mock_send_text)

    # Sequence of incoming messages from device: register, heartbeat, then disconnect
    incoming_messages = [
        json.dumps({
            "type": "register",
            "request_id": "req-reg-1",
            "payload": {
                "device_id": "laptop-real-ws",
                "capabilities": ["battery_status", "volume_control"]
            }
        }),
        json.dumps({
            "type": "heartbeat",
            "request_id": "req-hb-1",
            "payload": {"device_id": "laptop-real-ws"}
        })
    ]

    async def mock_receive_text():
        if incoming_messages:
            return incoming_messages.pop(0)
        raise WebSocketDisconnect()

    mock_ws.receive_text = AsyncMock(side_effect=mock_receive_text)

    # Run endpoint loop
    await websocket_device_endpoint(mock_ws, token="tok_real_123")

    # Verify messages sent back to device
    types = [m["type"] for m in sent_messages]
    assert "register_ack" in types
    assert "heartbeat_ack" in types

    # Verify device status is back to offline after disconnect
    assert not manager.is_device_online("laptop-real-ws")


@pytest.mark.anyio
async def test_client_websocket_endpoint_flow():
    # 1. Invalid JWT rejected
    mock_bad_client_ws = AsyncMock()
    mock_bad_client_ws.close = AsyncMock()
    await websocket_client_endpoint(mock_bad_client_ws, token="invalid_jwt")
    mock_bad_client_ws.close.assert_called_once()

    # 2. Valid JWT accepted and ping/pong handled
    valid_token = create_access_token("user_client_1")
    mock_client_ws = AsyncMock()
    mock_client_ws.accept = AsyncMock()
    sent = []

    async def mock_send(msg):
        sent.append(json.loads(msg))

    mock_client_ws.send_text = AsyncMock(side_effect=mock_send)

    client_incoming = [
        json.dumps({"type": "ping"})
    ]

    async def mock_recv():
        if client_incoming:
            return client_incoming.pop(0)
        raise WebSocketDisconnect()

    mock_client_ws.receive_text = AsyncMock(side_effect=mock_recv)

    await websocket_client_endpoint(mock_client_ws, token=valid_token)

    assert len(sent) == 1
    assert sent[0]["type"] == "pong"
