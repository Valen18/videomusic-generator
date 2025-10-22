from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoRequest:
    image_path: str
    prompt: str
    duration: Optional[int] = None  # Duration in seconds for the final looped video
    
    def __post_init__(self):
        if not self.image_path:
            raise ValueError("Image path cannot be empty")
        if not self.prompt:
            raise ValueError("Animation prompt cannot be empty")
    
    def to_dict(self) -> dict:
        return {
            "image": f"file://{self.image_path}",  # WAN expects image URL or file path
            "prompt": self.prompt
        }