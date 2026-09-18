import json
import logging
from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from app.database.session import async_session_factory
from app.database.repositories.device_repository import DeviceRepository
from app.websocket.connection_manager import manager
from app.auth.security import decode_token

logger = logging.getLogger("edith.ws_router")
router = APIRouter(tags=["WebSockets"])


@router.websocket("/ws/device")
async def websocket_device_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="Device authentication token")
):
    # Authenticate device token
    async with async_session_factory() as session:
        repo = DeviceRepository(session)
        device = await repo.get_by_token(token)
        if not device:
            logger.warning(f"Rejected device WebSocket connection: invalid token {token[:10]}...")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return

        device_id = device.device_id
        owner_id = device.owner_id
        capabilities = device.capabilities or []

        # Update database status to online
        await repo.update_status(device_id, "online")
        await session.commit()

    # Register in ConnectionManager
    await manager.connect_device(device_id, owner_id, websocket, capabilities)

    try:
        while True:
            text_data = await websocket.receive_text()
            try:
                message = json.loads(text_data)
            except json.JSONDecodeError:
                logger.warning(f"Device {device_id} sent invalid JSON")
                continue

            msg_type = message.get("type")
            request_id = message.get("request_id")
            payload = message.get("payload", {})

            if msg_type == "register":
                # Dynamic capability update
                new_caps = payload.get("capabilities", [])
                manager.update_device_capabilities(device_id, new_caps)
                async with async_session_factory() as session:
                    repo = DeviceRepository(session)
                    await repo.update_capabilities(device_id, new_caps)
                    await session.commit()

                ack = {
                    "type": "register_ack",
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "payload": {
                        "status": "authenticated",
                        "device_id": device_id,
                        "heartbeat_interval_seconds": 30
                    }
                }
                await websocket.send_text(json.dumps(ack))

            elif msg_type == "heartbeat":
                manager.update_device_heartbeat(device_id)
                ack = {
                    "type": "heartbeat_ack",
                    "request_id": request_id,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "payload": {"status": "ok"}
                }
                await websocket.send_text(json.dumps(ack))

            elif msg_type == "command_result":
                if request_id:
                    manager.handle_command_result(request_id, payload)
                else:
                    logger.warning(f"Device {device_id} sent command_result without request_id")

            elif msg_type == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.now(timezone.utc).isoformat()}))

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for device {device_id}")
    except Exception as e:
        logger.error(f"Error in device WebSocket loop for {device_id}: {e}")
    finally:
        await manager.disconnect_device(device_id)
        async with async_session_factory() as session:
            repo = DeviceRepository(session)
            await repo.update_status(device_id, "offline")
            await session.commit()


@router.websocket("/ws/client")
async def websocket_client_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="User access JWT token")
):
    # Authenticate user JWT
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        logger.warning("Rejected client WebSocket connection: invalid JWT")
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    user_id = payload.get("sub")
    if not user_id:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await manager.connect_client(user_id, websocket)

    try:
        while True:
            text_data = await websocket.receive_text()
            try:
                message = json.loads(text_data)
            except json.JSONDecodeError:
                continue

            msg_type = message.get("type")
            if msg_type == "ping":
                await websocket.send_text(json.dumps({
                    "type": "pong",
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }))

    except WebSocketDisconnect:
        manager.disconnect_client(user_id, websocket)
    except Exception as e:
        logger.error(f"Error in client WebSocket loop for user {user_id}: {e}")
        manager.disconnect_client(user_id, websocket)
