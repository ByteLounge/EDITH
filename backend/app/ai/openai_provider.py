import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.ai.base import AIProvider, IntentResult, SpeechTextResponse
from app.ai.fallback_parser import FallbackParser
from app.config.settings import settings

logger = logging.getLogger("edith.ai.openai")


class OpenAIProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL
        self.fallback = FallbackParser()

    async def parse_intent(
        self,
        query: str,
        available_devices: List[Dict[str, Any]],
        tools: List[Dict[str, Any]]
    ) -> Optional[IntentResult]:
        if not self.api_key:
            return self.fallback.parse(query, available_devices)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        devices_summary = [
            {"id": d.get("device_id"), "name": d.get("name"), "type": d.get("type"), "caps": d.get("capabilities", [])}
            for d in available_devices
        ]

        payload = {
            "model": self.model,
            "response_format": {"type": "json_object"},
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are EDITH Core Intent Classifier. Given user query, devices, and tools, "
                        "select the tool and target device. Respond with JSON: "
                        '{"tool_name": "...", "capability": "...", "device_hint": "...", "parameters": {}}'
                    )
                },
                {
                    "role": "user",
                    "content": f"Query: {query}\nDevices: {json.dumps(devices_summary)}\nTools: {json.dumps(tools)}"
                }
            ]
        }

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if res.status_code == 200:
                    content = res.json()["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    if parsed.get("capability"):
                        return IntentResult(
                            tool_name=parsed.get("tool_name", parsed.get("capability")),
                            capability=parsed.get("capability"),
                            device_hint=parsed.get("device_hint"),
                            parameters=parsed.get("parameters", {}),
                            confidence=0.98
                        )
        except Exception as e:
            logger.warning(f"OpenAI error ({e}), falling back.")

        return self.fallback.parse(query, available_devices)

    async def generate_response(
        self,
        query: str,
        capability: str,
        device_name: str,
        execution_result: Dict[str, Any],
        success: bool
    ) -> SpeechTextResponse:
        return self.fallback.format_response(capability, device_name, execution_result, success)
