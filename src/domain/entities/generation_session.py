from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import time


@dataclass
class GenerationSession:
    session_id: str
    timestamp: int
    request: 'SongRequest'
    response: Optional['SongResponse'] = None
    local_path: Optional[str] = None
    image_response: Optional['ImageResponse'] = None
    image_path: Optional[str] = None
    video_response: Optional['VideoResponse'] = None
    video_path: Optional[str] = None
    
    @classmethod
    def create_new(cls, request: 'SongRequest') -> 'GenerationSession':
        timestamp = int(time.time())
        session_id = f"song_{timestamp}"
        return cls(
            session_id=session_id,
            timestamp=timestamp,
            request=request
        )
    
    @property
    def output_directory(self) -> str:
        return f"output/{self.session_id}"