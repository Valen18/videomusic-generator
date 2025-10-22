from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class SongTrack:
    id: str
    title: str
    audio_url: Optional[str]
    stream_url: Optional[str]
    status: str
    created_at: datetime


@dataclass
class SongResponse:
    request_id: str
    status: str
    tracks: List[SongTrack]
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    @property
    def is_completed(self) -> bool:
        return self.status == "completed"
    
    @property
    def has_downloadable_tracks(self) -> bool:
        return any(track.audio_url for track in self.tracks)