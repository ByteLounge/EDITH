import os
import json
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-32chars-minimum-test"
os.environ["AI_PROVIDER"] = "ollama"

from app.main import app
from app.database.session import init_db, async_session_factory
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.device_repository import DeviceRepository
from app.websocket.connection_manager import manager
from app.auth.security import create_access_token


@pytest.mark.anyio
async def test_full_command_flow_low_risk():
    await init_db()

    # Create user and device
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.create("cmd_user@example.com", "hash_pw", "Cmd User")

        dev_repo = DeviceRepository(session)
        device = await dev_repo.create(
            device_id="laptop-yash",
            owner_id=user.id,
            name="Yash Laptop",
            type="computer",
            platform="windows",
            device_token="dev_tok_cmd_1",
            capabilities=["battery_status", "open_application", "lock", "shutdown"]
        )
        await session.commit()
        user_id = user.id

    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)

    # 1. Device is offline: should return offline error
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/commands/process", json={"query": "What is my laptop battery?"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "failed"
        assert "offline" in data["speech_response"].lower()

    # 2. Connect device to ConnectionManager with auto-responding mock socket
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()

    async def mock_device_handler(raw_msg):
        msg = json.loads(raw_msg)
        if msg.get("type") == "command":
            req_id = msg.get("request_id")
            cap = msg.get("payload", {}).get("capability")
            if cap == "battery_status":
                manager.handle_command_result(req_id, {
                    "success": True,
                    "data": {"percentage": 64, "power_plugged": False}
                })
            elif cap == "open_application":
                manager.handle_command_result(req_id, {
                    "success": True,
                    "data": {"application": "vscode", "message": "Launched vscode"}
                })

    mock_ws.send_text = AsyncMock(side_effect=mock_device_handler)

    await manager.connect_device(
        device_id="laptop-yash",
        owner_id=user_id,
        websocket=mock_ws,
        capabilities=["battery_status", "open_application", "lock", "shutdown"]
    )

    # 3. Process battery command
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post("/api/v1/commands/process", json={"query": "EDITH, what's my laptop battery?"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["capability"] == "battery_status"
        assert "64 percent" in data["speech_response"]

        # 4. Process open VS Code command
        res_app = await client.post("/api/v1/commands/process", json={"query": "EDITH, open VS Code on my laptop"}, headers=headers)
        assert res_app.status_code == 200
        app_data = res_app.json()
        assert app_data["status"] == "completed"
        assert app_data["capability"] == "open_application"
        assert "vscode is open" in app_data["speech_response"].lower()


@pytest.mark.anyio
async def test_high_risk_confirmation_flow():
    await init_db()

    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        user = await user_repo.create("risk_user@example.com", "hash_pw", "Risk User")

        dev_repo = DeviceRepository(session)
        device = await dev_repo.create(
            device_id="laptop-risk",
            owner_id=user.id,
            name="Yash Laptop",
            type="computer",
            platform="windows",
            device_token="dev_tok_risk_1",
            capabilities=["lock", "shutdown", "restart"]
        )
        await session.commit()
        user_id = user.id

    token = create_access_token(user_id)
    headers = {"Authorization": f"Bearer {token}"}
    transport = ASGITransport(app=app)

    # Connect device with auto-responder
    mock_ws = AsyncMock()
    mock_ws.accept = AsyncMock()

    async def mock_shutdown_handler(raw_msg):
        msg = json.loads(raw_msg)
        if msg.get("type") == "command":
            req_id = msg.get("request_id")
            manager.handle_command_result(req_id, {
                "success": True,
                "data": {"message": "Windows shutdown initiated"}
            })

    mock_ws.send_text = AsyncMock(side_effect=mock_shutdown_handler)

    await manager.connect_device(
        device_id="laptop-risk",
        owner_id=user_id,
        websocket=mock_ws,
        capabilities=["lock", "shutdown", "restart"]
    )

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Request high-risk shutdown
        res = await client.post("/api/v1/commands/process", json={"query": "EDITH, shut down my laptop"}, headers=headers)
        assert res.status_code == 200
        data = res.json()
        assert data["requires_confirmation"] is True
        assert data["status"] == "confirmation_required"
        assert data["confirmation_token"] is not None
        assert "Shutting down" in data["confirmation_prompt"]
        conf_token = data["confirmation_token"]

        # 2. Confirm execution
        res_conf = await client.post("/api/v1/commands/confirm", json={"confirmation_token": conf_token, "confirmed": True}, headers=headers)
        assert res_conf.status_code == 200
        conf_data = res_conf.json()
        assert conf_data["status"] == "completed"
        assert "Shutting down" in conf_data["speech_response"]

        # 3. Check Command History
        res_hist = await client.get("/api/v1/commands/history", headers=headers)
        assert res_hist.status_code == 200
        history = res_hist.json()
        assert len(history) >= 1
        assert history[0]["status"] == "completed"

        # 4. Clear History
        res_del = await client.delete("/api/v1/commands/history", headers=headers)
        assert res_del.status_code == 204

        res_empty = await client.get("/api/v1/commands/history", headers=headers)
        assert len(res_empty.json()) == 0
