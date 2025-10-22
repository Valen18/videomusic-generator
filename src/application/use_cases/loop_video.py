import os
from typing import Callable, Optional

from ...domain.entities.generation_session import GenerationSession
from ...domain.ports.video_generator import VideoGeneratorPort
from ...domain.ports.file_storage import FileStoragePort


class LoopVideoUseCase:
    
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
        Crea un bucle del video original para que coincida con la duración de la canción
        """
        try:
            # Verificar que existe el video original
            session_path = self.file_storage.create_session_directory(session)
            original_video_path = os.path.join(session_path, f"{session.session_id}_animation_original.mp4")
            
            if not os.path.exists(original_video_path):
                if progress_callback:
                    progress_callback("Error: No se encontró el video original para hacer bucle")
                return session
            
            if progress_callback:
                progress_callback("Calculando duración de la canción...")
            
            # Calcular duración objetivo basada en los tracks de audio
            target_duration = self._calculate_target_duration(session)
            if not target_duration:
                if progress_callback:
                    progress_callback("Error: No se pudo calcular duración de la canción")
                return session
            
            if progress_callback:
                progress_callback(f"Creando bucle de video para {target_duration} segundos...")
            
            # Crear video en bucle con subtítulos karaoke
            looped_video_path = os.path.join(session_path, f"{session.session_id}_cover_video.mp4")
            
            # Intentar crear bucle con subtítulos si están disponibles las letras
            if hasattr(session.request, 'prompt') and session.request.prompt:
                if progress_callback:
                    progress_callback("Creando bucle con subtítulos karaoke...")
                
                # Buscar archivo de audio para sincronización
                audio_file = self._find_audio_file(session)
                
                # Usar método con subtítulos si está disponible
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
            else:
                # Sin letras, usar método básico
                loop_success = self.video_generator.loop_video_to_duration(
                    original_video_path,
                    looped_video_path,
                    target_duration
                )
            
            if loop_success:
                session.video_path = looped_video_path
                self.file_storage.save_metadata(session)
                
                if progress_callback:
                    progress_callback(f"¡Bucle de video creado exitosamente! ({target_duration}s)")
            else:
                if progress_callback:
                    progress_callback("Error: No se pudo crear el bucle de video")
            
            return session
        
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error creando bucle: {str(e)}")
            print(f"Error en loop_video: {str(e)}")
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