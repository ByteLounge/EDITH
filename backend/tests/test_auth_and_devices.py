import os
import pytest
from httpx import AsyncClient, ASGITransport

# Configure in-memory SQLite for testing
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-32chars-minimum-test"

from app.main import app
from app.database.session import init_db, async_session_factory
from app.services.device_service import DeviceService
from app.database.repositories.user_repository import UserRepository
from app.database.repositories.device_repository import DeviceRepository


@pytest.mark.anyio
async def test_health_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["service"] == "EDITH Core"


@pytest.mark.anyio
async def test_auth_flow():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Register user
        reg_payload = {
            "email": "yash@example.com",
            "password": "Password123!",
            "full_name": "Yash"
        }
        res = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res.status_code == 201
        data = res.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["email"] == "yash@example.com"
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]

        # 2. Duplicate registration should fail
        res_dup = await client.post("/api/v1/auth/register", json=reg_payload)
        assert res_dup.status_code == 400

        # 3. Login with correct credentials
        login_payload = {
            "email": "yash@example.com",
            "password": "Password123!"
        }
        res_login = await client.post("/api/v1/auth/login", json=login_payload)
        assert res_login.status_code == 200
        assert "access_token" in res_login.json()

        # 4. Login with incorrect credentials
        res_bad_login = await client.post("/api/v1/auth/login", json={"email": "yash@example.com", "password": "Wrong"})
        assert res_bad_login.status_code == 401

        # 5. Get current user profile
        headers = {"Authorization": f"Bearer {access_token}"}
        res_me = await client.get("/api/v1/auth/me", headers=headers)
        assert res_me.status_code == 200
        assert res_me.json()["email"] == "yash@example.com"
        assert res_me.json()["full_name"] == "Yash"

        # 6. Refresh token
        res_refresh = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
        assert res_refresh.status_code == 200
        assert "access_token" in res_refresh.json()


@pytest.mark.anyio
async def test_device_pairing_and_management():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Register user
        reg_res = await client.post("/api/v1/auth/register", json={
            "email": "device_tester@example.com",
            "password": "Password123!",
            "full_name": "Device Tester"
        })
        token = reg_res.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Generate pairing code
        pair_res = await client.post("/api/v1/devices/pair/code", headers=headers)
        assert pair_res.status_code == 201
        pairing_code = pair_res.json()["pairing_code"]
        assert len(pairing_code) == 6

        # 2. Redeem pairing code (Windows Agent)
        claim_payload = {
            "pairing_code": pairing_code,
            "device_id": "laptop-main",
            "device_name": "Yash Laptop",
            "device_type": "computer",
            "platform": "windows",
            "capabilities": ["battery_status", "open_application", "screenshot", "lock"],
            "version": "1.0.0"
        }
        claim_res = await client.post("/api/v1/devices/pair/claim", json=claim_payload)
        assert claim_res.status_code == 200
        claim_data = claim_res.json()
        assert claim_data["device_id"] == "laptop-main"
        assert "device_token" in claim_data
        assert claim_data["ws_url"].startswith("/ws/device?token=")

        # 3. Trying to reuse the same code should fail
        reuse_res = await client.post("/api/v1/devices/pair/claim", json=claim_payload)
        assert reuse_res.status_code == 400

        # 4. List devices for user
        devs_res = await client.get("/api/v1/devices", headers=headers)
        assert devs_res.status_code == 200
        dev_list = devs_res.json()
        assert len(dev_list) == 1
        assert dev_list[0]["device_id"] == "laptop-main"
        assert dev_list[0]["name"] == "Yash Laptop"
        assert "battery_status" in dev_list[0]["capabilities"]

        # 5. Rename device
        rename_res = await client.patch("/api/v1/devices/laptop-main", json={"name": "Primary Laptop"}, headers=headers)
        assert rename_res.status_code == 200
        assert rename_res.json()["name"] == "Primary Laptop"

        # 6. Get single device
        single_res = await client.get("/api/v1/devices/laptop-main", headers=headers)
        assert single_res.status_code == 200
        assert single_res.json()["name"] == "Primary Laptop"


@pytest.mark.anyio
async def test_natural_language_device_resolution():
    await init_db()
    async with async_session_factory() as session:
        service = DeviceService(session)
        user_repo = UserRepository(session)

        # Create user
        user = await user_repo.create("nl_user@example.com", "dummy_hash", "NL User")

        # 1. No devices registered
        dev, err = await service.resolve_device_by_hint(user.id, "laptop")
        assert dev is None
        assert "No devices" in err

        # Create a laptop device
        dev_repo = DeviceRepository(session)
        laptop = await dev_repo.create(
            device_id="laptop-1",
            owner_id=user.id,
            name="Yash Laptop",
            type="computer",
            platform="windows",
            device_token="tok_1",
            capabilities=["battery_status"]
        )

        # 2. Single device exists, empty hint -> should resolve directly
        dev, err = await service.resolve_device_by_hint(user.id, None)
        assert dev is not None
        assert dev.device_id == "laptop-1"

        # 3. Hint matches "laptop"
        dev, err = await service.resolve_device_by_hint(user.id, "my laptop")
        assert dev is not None
        assert dev.device_id == "laptop-1"

        # 4. Hint matches "computer"
        dev, err = await service.resolve_device_by_hint(user.id, "on my computer")
        assert dev is not None
        assert dev.device_id == "laptop-1"

        # Add a phone device
        phone = await dev_repo.create(
            device_id="phone-1",
            owner_id=user.id,
            name="Pixel Phone",
            type="phone",
            platform="android",
            device_token="tok_2",
            capabilities=["ring"]
        )

        # 5. Resolving "phone" should resolve to phone-1
        dev, err = await service.resolve_device_by_hint(user.id, "phone")
        assert dev is not None
        assert dev.device_id == "phone-1"

        # 6. Resolving "laptop" should resolve to laptop-1
        dev, err = await service.resolve_device_by_hint(user.id, "laptop")
        assert dev is not None
        assert dev.device_id == "laptop-1"

        # 7. Unmatched hint
        dev, err = await service.resolve_device_by_hint(user.id, "television")
        assert dev is None
        assert "couldn't find" in err
