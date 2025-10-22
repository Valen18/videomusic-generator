import os
import json
import asyncio
import aiohttp
from typing import Optional

from ...domain.ports.image_generator import ImageGeneratorPort
from ...domain.entities.image_request import ImageRequest
from ...domain.entities.image_response import ImageResponse


class ReplicateImageClient(ImageGeneratorPort):
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN is required")
        
        self.base_url = "https://api.replicate.com/v1"
        self.model = "bytedance/seedream-4"
        
    async def generate_image(self, request: ImageRequest) -> ImageResponse:
        """
        Genera una imagen usando seedream-4 a través de Replicate API
        """
        url = f"{self.base_url}/models/{self.model}/predictions"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "input": request.to_dict()
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        raise Exception(f"Replicate API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    return ImageResponse(
                        prediction_id=data["id"],
                        status=data["status"],
                        image_urls=data.get("output", []) or [],
                        error=data.get("error")
                    )
            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
    
    async def get_generation_status(self, prediction_id: str) -> ImageResponse:
        """
        Obtiene el estado actual de una generación de imagen
        """
        url = f"{self.base_url}/predictions/{prediction_id}"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, headers=headers) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Replicate API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    return ImageResponse(
                        prediction_id=data["id"],
                        status=data["status"],
                        image_urls=data.get("output", []) or [],
                        error=data.get("error")
                    )
            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
    
    async def download_image(self, image_url: str, file_path: str) -> bool:
        """
        Descarga una imagen desde la URL y la guarda en el archivo especificado
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(image_url) as response:
                    if response.status == 200:
                        # Asegurar que el directorio existe
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        print(f"Imagen descargada: {file_path}")
                        return True
                    else:
                        print(f"Error descargando imagen: {response.status}")
                        return False
        except Exception as e:
            print(f"Error descargando imagen: {str(e)}")
            return False