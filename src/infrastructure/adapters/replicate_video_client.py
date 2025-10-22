import os
import json
import asyncio
import aiohttp
import subprocess
from typing import Optional
import tempfile

from ...domain.ports.video_generator import VideoGeneratorPort
from ...domain.entities.video_request import VideoRequest
from ...domain.entities.video_response import VideoResponse
from .subtitle_animator import SubtitleAnimator


class ReplicateVideoClient(VideoGeneratorPort):
    
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or os.getenv('REPLICATE_API_TOKEN')
        if not self.api_token:
            raise ValueError("REPLICATE_API_TOKEN is required")
        
        self.base_url = "https://api.replicate.com/v1"
        self.model = "wan-video/wan-2.2-i2v-fast"  # WAN Image-to-Video model
        self.subtitle_animator = SubtitleAnimator()
        
    async def generate_video(self, request: VideoRequest) -> VideoResponse:
        """
        Genera un video animado desde una imagen usando WAN de Replicate
        """
        url = f"{self.base_url}/models/{self.model}/predictions"
        
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
        
        # Upload image first if it's a local file
        image_url = await self._upload_image_if_local(request.image_path)
        
        payload = {
            "input": {
                "image": image_url,
                "prompt": request.prompt
            }
        }
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status != 201:
                        error_text = await response.text()
                        raise Exception(f"Replicate API error: {response.status} - {error_text}")
                    
                    data = await response.json()
                    
                    return VideoResponse(
                        prediction_id=data["id"],
                        status=data["status"],
                        video_url=data.get("output"),
                        error=data.get("error")
                    )
            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
    
    async def _upload_image_if_local(self, image_path: str) -> str:
        """
        Si la imagen es un archivo local, la convierte a data URI base64
        """
        if image_path.startswith("http"):
            return image_path
        
        try:
            import base64
            import mimetypes
            
            # Detectar tipo MIME
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type or not mime_type.startswith('image/'):
                mime_type = 'image/png'  # Fallback
            
            # Leer archivo y convertir a base64
            with open(image_path, 'rb') as image_file:
                image_data = image_file.read()
                base64_data = base64.b64encode(image_data).decode('utf-8')
                
            # Crear data URI
            data_uri = f"data:{mime_type};base64,{base64_data}"
            
            print(f"Imagen convertida a data URI (tamaño: {len(data_uri)} chars)")
            return data_uri
            
        except Exception as e:
            print(f"Error al convertir imagen a data URI: {str(e)}")
            # Fallback: intentar usar el upload endpoint de Replicate
            return await self._upload_to_replicate(image_path)
    
    async def _upload_to_replicate(self, image_path: str) -> str:
        """
        Sube la imagen usando el endpoint de upload de Replicate
        """
        try:
            # Endpoint para uploads de Replicate
            upload_url = f"{self.base_url}/files"
            
            headers = {
                "Authorization": f"Bearer {self.api_token}"
            }
            
            async with aiohttp.ClientSession() as session:
                with open(image_path, 'rb') as f:
                    data = aiohttp.FormData()
                    data.add_field('content', f, filename=os.path.basename(image_path))
                    
                    async with session.post(upload_url, headers=headers, data=data) as response:
                        if response.status == 201:
                            result = await response.json()
                            file_url = result.get('urls', {}).get('get')
                            if file_url:
                                print(f"Imagen subida a Replicate: {file_url}")
                                return file_url
                        
                        error_text = await response.text()
                        print(f"Error subiendo imagen: {response.status} - {error_text}")
                        raise Exception(f"Error subiendo imagen: {response.status}")
                        
        except Exception as e:
            print(f"Error en upload a Replicate: {str(e)}")
            # Último fallback: usar path absoluto como URI (puede fallar)
            return f"file://{os.path.abspath(image_path)}"
    
    async def get_generation_status(self, prediction_id: str) -> VideoResponse:
        """
        Obtiene el estado actual de una generación de video
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
                    
                    return VideoResponse(
                        prediction_id=data["id"],
                        status=data["status"],
                        video_url=data.get("output"),
                        error=data.get("error")
                    )
            except aiohttp.ClientError as e:
                raise Exception(f"Network error: {str(e)}")
    
    async def download_video(self, video_url: str, file_path: str) -> bool:
        """
        Descarga un video desde la URL y lo guarda en el archivo especificado
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url) as response:
                    if response.status == 200:
                        # Asegurar que el directorio existe
                        os.makedirs(os.path.dirname(file_path), exist_ok=True)
                        
                        with open(file_path, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                f.write(chunk)
                        
                        print(f"Video descargado: {file_path}")
                        return True
                    else:
                        print(f"Error descargando video: {response.status}")
                        return False
        except Exception as e:
            print(f"Error descargando video: {str(e)}")
            return False
    
    def loop_video_to_duration(self, input_path: str, output_path: str, target_duration: int) -> bool:
        """
        Crea un bucle del video hasta alcanzar la duración objetivo usando FFmpeg
        """
        try:
            # Primero obtenemos la duración del video original
            probe_cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                input_path
            ]
            
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error getting video duration: {result.stderr}")
                return False
            
            video_info = json.loads(result.stdout)
            original_duration = float(video_info['format']['duration'])
            
            # Calcular cuántas veces necesitamos repetir el video
            loops_needed = int(target_duration / original_duration) + 1
            
            # Crear archivo temporal con lista de videos para concatenar
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                concat_file = f.name
                # Usar path absoluto y escapar comillas
                abs_input_path = os.path.abspath(input_path).replace('\\', '/')
                for _ in range(loops_needed):
                    f.write(f"file '{abs_input_path}'\n")
            
            print(f"Archivo concat creado: {concat_file}")
            print(f"Video input: {abs_input_path}")
            print(f"Loops necesarios: {loops_needed}")
            
            try:
                # Usar FFmpeg para concatenar el video en bucle
                # Re-encodear para asegurar compatibilidad con audio posterior
                ffmpeg_cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', concat_file,
                    '-t', str(target_duration),  # Cortar al tiempo exacto
                    '-c:v', 'libx264',  # Re-encodear video
                    '-preset', 'medium',
                    '-crf', '23',
                    '-pix_fmt', 'yuv420p',
                    '-y',  # Sobrescribir archivo de salida
                    output_path
                ]
                
                result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"Video en bucle creado: {output_path} ({target_duration}s)")
                    return True
                else:
                    print(f"Error creando bucle de video: {result.stderr}")
                    return False
                    
            finally:
                # Limpiar archivo temporal
                os.unlink(concat_file)
                
        except Exception as e:
            print(f"Error procesando video: {str(e)}")
            return False
    
    def get_audio_duration(self, audio_path: str) -> Optional[float]:
        """
        Obtiene la duración de un archivo de audio usando FFmpeg
        """
        try:
            probe_cmd = [
                'ffprobe', 
                '-v', 'quiet', 
                '-print_format', 'json', 
                '-show_format', 
                audio_path
            ]
            
            result = subprocess.run(probe_cmd, capture_output=True, text=True)
            if result.returncode == 0:
                audio_info = json.loads(result.stdout)
                return float(audio_info['format']['duration'])
            else:
                print(f"Error getting audio duration: {result.stderr}")
                return None
                
        except Exception as e:
            print(f"Error getting audio duration: {str(e)}")
            return None
    
    def loop_video_with_subtitles(
        self, 
        input_path: str, 
        output_path: str, 
        target_duration: int, 
        lyrics: str,
        audio_path: str = None
    ) -> bool:
        """
        Crea un bucle del video con subtítulos animados tipo karaoke
        """
        try:
            # Primero crear el bucle básico
            temp_looped_path = output_path.replace('.mp4', '_temp_loop.mp4')
            
            loop_success = self.loop_video_to_duration(input_path, temp_looped_path, target_duration)
            if not loop_success:
                return False
            
            print("Añadiendo subtítulos animados...")
            
            # Luego añadir subtítulos al bucle
            subtitle_success = self.subtitle_animator.add_subtitles_to_video(
                temp_looped_path,
                output_path,
                lyrics,
                target_duration,
                audio_path
            )
            
            # Limpiar archivo temporal
            if os.path.exists(temp_looped_path):
                os.unlink(temp_looped_path)
            
            if subtitle_success:
                print(f"Video con subtítulos creado: {output_path}")
                return True
            else:
                print("Error añadiendo subtítulos, usando video sin subtítulos")
                # Si falla, al menos conservar el bucle sin subtítulos
                if os.path.exists(temp_looped_path):
                    os.rename(temp_looped_path, output_path)
                return True
                
        except Exception as e:
            print(f"Error en loop_video_with_subtitles: {str(e)}")
            return False