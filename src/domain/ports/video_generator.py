from abc import ABC, abstractmethod
from typing import Optional

from ..entities.video_request import VideoRequest
from ..entities.video_response import VideoResponse


class VideoGeneratorPort(ABC):
    
    @abstractmethod
    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """
        Genera un video animado desde una imagen usando el prompt proporcionado
        """
        pass
    
    @abstractmethod
    async def get_generation_status(self, prediction_id: str) -> VideoResponse:
        """
        Obtiene el estado de una generación de video
        """
        pass
    
    @abstractmethod
    async def download_video(self, video_url: str, file_path: str) -> bool:
        """
        Descarga un video desde la URL y lo guarda en el archivo especificado
        """
        pass
    
    @abstractmethod
    def loop_video_to_duration(self, input_path: str, output_path: str, target_duration: int) -> bool:
        """
        Crea un bucle del video hasta alcanzar la duración objetivo usando FFmpeg
        """
        pass