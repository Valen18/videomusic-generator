from dataclasses import dataclass
from typing import Optional


@dataclass
class ImageResponse:
    prediction_id: str
    status: str
    image_urls: list[str]
    error: Optional[str] = None
    
    @property
    def is_completed(self) -> bool:
        return self.status == "succeeded"
    
    @property
    def is_failed(self) -> bool:
        return self.status == "failed"
    
    @property
    def has_images(self) -> bool:
        return bool(self.image_urls) and self.is_completed