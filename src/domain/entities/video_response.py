from dataclasses import dataclass
from typing import Optional


@dataclass
class VideoResponse:
    prediction_id: str
    status: str
    video_url: Optional[str] = None
    error: Optional[str] = None
    
    @property
    def is_completed(self) -> bool:
        return self.status == "succeeded"
    
    @property
    def is_failed(self) -> bool:
        return self.status == "failed"
    
    @property
    def has_video(self) -> bool:
        return bool(self.video_url) and self.is_completed