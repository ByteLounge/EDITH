import json
import logging
from typing import Dict, Any, List, Optional
import httpx
from app.ai.base import AIProvider, IntentResult, SpeechTextResponse
from app.ai.fallback_parser import FallbackParser
from app.config.settings import settings

logger = logging.getLogger("edith.ai.gemini")


class GeminiProvider(AIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self.fallback = FallbackParser()

    async def parse_intent(
        self,
        query: str,
        available_devices: List[Dict[str, Any]],
        tools: List[Dict[str, Any]]
    ) -> Optional[IntentResult]:
        if not self.api_key:
            return self.fallback.parse(query, available_devices)

        # Build request to Gemini REST API
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        prompt = (
            f"You are EDITH Core Intent Classifier. Given query: '{query}', devices: {json.dumps(available_devices)}, "
            f"and tools: {json.dumps(tools)}, output JSON: "
            '{"tool_name": "...", "capability": "...", "device_hint": "...", "parameters": {}}'
        )

        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.post(endpoint, json={"contents": [{"parts": [{"text": prompt}]}]})
                if res.status_code == 200:
                    text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
                    clean_text = text.strip("```json\n").strip("```").strip()
                    parsed = json.loads(clean_text)
                    if parsed.get("capability"):
                        return IntentResult(
                            tool_name=parsed.get("tool_name", parsed.get("capability")),
                            capability=parsed.get("capability"),
                            device_hint=parsed.get("device_hint"),
                            parameters=parsed.get("parameters", {}),
                            confidence=0.98
                        )
        except Exception as e:
            logger.warning(f"Gemini error ({e}), falling back.")

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
