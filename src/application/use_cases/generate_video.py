import asyncio
import os
from typing import Callable, Optional

from ...domain.entities.video_request import VideoRequest
from ...domain.entities.generation_session import GenerationSession
from ...domain.ports.video_generator import VideoGeneratorPort
from ...domain.ports.file_storage import FileStoragePort


class GenerateVideoUseCase:
    
    def __init__(
        self,
        video_generator: VideoGeneratorPort,
        file_storage: FileStoragePort
    ):
        self.video_generator = video_generator
        self.file_storage = file_storage
    
    async def execute(
        self,
        session: GenerationSession,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> GenerationSession:
        """
        Genera un video animado desde la imagen de portada de la sesión
        """
        try:
            # Verificar que la sesión tiene una imagen
            if not session.image_path or not os.path.exists(session.image_path):
                if progress_callback:
                    await progress_callback("Error: No hay imagen para animar")
                return session

            if progress_callback:
                await progress_callback("Creando video animado...")

            # Calcular duración objetivo basada en los tracks de audio
            target_duration = self._calculate_target_duration(session)
            if not target_duration:
                if progress_callback:
                    await progress_callback("Error: No se pudo calcular duración de la canción")
                return session
            
            # Crear prompt de animación basado en la canción
            animation_prompt = self._create_animation_prompt(session)
            
            # Crear request de video
            video_request = VideoRequest(
                image_path=session.image_path,
                prompt=animation_prompt,
                duration=target_duration
            )
            
            # Generar video
            if progress_callback:
                await progress_callback("Enviando imagen a WAN para animación...")

            video_response = await self.video_generator.generate_video(video_request)

            # Guardar referencia del video en progreso
            session.video_response = video_response
            self.file_storage.save_metadata(session)

            if progress_callback:
                await progress_callback("Esperando generación de video...")

            # Esperar a que se complete la generación
            while not video_response.is_completed and not video_response.is_failed:
                await asyncio.sleep(10)  # WAN tarda más que las imágenes
                try:
                    video_response = await self.video_generator.get_generation_status(
                        video_response.prediction_id
                    )
                    session.video_response = video_response
                    self.file_storage.save_metadata(session)

                    if progress_callback:
                        await progress_callback(f"Estado video: {video_response.status}")

                except Exception as e:
                    print(f"Error verificando estado de video: {str(e)}")
                    if progress_callback:
                        await progress_callback(f"Error verificando video: {str(e)}")
                    break
            
            # Descargar y procesar video si se completó exitosamente
            if video_response.has_video:
                if progress_callback:
                    await progress_callback("Descargando video...")

                await self._download_and_process_video(session, target_duration, progress_callback)

                if progress_callback:
                    await progress_callback("¡Video animado creado!")
            else:
                if progress_callback:
                    await progress_callback("Error: No se pudo generar el video")

            return session

        except Exception as e:
            if progress_callback:
                await progress_callback(f"Error generando video: {str(e)}")
            print(f"Error en generate_video: {str(e)}")
            return session
    
    def _calculate_target_duration(self, session: GenerationSession) -> Optional[int]:
        """
        Calcula la duración objetivo del video basada en los tracks de audio
        """
        if not session.response or not session.response.tracks:
            return None
        
        if not session.local_path or not os.path.exists(session.local_path):
            return None
        
        # Buscar el primer archivo de audio y obtener su duración
        try:
            for file in os.listdir(session.local_path):
                if file.endswith(('.mp3', '.wav', '.ogg')):
                    audio_path = os.path.join(session.local_path, file)
                    duration = self.video_generator.get_audio_duration(audio_path)
                    if duration:
                        return int(duration)  # Redondear a segundos enteros
            
            # Fallback: usar duración promedio de canciones infantiles (3 minutos)
            return 180
            
        except Exception as e:
            print(f"Error calculando duración: {str(e)}")
            return 180  # Fallback de 3 minutos
    
    def _create_animation_prompt(self, session: GenerationSession) -> str:
        """
        Crea un prompt de animación apropiado para el contenido de la canción
        """
        title_lower = session.request.title.lower()
        lyrics_lower = session.request.prompt.lower()
        
        # Animaciones específicas basadas en el contenido
        if "perrita" in lyrics_lower or "perro" in lyrics_lower:
            return "A gentle animation of a cute little dog wagging its tail, blinking eyes softly, and making small movements in a peaceful children's book style scene"
        
        if "capibara" in lyrics_lower:
            return "A calm and peaceful animation of a happy capybara with subtle movements, gentle swaying, and soft blinking in a colorful cartoon environment"
        
        if "baila" in lyrics_lower or "dance" in lyrics_lower:
            return "A joyful animation with gentle dancing movements, characters swaying softly to music, with magical sparkles and warm lighting"
        
        if "aventura" in lyrics_lower or "adventure" in lyrics_lower:
            return "An adventurous animation with gentle movement through a magical landscape, soft camera movements, and whimsical elements floating around"
        
        # Prompt genérico para canciones infantiles
        return "A magical children's book illustration coming to life with gentle movements, soft character animations, twinkling effects, and warm lighting that creates a peaceful and joyful atmosphere"
    
    async def _download_and_process_video(
        self,
        session: GenerationSession,
        target_duration: int,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Descarga el video y lo procesa para crear el bucle de la duración correcta
        """
        if not session.video_response or not session.video_response.has_video:
            return
        
        session_path = self.file_storage.create_session_directory(session)
        
        # Descargar video original
        original_video_path = os.path.join(session_path, f"{session.session_id}_animation_original.mp4")
        success = await self.video_generator.download_video(
            session.video_response.video_url, 
            original_video_path
        )
        
        if not success:
            if progress_callback:
                await progress_callback("Error descargando video")
            return

        # Crear video en bucle de la duración correcta con subtítulos
        if progress_callback:
            await progress_callback("Creando bucle de video con subtítulos...")
        
        looped_video_path = os.path.join(session_path, f"{session.session_id}_cover_video.mp4")
        
        # Buscar archivo de audio para sincronización
        audio_file = self._find_audio_file(session)
        
        # Intentar crear bucle con subtítulos
        if hasattr(self.video_generator, 'loop_video_with_subtitles'):
            loop_success = self.video_generator.loop_video_with_subtitles(
                original_video_path,
                looped_video_path,
                target_duration,
                session.request.prompt,
                audio_file
            )
        else:
            # Fallback al método básico
            loop_success = self.video_generator.loop_video_to_duration(
                original_video_path,
                looped_video_path,
                target_duration
            )
        
        if loop_success:
            session.video_path = looped_video_path
            self.file_storage.save_metadata(session)

            if progress_callback:
                await progress_callback(f"Video en bucle creado: {target_duration}s")
        else:
            if progress_callback:
                await progress_callback("Error creando bucle de video")
    
    def _find_audio_file(self, session: GenerationSession) -> Optional[str]:
        """
        Busca el primer archivo de audio en la sesión para sincronización
        """
        if not session.local_path or not os.path.exists(session.local_path):
            return None
        
        try:
            for file in os.listdir(session.local_path):
                if file.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
                    audio_path = os.path.join(session.local_path, file)
                    print(f"Archivo de audio encontrado para subtítulos: {audio_path}")
                    return audio_path
            
            print("No se encontró archivo de audio para sincronización")
            return None
            
        except Exception as e:
            print(f"Error buscando archivo de audio: {str(e)}")
            return None