from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ModelVersion(Enum):
    V3_5 = "V3_5"
    V4 = "V4"
    V4_5 = "V4_5"


@dataclass
class SongRequest:
    prompt: str
    style: str
    title: str
    model: ModelVersion
    custom_mode: bool
    instrumental: bool
    callback_url: Optional[str] = None
    
    def __post_init__(self):
        if not self.prompt:
            raise ValueError("Prompt cannot be empty")
        if not self.title:
            raise ValueError("Title cannot be empty")
    
    def to_dict(self) -> dict:
        payload = {
            "prompt": self.prompt,
            "style": self.style,
            "title": self.title,
            "model": self.model.value,
            "customMode": self.custom_mode,
            "instrumental": self.instrumental
        }
        
        # Añadir callBackUrl si está disponible, o usar URL por defecto
        if self.callback_url:
            payload["callBackUrl"] = self.callback_url
        else:
            payload["callBackUrl"] = "https://httpbin.org/post"  # URL de prueba que acepta cualquier POST
        
        return payload