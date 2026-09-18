import asyncio
import json
import logging
import uuid
from datetime import datetime, timezone
import websockets
from edith_agent.config.settings import agent_settings
from edith_agent.capabilities.registry import CapabilityRegistry
from edith_agent.commands.dispatcher import dispatcher

logger = logging.getLogger("edith.agent.ws")


class AgentWebSocketClient:
    def __init__(self, server_url: str, device_token: str, device_id: str):
        self.server_url = server_url
        self.device_token = device_token
        self.device_id = device_id
        self.running = False
        self.websocket = None

    async def start(self):
        self.running = True
        retry_delay = 2.0
        max_retry_delay = 30.0

        # Build WS URL
        ws_url = f"{self.server_url}/ws/device?token={self.device_token}"
        if ws_url.startswith("http://"):
            ws_url = ws_url.replace("http://", "ws://", 1)
        elif ws_url.startswith("https://"):
            ws_url = ws_url.replace("https://", "wss://", 1)

        logger.info(f"Connecting to EDITH Core at: {ws_url.split('?')[0]}")

        while self.running:
            try:
                async with websockets.connect(ws_url) as ws:
                    self.websocket = ws
                    logger.info("Connected successfully to EDITH Core!")
                    retry_delay = 2.0  # Reset backoff on successful connect

                    # 1. Send handshake register frame
                    await self._send_register()

                    # 2. Launch heartbeat background loop
                    heartbeat_task = asyncio.create_task(self._heartbeat_loop())

                    # 3. Message listen loop
                    try:
                        async for message in ws:
                            await self._handle_message(message)
                    finally:
                        heartbeat_task.cancel()

            except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
                logger.warning(f"Connection lost or unreachable: {e}. Reconnecting in {retry_delay:.1f}s...")
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, max_retry_delay)
            except Exception as e:
                logger.error(f"Unexpected connection error: {e}", exc_info=True)
                await asyncio.sleep(retry_delay)
                retry_delay = min(retry_delay * 1.5, max_retry_delay)

    def stop(self):
        self.running = False

    async def _send_register(self):
        capabilities = CapabilityRegistry.discover_capabilities()
        frame = {
            "type": "register",
            "request_id": str(uuid.uuid4()),
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "payload": {
                "device_id": self.device_id,
                "name": agent_settings.DEVICE_NAME,
                "type": agent_settings.DEVICE_TYPE,
                "platform": agent_settings.PLATFORM,
                "version": agent_settings.VERSION,
                "capabilities": capabilities
            }
        }
        await self.websocket.send(json.dumps(frame))
        logger.info(f"Sent registration with {len(capabilities)} capabilities: {capabilities}")

    async def _heartbeat_loop(self):
        while self.running and self.websocket:
            try:
                await asyncio.sleep(agent_settings.HEARTBEAT_INTERVAL_SECONDS)
                frame = {
                    "type": "heartbeat",
                    "request_id": str(uuid.uuid4()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "payload": {
                        "device_id": self.device_id
                    }
                }
                await self.websocket.send(json.dumps(frame))
                logger.debug("Sent heartbeat ping")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Failed to send heartbeat: {e}")
                break

    async def _handle_message(self, raw_message: str):
        try:
            message = json.loads(raw_message)
        except json.JSONDecodeError:
            logger.warning("Received non-JSON frame from Core")
            return

        msg_type = message.get("type")
        request_id = message.get("request_id")
        payload = message.get("payload", {})

        if msg_type == "command":
            capability = payload.get("capability")
            parameters = payload.get("parameters", {})

            # Execute capability via dispatcher
            success, result_data = await dispatcher.execute(capability, parameters)

            # Build command_result response frame
            response_frame = {
                "type": "command_result",
                "request_id": request_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "payload": {
                    "device_id": self.device_id,
                    "capability": capability,
                    "success": success,
                    "data" if success else "error": result_data
                }
            }
            await self.websocket.send(json.dumps(response_frame))
            logger.info(f"Handled command '{capability}', success={success}")

        elif msg_type == "register_ack":
            logger.info("Core acknowledged registration.")

        elif msg_type == "heartbeat_ack":
            logger.debug("Core acknowledged heartbeat.")
