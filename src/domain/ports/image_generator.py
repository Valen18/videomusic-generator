from abc import ABC, abstractmethod
from typing import Optional

from ..entities.image_request import ImageRequest
from ..entities.image_response import ImageResponse


class ImageGeneratorPort(ABC):
    
    @abstractmethod
    async def generate_image(self, request: ImageRequest) -> ImageResponse:
        """
        Genera una imagen usando el prompt proporcionado
        """
        pass
    
    @abstractmethod
    async def get_generation_status(self, prediction_id: str) -> ImageResponse:
        """
        Obtiene el estado de una generación de imagen
        """
        pass
    
    @abstractmethod
    async def download_image(self, image_url: str, file_path: str) -> bool:
        """
        Descarga una imagen desde la URL y la guarda en el archivo especificado
        """
        pass