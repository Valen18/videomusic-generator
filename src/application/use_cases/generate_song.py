import asyncio
from typing import Callable, Optional

from ...domain.entities.song_request import SongRequest
from ...domain.entities.generation_session import GenerationSession
from ...domain.ports.music_generator import MusicGeneratorPort
from ...domain.ports.file_storage import FileStoragePort
from ...domain.ports.image_generator import ImageGeneratorPort
from .generate_image import GenerateImageUseCase


class GenerateSongUseCase:
    
    def __init__(
        self,
        music_generator: MusicGeneratorPort,
        file_storage: FileStoragePort,
        image_generator: Optional[ImageGeneratorPort] = None
    ):
        self.music_generator = music_generator
        self.file_storage = file_storage
        self.image_generator = image_generator
        
        # Inicializar el caso de uso de imagen si está disponible
        if self.image_generator:
            self.generate_image_use_case = GenerateImageUseCase(
                self.image_generator,
                self.file_storage
            )
    
    async def execute(
        self,
        request: SongRequest,
        progress_callback: Optional[Callable[[str], None]] = None,
        generate_image: bool = True
    ) -> GenerationSession:
        session = GenerationSession.create_new(request)
        
        try:
            if progress_callback:
                await progress_callback("Creando sesión...")

            self.file_storage.create_session_directory(session)
            self.file_storage.save_metadata(session)

            if progress_callback:
                await progress_callback("Enviando petición a SunoAPI...")
            
            # Iniciar generación de música
            try:
                response = await self.music_generator.generate_music(request)
                print(f"DEBUG: Received response: {response}")
                session.response = response
            except Exception as e:
                print(f"DEBUG: Error in generate_music: {str(e)}")
                if progress_callback:
                    await progress_callback(f"Error en generación: {str(e)}")
                raise

            if progress_callback:
                await progress_callback("Guardando respuesta...")

            self.file_storage.save_metadata(session)
            
            # Crear tareas paralelas para música e imagen
            tasks = []
            
            # Tarea para procesar música
            music_task = asyncio.create_task(
                self._process_music_generation(session, progress_callback)
            )
            tasks.append(music_task)
            
            # Tarea para generar imagen si está disponible y solicitado
            if generate_image and self.image_generator and hasattr(self, 'generate_image_use_case'):
                image_prompt = self._create_image_prompt(request)
                image_task = asyncio.create_task(
                    self.generate_image_use_case.execute(
                        session, 
                        image_prompt, 
                        progress_callback
                    )
                )
                tasks.append(image_task)
            
            # Esperar a que todas las tareas terminen
            if progress_callback:
                await progress_callback("Procesando música e imagen en paralelo...")

            await asyncio.gather(*tasks, return_exceptions=True)

            if progress_callback:
                await progress_callback("¡Generación completada!")

            return session
        
        except Exception as e:
            if progress_callback:
                await progress_callback(f"Error: {str(e)}")
            raise
    
    async def _process_music_generation(
        self,
        session: GenerationSession,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Procesa la generación de música (espera a que complete y descarga)
        """
        response = session.response

        if progress_callback:
            await progress_callback("Esperando generación de música completa...")

        while not response.is_completed:
            await asyncio.sleep(5)
            try:
                response = await self.music_generator.get_generation_status(response.request_id)
                print(f"DEBUG: Status response: {response}")
                session.response = response
                self.file_storage.save_metadata(session)

                if progress_callback:
                    await progress_callback(f"Estado música: {response.status}")
            except Exception as e:
                print(f"DEBUG: Error in get_generation_status: {str(e)}")
                if progress_callback:
                    await progress_callback(f"Error verificando estado música: {str(e)}")
                break

        if progress_callback:
            await progress_callback("Descargando archivos de audio...")

        await self._download_tracks(session, progress_callback)
    
    def _create_image_prompt(self, request: SongRequest) -> str:
        """
        Crea un prompt para imagen basado en la canción solicitada, 
        extrayendo elementos visuales sin incluir texto
        """
        # Extraer elementos visuales clave de la letra
        visual_elements = self._extract_visual_elements(request.prompt, request.title)
        
        # Crear prompt base solo con elementos visuales
        base_prompt = f"A colorful illustration showing {visual_elements}"
        
        return base_prompt
    
    def _extract_visual_elements(self, lyrics: str, title: str) -> str:
        """
        Extrae elementos visuales de la letra sin incluir el texto literal
        """
        lyrics_lower = lyrics.lower()
        title_lower = title.lower()
        visual_elements = []
        characters = []
        actions = []
        settings = []
        
        # Personajes y animales
        if "perrita" in lyrics_lower or "perro" in lyrics_lower or "dog" in lyrics_lower:
            characters.append("a cute little dog with wagging tail")
        if "gato" in lyrics_lower or "cat" in lyrics_lower:
            characters.append("a friendly cat")
        if "ratón" in lyrics_lower or "mouse" in lyrics_lower:
            characters.append("a small mouse")
        if "capibara" in lyrics_lower:
            characters.append("a happy capybara")
        if "capitán" in lyrics_lower or "captain" in lyrics_lower:
            characters.append("a brave captain character with hat")
        if "niño" in lyrics_lower or "niña" in lyrics_lower or "child" in lyrics_lower:
            characters.append("happy children")
            
        # Acciones y actividades
        if "juega" in lyrics_lower or "playing" in lyrics_lower:
            actions.append("playing and having fun")
        if "baila" in lyrics_lower or "dance" in lyrics_lower:
            actions.append("dancing joyfully")
        if "corre" in lyrics_lower or "running" in lyrics_lower:
            actions.append("running playfully")
        if "salta" in lyrics_lower or "jump" in lyrics_lower:
            actions.append("jumping with joy")
        if "canta" in lyrics_lower or "sing" in lyrics_lower:
            actions.append("expressing joy and music")
            
        # Escenarios y ambientes
        if "calle" in lyrics_lower or "street" in lyrics_lower:
            settings.append("in a colorful neighborhood street")
        if "parque" in lyrics_lower or "park" in lyrics_lower:
            settings.append("in a beautiful park")
        if "casa" in lyrics_lower or "home" in lyrics_lower:
            settings.append("in a cozy home environment")
        if "jardín" in lyrics_lower or "garden" in lyrics_lower:
            settings.append("in a magical garden")
        if "bosque" in lyrics_lower or "forest" in lyrics_lower:
            settings.append("in an enchanted forest")
        if "playa" in lyrics_lower or "beach" in lyrics_lower:
            settings.append("on a sunny beach")
            
        # Emociones y relaciones
        if "familia" in lyrics_lower or "family" in lyrics_lower:
            actions.append("surrounded by loving family")
        if "amigos" in lyrics_lower or "friends" in lyrics_lower:
            actions.append("playing with friends")
        if "feliz" in lyrics_lower or "happy" in lyrics_lower or "alegr" in lyrics_lower:
            actions.append("expressing happiness and joy")
        if "cariños" in lyrics_lower or "love" in lyrics_lower:
            actions.append("showing love and affection")
        if "aventura" in lyrics_lower or "adventure" in lyrics_lower:
            actions.append("on an exciting adventure")
            
        # Construir el prompt final
        if characters:
            visual_elements.extend(characters)
        if actions:
            visual_elements.extend(actions)
        if settings:
            visual_elements.extend(settings)
            
        # Si no encontramos elementos específicos, crear descripción genérica
        if not visual_elements:
            if "infantil" in title_lower or "children" in title_lower:
                visual_elements.append("happy children characters in a magical colorful world")
            else:
                visual_elements.append("cute cartoon characters in a joyful scene")
                
        return ", ".join(visual_elements)
    
    async def _download_tracks(
        self,
        session: GenerationSession,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        if not session.response or not session.response.has_downloadable_tracks:
            return
        
        session_path = self.file_storage.create_session_directory(session)
        
        for i, track in enumerate(session.response.tracks):
            if track.audio_url:
                if progress_callback:
                    await progress_callback(f"Descargando track {i+1}/{len(session.response.tracks)}: {track.title}")

                filename = f"track_{i+1}_{track.title}.mp3".replace(" ", "_")
                file_path = f"{session_path}/{filename}"
                
                success = await self.music_generator.download_track(track.audio_url, file_path)
                
                if success and not session.local_path:
                    session.local_path = session_path
        
        self.file_storage.save_metadata(session)