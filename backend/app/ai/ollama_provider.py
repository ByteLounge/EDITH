import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.ai.base import AIProvider, IntentResult, SpeechTextResponse
from app.ai.fallback_parser import FallbackParser
from app.config.settings import settings

logger = logging.getLogger("edith.ai.ollama")


class OllamaProvider(AIProvider):
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None):
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.model = model or settings.OLLAMA_MODEL
        self.fallback = FallbackParser()

    async def parse_intent(
        self,
        query: str,
        available_devices: List[Dict[str, Any]],
        tools: List[Dict[str, Any]]
    ) -> Optional[IntentResult]:
        """
        Invokes local Ollama to parse natural language intent.
        Falls back smoothly to FallbackParser if Ollama is unreachable.
        """
        devices_summary = [
            {"id": d.get("device_id"), "name": d.get("name"), "type": d.get("type"), "caps": d.get("capabilities", [])}
            for d in available_devices
        ]

        system_prompt = (
            "You are EDITH Core Intent Classifier. Given a user query, available devices, and tools, "
            "select the most appropriate tool and target device.\n"
            "Respond ONLY with a JSON object with this exact structure:\n"
            "{\n"
            '  "tool_name": "string (name of matched tool)",\n'
            '  "capability": "string (capability of matched tool)",\n'
            '  "device_hint": "string (e.g. laptop, phone, or device name/id)",\n'
            '  "parameters": { ... }\n'
            "}\n"
            "If no tool matches, return null."
        )

        user_content = (
            f"User Query: \"{query}\"\n"
            f"Available Devices: {json.dumps(devices_summary)}\n"
            f"Available Tools: {json.dumps(tools)}"
        )

        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "system": system_prompt,
                        "prompt": user_content,
                        "stream": False,
                        "format": "json"
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    response_text = data.get("response", "").strip()
                    if response_text and response_text != "null":
                        parsed = json.loads(response_text)
                        if parsed.get("capability"):
                            return IntentResult(
                                tool_name=parsed.get("tool_name", parsed.get("capability")),
                                capability=parsed.get("capability"),
                                device_hint=parsed.get("device_hint"),
                                parameters=parsed.get("parameters", {}),
                                confidence=0.95
                            )
        except Exception as e:
            logger.info(f"Ollama API not responding ({e}). Using deterministic fallback parser.")

        # Smooth fallback to local deterministic parser
        return self.fallback.parse(query, available_devices)

    async def generate_response(
        self,
        query: str,
        capability: str,
        device_name: str,
        execution_result: Dict[str, Any],
        success: bool
    ) -> SpeechTextResponse:
        """Generates conversational speech and text responses."""
        if not success:
            return self.fallback.format_response(capability, device_name, execution_result, False)

        prompt = (
            f"User asked: \"{query}\"\n"
            f"Action performed: {capability} on {device_name}\n"
            f"Result data: {json.dumps(execution_result)}\n"
            "Generate a concise, natural, polite single-sentence response for speech synthesis. "
            "Example: 'Chrome is open on your laptop.'"
        )

        try:
            async with httpx.AsyncClient(timeout=3.0) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if res.status_code == 200:
                    text = res.json().get("response", "").strip()
                    if text:
                        return SpeechTextResponse(speech_text=text, display_text=text)
        except Exception:
            pass

        # Fallback to standard deterministic format
        return self.fallback.format_response(capability, device_name, execution_result, True)
