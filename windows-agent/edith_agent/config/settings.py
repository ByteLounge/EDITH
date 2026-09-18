import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    DEVICE_ID: str = "laptop-main"
    DEVICE_NAME: str = "Windows Laptop"
    DEVICE_TYPE: str = "computer"
    PLATFORM: str = "windows"
    VERSION: str = "1.0.0"

    SERVER_URL: str = "http://localhost:8000"
    WS_SERVER_URL: str = "ws://localhost:8000"
    DEVICE_TOKEN: str = ""

    HEARTBEAT_INTERVAL_SECONDS: int = 30
    CONFIG_DIR: str = str(Path.home() / ".edith")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


agent_settings = AgentSettings()
