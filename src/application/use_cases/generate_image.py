import asyncio
from typing import Callable, Optional

from ...domain.entities.image_request import ImageRequest
from ...domain.entities.generation_session import GenerationSession
from ...domain.ports.image_generator import ImageGeneratorPort
from ...domain.ports.file_storage import FileStoragePort


class GenerateImageUseCase:
    
    def __init__(
        self,
        image_generator: ImageGeneratorPort,
        file_storage: FileStoragePort
    ):
        self.image_generator = image_generator
        self.file_storage = file_storage
    
    async def execute(
        self,
        session: GenerationSession,
        image_prompt: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> GenerationSession:
        try:
            if progress_callback:
                await progress_callback("Generando imagen...")

            # Crear el prompt para imagen infantil y colorida
            enhanced_prompt = self._enhance_prompt_for_children(image_prompt)
            
            # Crear request de imagen
            image_request = ImageRequest(
                prompt=enhanced_prompt,
                aspect_ratio="16:9"
            )
            
            # Generar imagen
            image_response = await self.image_generator.generate_image(image_request)
            session.image_response = image_response
            
            # Guardar metadata actualizada
            self.file_storage.save_metadata(session)

            if progress_callback:
                await progress_callback("Esperando generación de imagen...")

            # Esperar a que se complete la generación
            while not image_response.is_completed and not image_response.is_failed:
                await asyncio.sleep(5)
                try:
                    image_response = await self.image_generator.get_generation_status(
                        image_response.prediction_id
                    )
                    session.image_response = image_response
                    self.file_storage.save_metadata(session)

                    if progress_callback:
                        await progress_callback(f"Estado imagen: {image_response.status}")

                except Exception as e:
                    print(f"Error verificando estado de imagen: {str(e)}")
                    if progress_callback:
                        await progress_callback(f"Error verificando imagen: {str(e)}")
                    break
            
            # Descargar imagen si se completó exitosamente
            if image_response.has_images:
                if progress_callback:
                    await progress_callback("Descargando imagen...")

                await self._download_image(session, progress_callback)

                if progress_callback:
                    await progress_callback("¡Imagen generada!")
            else:
                if progress_callback:
                    await progress_callback("Error: No se pudo generar la imagen")
            
            return session
        
        except Exception as e:
            if progress_callback:
                await progress_callback(f"Error generando imagen: {str(e)}")
            print(f"Error en generate_image: {str(e)}")
            return session
    
    def _enhance_prompt_for_children(self, base_prompt: str) -> str:
        """
        Mejora el prompt para crear imágenes infantiles y coloridas SIN TEXTO
        """
        # Estilos visuales
        visual_style_keywords = [
            "children's book illustration style",
            "bright and vibrant colors", 
            "cartoon style",
            "friendly and cute characters",
            "magical and whimsical atmosphere",
            "high quality digital art",
            "soft rounded shapes",
            "cheerful and warm lighting"
        ]
        
        # Instrucciones EXPLÍCITAS para evitar texto
        no_text_instructions = [
            "NO TEXT",
            "NO LETTERS", 
            "NO WORDS",
            "NO WRITTEN CONTENT",
            "PURE VISUAL ILLUSTRATION ONLY",
            "NO TYPOGRAPHY"
        ]
        
        # Combinar todo con énfasis en no incluir texto
        enhanced = f"IMPORTANT: {', '.join(no_text_instructions)}. {base_prompt}, {', '.join(visual_style_keywords)}"
        return enhanced
    
    async def _download_image(
        self,
        session: GenerationSession,
        progress_callback: Optional[Callable[[str], None]] = None
    ):
        if not session.image_response or not session.image_response.has_images:
            return
        
        session_path = self.file_storage.create_session_directory(session)
        
        # Descargar la primera imagen (Replicate puede devolver múltiples)
        image_url = session.image_response.image_urls[0]
        filename = f"{session.session_id}_cover.png"
        file_path = f"{session_path}/{filename}"
        
        success = await self.image_generator.download_image(image_url, file_path)
        
        if success:
            session.image_path = file_path
            self.file_storage.save_metadata(session)

            if progress_callback:
                await progress_callback(f"Imagen guardada: {filename}")
        else:
            if progress_callback:
                await progress_callback("Error descargando imagen")