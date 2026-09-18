from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class IntentResult(BaseModel):
    tool_name: str
    capability: str
    device_hint: Optional[str] = None
    parameters: Dict[str, Any] = {}
    explanation: Optional[str] = None
    confidence: float = 1.0


class SpeechTextResponse(BaseModel):
    speech_text: str
    display_text: str


class AIProvider(ABC):
    @abstractmethod
    async def parse_intent(
        self,
        query: str,
        available_devices: List[Dict[str, Any]],
        tools: List[Dict[str, Any]]
    ) -> Optional[IntentResult]:
        """Parses natural language query into a structured tool invocation."""
        pass

    @abstractmethod
    async def generate_response(
        self,
        query: str,
        capability: str,
        device_name: str,
        execution_result: Dict[str, Any],
        success: bool
    ) -> SpeechTextResponse:
        """Synthesizes human-friendly speech and text responses from tool results."""
        pass
