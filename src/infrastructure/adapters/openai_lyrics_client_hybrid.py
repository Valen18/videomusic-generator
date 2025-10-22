import asyncio
import time
import traceback
from openai import OpenAI
from typing import Optional
from .usage_tracker import get_tracker, APIUsage


class OpenAILyricsClientHybrid:
    """
    Hybrid OpenAI client that tries Assistants API first, then falls back to Chat Completions
    """

    def __init__(self, api_key: str, assistant_id: str = None):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.tracker = get_tracker()
        self.use_assistant = True  # Try assistant first

    async def generate_lyrics(self, description: str, progress_callback=None, session_id: str = "unknown") -> str:
        """
        Generate song lyrics - tries Assistant first, falls back to Chat Completions if 404

        Args:
            description: The description of the song to generate lyrics for
            progress_callback: Optional callback for progress updates
            session_id: Session ID for tracking

        Returns:
            Generated lyrics as a string
        """

        # Try with Assistant first (if configured and not previously failed)
        if self.use_assistant and self.assistant_id:
            try:
                return await self._generate_with_assistant(description, progress_callback, session_id)
            except Exception as e:
                error_str = str(e).lower()
                # If it's a 404 error (assistant not found), switch to Chat Completions permanently
                if "404" in error_str or "no assistant found" in error_str or "not found" in error_str:
                    print(f"[OpenAI Hybrid] Assistant no encontrado, cambiando a Chat Completions para esta sesión")
                    self.use_assistant = False  # Don't try assistant again for this client instance
                    # Continue to Chat Completions below
                else:
                    # Other error, re-raise
                    raise

        # Use Chat Completions (either as fallback or primary method)
        return await self._generate_with_chat(description, progress_callback, session_id)

    async def _generate_with_assistant(self, description: str, progress_callback=None, session_id: str = "unknown") -> str:
        """Generate lyrics using Assistants API"""
        usage = APIUsage(
            api_name="OpenAI",
            endpoint="/v1/threads/runs",
            request_data={"description": description, "assistant_id": self.assistant_id},
            session_id=session_id
        )

        try:
            print(f"[OpenAI Hybrid] Intentando con Assistant: {self.assistant_id}")

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Conectando con el asistente de OpenAI..."
                )

            # Create a thread
            thread = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.beta.threads.create()
            )

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Enviando solicitud de generación de letra..."
                )

            # Create message first, then run (V2 approach)
            message = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=description
                )
            )

            # Create and poll run
            run = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=self.assistant_id
                )
            )

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Generando letra de la canción..."
                )

            # Check if run completed
            if run.status == 'completed':
                # Get messages
                messages = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.beta.threads.messages.list(thread_id=thread.id)
                )

                # Get the assistant's response
                for message in messages.data:
                    if message.role == "assistant":
                        if message.content and len(message.content) > 0:
                            # Handle text content
                            for content in message.content:
                                if content.type == 'text':
                                    lyrics = content.text.value
                                    print(f"[OpenAI Hybrid - Assistant] Letra generada exitosamente")

                                    if progress_callback:
                                        await asyncio.get_event_loop().run_in_executor(
                                            None, progress_callback, "Letra generada exitosamente"
                                        )

                                    # Registrar uso exitoso
                                    usage.response_data = {"lyrics_length": len(lyrics)}
                                    usage.tokens_used = len(lyrics) // 4  # Estimación aproximada
                                    usage.cost_usd = self.tracker.calculate_openai_cost("gpt-4", usage.tokens_used)
                                    usage.success = True
                                    self.tracker.track_usage(usage)

                                    return lyrics

                usage.success = False
                usage.error_message = "No se pudo obtener respuesta del asistente"
                self.tracker.track_usage(usage)
                raise Exception("No se pudo obtener respuesta del asistente")
            else:
                error_msg = f"La generación falló con estado: {run.status}"
                if hasattr(run, 'last_error') and run.last_error:
                    error_msg = f"La generación falló: {run.last_error}"

                usage.success = False
                usage.error_message = error_msg
                self.tracker.track_usage(usage)
                raise Exception(error_msg)

        except Exception as e:
            print(f"[OpenAI Hybrid - Assistant] ERROR: {str(e)}")

            if usage.success is None:  # Solo registrar si no se ha registrado ya
                usage.success = False
                usage.error_message = str(e)
                self.tracker.track_usage(usage)

            raise Exception(f"Error al generar letra: {str(e)}")

    async def _generate_with_chat(self, description: str, progress_callback=None, session_id: str = "unknown") -> str:
        """Generate lyrics using Chat Completions API"""
        usage = APIUsage(
            api_name="OpenAI",
            endpoint="/v1/chat/completions",
            request_data={"description": description},
            session_id=session_id
        )

        try:
            print(f"[OpenAI Hybrid] Generando letra con Chat Completions")

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Conectando con OpenAI (Chat)..."
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
                print(f"[OpenAI Hybrid - Chat] Letra generada exitosamente")

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
            print(f"[OpenAI Hybrid - Chat] ERROR: {str(e)}")

            if usage.success is None:
                usage.success = False
                usage.error_message = str(e)
                self.tracker.track_usage(usage)

            raise Exception(f"Error al generar letra: {str(e)}")
