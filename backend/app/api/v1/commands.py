from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.dependencies import get_current_user
from app.database.models import User
from app.services.command_service import CommandService
from app.commands.schemas import (
    ProcessCommandRequest,
    ProcessCommandResponse,
    ConfirmCommandRequest,
    CommandHistoryResponse
)

router = APIRouter(prefix="/commands", tags=["Commands"])


@router.post("/process", response_model=ProcessCommandResponse)
async def process_natural_language_command(
    req: ProcessCommandRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CommandService(db)
    response = await service.process_command(current_user.id, req.query)
    return response


@router.post("/confirm", response_model=ProcessCommandResponse)
async def confirm_high_risk_command(
    req: ConfirmCommandRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CommandService(db)
    response = await service.confirm_command(current_user.id, req)
    return response


@router.get("/history", response_model=List[CommandHistoryResponse])
async def get_command_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CommandService(db)
    records = await service.get_history(current_user.id, limit=limit, offset=offset)
    return records


@router.delete("/history", status_code=status.HTTP_204_NO_CONTENT)
async def clear_command_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CommandService(db)
    await service.clear_history(current_user.id)
    return None
