from abc import ABC, abstractmethod
from typing import Optional
from ..entities.song_request import SongRequest
from ..entities.song_response import SongResponse


class MusicGeneratorPort(ABC):
    
    @abstractmethod
    async def generate_music(self, request: SongRequest) -> SongResponse:
        pass
    
    @abstractmethod
    async def get_generation_status(self, request_id: str) -> SongResponse:
        pass
    
    @abstractmethod
    async def download_track(self, audio_url: str, output_path: str) -> bool:
        pass