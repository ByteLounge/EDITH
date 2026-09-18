import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Set, Optional, Any, Tuple
from fastapi import WebSocket, status

logger = logging.getLogger("edith.websocket")


class DeviceSession:
    def __init__(self, device_id: str, owner_id: str, websocket: WebSocket, capabilities: list):
        self.device_id = device_id
        self.owner_id = owner_id
        self.websocket = websocket
        self.capabilities = capabilities
        self.last_heartbeat = datetime.now(timezone.utc)


class ConnectionManager:
    def __init__(self):
        # Active device connections: device_id -> DeviceSession
        self.active_devices: Dict[str, DeviceSession] = {}
        # Active client connections: owner_id -> Set[WebSocket]
        self.active_clients: Dict[str, Set[WebSocket]] = {}
        # In-flight command futures: request_id -> asyncio.Future
        self.pending_commands: Dict[str, asyncio.Future] = {}
        # Pending confirmation requests: confirmation_token -> dict
        self.pending_confirmations: Dict[str, dict] = {}

    async def connect_client(self, owner_id: str, websocket: WebSocket):
        await websocket.accept()
        if owner_id not in self.active_clients:
            self.active_clients[owner_id] = set()
        self.active_clients[owner_id].add(websocket)
        logger.info(f"Client connected for user {owner_id}. Total clients: {len(self.active_clients[owner_id])}")

    def disconnect_client(self, owner_id: str, websocket: WebSocket):
        if owner_id in self.active_clients:
            self.active_clients[owner_id].discard(websocket)
            if not self.active_clients[owner_id]:
                del self.active_clients[owner_id]
        logger.info(f"Client disconnected for user {owner_id}")

    async def connect_device(
        self,
        device_id: str,
        owner_id: str,
        websocket: WebSocket,
        capabilities: Optional[list] = None
    ):
        await websocket.accept()
        session = DeviceSession(
            device_id=device_id,
            owner_id=owner_id,
            websocket=websocket,
            capabilities=capabilities or []
        )
        self.active_devices[device_id] = session
        logger.info(f"Device {device_id} connected (owner={owner_id})")

        # Broadcast online status to user's connected clients
        await self.broadcast_to_clients(owner_id, {
            "type": "device_status",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "device_id": device_id,
                "status": "online",
                "capabilities": session.capabilities
            }
        })

    async def disconnect_device(self, device_id: str):
        session = self.active_devices.pop(device_id, None)
        if session:
            logger.info(f"Device {device_id} disconnected (owner={session.owner_id})")
            # Fail any in-flight commands for this device
            for req_id, fut in list(self.pending_commands.items()):
                if not fut.done():
                    fut.set_exception(ConnectionError(f"Device {device_id} disconnected during command execution."))

            # Broadcast offline status to user's connected clients
            await self.broadcast_to_clients(session.owner_id, {
                "type": "device_status",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {
                    "device_id": device_id,
                    "status": "offline"
                }
            })

    def is_device_online(self, device_id: str) -> bool:
        return device_id in self.active_devices

    def get_device_capabilities(self, device_id: str) -> list:
        session = self.active_devices.get(device_id)
        return session.capabilities if session else []

    def update_device_capabilities(self, device_id: str, capabilities: list):
        if device_id in self.active_devices:
            self.active_devices[device_id].capabilities = capabilities

    def update_device_heartbeat(self, device_id: str):
        if device_id in self.active_devices:
            self.active_devices[device_id].last_heartbeat = datetime.now(timezone.utc)

    async def broadcast_to_clients(self, owner_id: str, message: dict):
        clients = self.active_clients.get(owner_id, set()).copy()
        if not clients:
            return
        payload = json.dumps(message)
        dead_clients = []
        for ws in clients:
            try:
                await ws.send_text(payload)
            except Exception:
                dead_clients.append(ws)
        for dead_ws in dead_clients:
            self.disconnect_client(owner_id, dead_ws)

    async def send_command(
        self,
        device_id: str,
        capability: str,
        parameters: Optional[dict] = None,
        timeout: float = 12.0
    ) -> Tuple[bool, Any]:
        """
        Sends a command to the device and awaits the result asynchronously via request_id correlation.
        Returns (success: bool, data_or_error: dict).
        """
        if device_id not in self.active_devices:
            return False, {
                "code": "DEVICE_OFFLINE",
                "message": f"Device '{device_id}' is currently offline."
            }

        session = self.active_devices[device_id]
        request_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        future: asyncio.Future = loop.create_future()
        self.pending_commands[request_id] = future

        message = {
            "type": "command",
            "request_id": request_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "device_id": device_id,
                "capability": capability,
                "parameters": parameters or {}
            }
        }

        try:
            await session.websocket.send_text(json.dumps(message))
            # Wait for device response with timeout
            response_payload = await asyncio.wait_for(future, timeout=timeout)
            return response_payload.get("success", False), response_payload.get("data") or response_payload.get("error")
        except asyncio.TimeoutError:
            return False, {
                "code": "COMMAND_TIMEOUT",
                "message": f"Device '{device_id}' did not respond within {timeout} seconds."
            }
        except Exception as e:
            return False, {
                "code": "DEVICE_EXECUTION_FAILED",
                "message": str(e)
            }
        finally:
            self.pending_commands.pop(request_id, None)

    def handle_command_result(self, request_id: str, payload: dict):
        """Resolves the pending future corresponding to request_id."""
        future = self.pending_commands.get(request_id)
        if future and not future.done():
            future.set_result(payload)


# Global singleton instance for the application
manager = ConnectionManager()
