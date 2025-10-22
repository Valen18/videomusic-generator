import os
import json
from dotenv import load_dotenv
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from pathlib import Path

load_dotenv()


@dataclass
class APISettings:
    suno_api_key: str = ""
    suno_base_url: str = "https://api.sunoapi.org"

    replicate_api_token: str = ""
    replicate_base_url: str = "https://api.replicate.com/v1"

    openai_api_key: str = ""
    openai_assistant_id: str = "asst_tR6OL8QLpSsDDlc6hKdBmVNU"
    openai_base_url: str = "https://api.openai.com/v1"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'APISettings':
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Settings:
    suno_api_key: str
    suno_base_url: str = "https://api.sunoapi.org"
    output_directory: str = "output"
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    callback_url: str = "https://httpbin.org/post"

    @classmethod
    def from_env(cls) -> 'Settings':
        api_key = os.getenv("SUNO_API_KEY")
        if not api_key:
            raise ValueError("SUNO_API_KEY environment variable is required")

        return cls(
            suno_api_key=api_key,
            suno_base_url=os.getenv("SUNO_BASE_URL", "https://api.sunoapi.org"),
            output_directory=os.getenv("OUTPUT_DIRECTORY", "output"),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "5")),
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
            callback_url=os.getenv("CALLBACK_URL", "https://httpbin.org/post")
        )


class ConfigManager:
    def __init__(self, config_file: str = "api_config.json"):
        self.config_file = Path(config_file)
        self.api_settings = self._load_config()

    def _load_config(self) -> APISettings:
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return APISettings.from_dict(data)
            except (json.JSONDecodeError, KeyError):
                pass

        return APISettings(
            suno_api_key=os.getenv("SUNO_API_KEY", ""),
            replicate_api_token=os.getenv("REPLICATE_API_TOKEN", ""),
            openai_api_key=os.getenv("OPENAI_API_KEY", "")
        )

    def save_config(self, api_settings: APISettings):
        self.api_settings = api_settings
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(api_settings.to_dict(), f, indent=2, ensure_ascii=False)

    def get_api_settings(self) -> APISettings:
        return self.api_settings