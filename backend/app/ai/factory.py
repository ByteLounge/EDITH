from app.config.settings import settings
from app.ai.base import AIProvider
from app.ai.ollama_provider import OllamaProvider
from app.ai.openai_provider import OpenAIProvider
from app.ai.gemini_provider import GeminiProvider


def get_ai_provider() -> AIProvider:
    provider_name = settings.AI_PROVIDER.lower().strip()
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    else:
        # Default is Ollama with graceful fallback
        return OllamaProvider()
