import uuid
import logging
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.repositories.device_repository import DeviceRepository
from app.database.repositories.command_repository import CommandRepository
from app.services.device_service import DeviceService
from app.ai.factory import get_ai_provider
from app.capabilities.tools import TOOL_DEFINITIONS
from app.permissions.risk import confirmation_manager
from app.websocket.connection_manager import manager
from app.commands.schemas import ProcessCommandResponse, ConfirmCommandRequest
from app.database.models import CommandRecord

logger = logging.getLogger("edith.command_service")


class CommandService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.command_repo = CommandRepository(db)
        self.device_service = DeviceService(db)
        self.ai_provider = get_ai_provider()

    async def process_command(self, user_id: str, query: str) -> ProcessCommandResponse:
        command_id = str(uuid.uuid4())
        logger.info(f"Processing command '{query}' for user {user_id}")

        # 1. Fetch user devices
        devices = await self.device_repo.list_by_owner(user_id)
        if not devices:
            msg = "You don't have any devices connected. Please pair your laptop first in the Devices tab."
            return ProcessCommandResponse(
                command_id=command_id,
                status="failed",
                speech_response=msg,
                text_response=msg
            )

        devices_summary = [
            {
                "device_id": d.device_id,
                "name": d.name,
                "type": d.type,
                "platform": d.platform,
                "capabilities": d.capabilities or []
            }
            for d in devices
        ]

        # 2. Parse intent via AI Provider (Ollama / Fallback)
        intent = await self.ai_provider.parse_intent(query, devices_summary, TOOL_DEFINITIONS)
        if not intent or not intent.capability:
            msg = "I didn't understand that command. Try asking 'what's my laptop battery' or 'open VS Code'."
            return ProcessCommandResponse(
                command_id=command_id,
                status="failed",
                speech_response=msg,
                text_response=msg
            )

        # 3. Natural Language Device Resolution
        device, res_err = await self.device_service.resolve_device_by_hint(user_id, intent.device_hint)
        if not device or res_err:
            error_msg = res_err or "Could not determine target device."
            return ProcessCommandResponse(
                command_id=command_id,
                status="failed",
                speech_response=error_msg,
                text_response=error_msg
            )

        # 4. Device Capability Validation
        caps = device.capabilities or []
        if intent.capability not in caps and intent.tool_name not in caps:
            msg = f"Your {device.name} does not currently support '{intent.capability}'."
            return ProcessCommandResponse(
                command_id=command_id,
                status="failed",
                target_device_id=device.device_id,
                capability=intent.capability,
                speech_response=msg,
                text_response=msg
            )

        # 5. Online Status Validation
        if not manager.is_device_online(device.device_id):
            msg = f"Your {device.name} is currently offline."
            return ProcessCommandResponse(
                command_id=command_id,
                status="failed",
                target_device_id=device.device_id,
                capability=intent.capability,
                speech_response=msg,
                text_response=msg
            )

        # 6. Risk Level & Confirmation Check
        if confirmation_manager.requires_confirmation(intent.capability):
            token, prompt = confirmation_manager.create_confirmation_request(
                user_id=user_id,
                device_id=device.device_id,
                device_name=device.name,
                capability=intent.capability,
                parameters=intent.parameters
            )
            return ProcessCommandResponse(
                command_id=command_id,
                status="confirmation_required",
                target_device_id=device.device_id,
                capability=intent.capability,
                speech_response=prompt,
                text_response=prompt,
                requires_confirmation=True,
                confirmation_token=token,
                confirmation_prompt=prompt
            )

        # 7. Execute Command via WebSocket
        success, result_data = await manager.send_command(
            device_id=device.device_id,
            capability=intent.capability,
            parameters=intent.parameters
        )

        # 8. Generate Natural Response
        speech_text = await self.ai_provider.generate_response(
            query=query,
            capability=intent.capability,
            device_name=device.name,
            execution_result=result_data if isinstance(result_data, dict) else {"message": str(result_data)},
            success=success
        )

        # 9. Record in Command History
        await self.command_repo.create(
            owner_id=user_id,
            query=query,
            action=intent.capability,
            device_id=device.device_id,
            device_name=device.name,
            status="completed" if success else "failed",
            result=result_data if success else None,
            error=result_data if not success else None
        )

        return ProcessCommandResponse(
            command_id=command_id,
            status="completed" if success else "failed",
            target_device_id=device.device_id,
            capability=intent.capability,
            speech_response=speech_text.speech_text,
            text_response=speech_text.display_text
        )

    async def confirm_command(self, user_id: str, req: ConfirmCommandRequest) -> ProcessCommandResponse:
        command_id = str(uuid.uuid4())

        if not req.confirmed:
            msg = "Action cancelled."
            return ProcessCommandResponse(
                command_id=command_id,
                status="cancelled",
                speech_response=msg,
                text_response=msg
            )

        entry = confirmation_manager.consume_confirmation(req.confirmation_token, user_id)
        if not entry:
            msg = "Confirmation token is invalid or has expired."
            return ProcessCommandResponse(
                command_id=command_id,
                status="failed",
                speech_response=msg,
                text_response=msg
            )

        device_id = entry["device_id"]
        device_name = entry["device_name"]
        capability = entry["capability"]
        parameters = entry["parameters"]

        if not manager.is_device_online(device_id):
            msg = f"Your {device_name} went offline before the command could be executed."
            return ProcessCommandResponse(
                command_id=command_id,
                status="failed",
                speech_response=msg,
                text_response=msg
            )

        # Execute confirmed high-risk command
        success, result_data = await manager.send_command(
            device_id=device_id,
            capability=capability,
            parameters=parameters
        )

        speech_text = await self.ai_provider.generate_response(
            query=f"Confirmed {capability}",
            capability=capability,
            device_name=device_name,
            execution_result=result_data if isinstance(result_data, dict) else {"message": str(result_data)},
            success=success
        )

        # Record in Command History
        await self.command_repo.create(
            owner_id=user_id,
            query=f"Confirmed {capability}",
            action=capability,
            device_id=device_id,
            device_name=device_name,
            status="completed" if success else "failed",
            result=result_data if success else None,
            error=result_data if not success else None
        )

        return ProcessCommandResponse(
            command_id=command_id,
            status="completed" if success else "failed",
            target_device_id=device_id,
            capability=capability,
            speech_response=speech_text.speech_text,
            text_response=speech_text.display_text
        )

    async def get_history(self, user_id: str, limit: int = 50, offset: int = 0) -> List[CommandRecord]:
        return await self.command_repo.list_by_owner(user_id, limit, offset)

    async def clear_history(self, user_id: str) -> int:
        return await self.command_repo.clear_by_owner(user_id)
