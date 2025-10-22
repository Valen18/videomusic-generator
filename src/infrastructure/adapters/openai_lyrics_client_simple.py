import asyncio
from openai import OpenAI
from typing import Optional
from .usage_tracker import get_tracker, APIUsage


class OpenAILyricsClientSimple:
    """
    Simple OpenAI client that uses Chat Completions API instead of Assistants
    No need for Assistant ID
    """

    def __init__(self, api_key: str, assistant_id: str = None):
        self.client = OpenAI(api_key=api_key)
        self.tracker = get_tracker()

    async def generate_lyrics(self, description: str, progress_callback=None, session_id: str = "unknown") -> str:
        """
        Generate song lyrics based on a description using OpenAI Chat Completions

        Args:
            description: The description of the song to generate lyrics for
            progress_callback: Optional callback for progress updates
            session_id: Session ID for tracking

        Returns:
            Generated lyrics as a string
        """

        usage = APIUsage(
            api_name="OpenAI",
            endpoint="/v1/chat/completions",
            request_data={"description": description},
            session_id=session_id
        )

        try:
            print(f"[OpenAI Simple] Generando letra con descripción: {description}")

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Conectando con OpenAI..."
                )

            # System prompt for lyrics generation
            system_prompt = """Eres un compositor profesional de canciones infantiles.
Tu tarea es crear letras de canciones para niños que sean:
- Educativas y apropiadas para la edad
- Divertidas y pegajosas
- Fáciles de cantar y recordar
- Con un mensaje positivo

Genera SOLO la letra de la canción, sin títulos, sin explicaciones, sin comentarios adicionales.
Usa formato de estrofas y coros claramente separados."""

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Generando letra de la canción..."
                )

            # Call OpenAI Chat Completions API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model="gpt-4o-mini",  # Más económico que gpt-4
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Crea una letra de canción sobre: {description}"}
                    ],
                    temperature=0.8,  # Creatividad moderada
                    max_tokens=500
                )
            )

            if response.choices and len(response.choices) > 0:
                lyrics = response.choices[0].message.content.strip()
                print(f"[OpenAI Simple] Letra generada (primeros 100 chars): {lyrics[:100]}...")

                if progress_callback:
                    await asyncio.get_event_loop().run_in_executor(
                        None, progress_callback, "Letra generada exitosamente"
                    )

                # Registrar uso
                usage.response_data = {"lyrics_length": len(lyrics)}
                usage.tokens_used = response.usage.total_tokens if response.usage else len(lyrics) // 4
                usage.cost_usd = self.tracker.calculate_openai_cost("gpt-4o-mini", usage.tokens_used)
                usage.success = True
                self.tracker.track_usage(usage)

                return lyrics
            else:
                raise Exception("No se recibió respuesta de OpenAI")

        except Exception as e:
            print(f"[OpenAI Simple] ERROR: {str(e)}")

            if usage.success is None:
                usage.success = False
                usage.error_message = str(e)
                self.tracker.track_usage(usage)

            raise Exception(f"Error al generar letra: {str(e)}")
