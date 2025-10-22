import asyncio
import time
import traceback
from openai import OpenAI
from typing import Optional
from .usage_tracker import get_tracker, APIUsage


class OpenAILyricsClient:
    def __init__(self, api_key: str, assistant_id: str = "asst_tR6OL8QLpSsDDlc6hKdBmVNU"):
        self.client = OpenAI(api_key=api_key)
        self.assistant_id = assistant_id
        self.tracker = get_tracker()

    async def generate_lyrics(self, description: str, progress_callback=None, session_id: str = "unknown") -> str:
        """
        Generate song lyrics based on a description using OpenAI Assistant V2

        Args:
            description: The description of the song to generate lyrics for
            progress_callback: Optional callback for progress updates
            session_id: Session ID for tracking

        Returns:
            Generated lyrics as a string
        """

        usage = APIUsage(
            api_name="OpenAI",
            endpoint="/v1/threads/runs",
            request_data={"description": description, "assistant_id": self.assistant_id},
            session_id=session_id
        )

        try:
            print(f"[OpenAI] Iniciando generación de letra con descripción: {description}")
            print(f"[OpenAI] Assistant ID: {self.assistant_id}")

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Conectando con el asistente de OpenAI..."
                )

            # Create a thread
            print("[OpenAI] Creando thread...")
            thread = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.beta.threads.create()
            )
            print(f"[OpenAI] Thread creado: {thread.id}")

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Enviando solicitud de generación de letra..."
                )

            # Create message first, then run (V2 approach)
            print("[OpenAI] Creando mensaje en el thread...")
            message = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.beta.threads.messages.create(
                    thread_id=thread.id,
                    role="user",
                    content=description
                )
            )
            print(f"[OpenAI] Mensaje creado: {message.id}")

            # Create and poll run
            print("[OpenAI] Creando y ejecutando run...")
            run = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.beta.threads.runs.create_and_poll(
                    thread_id=thread.id,
                    assistant_id=self.assistant_id
                )
            )
            print(f"[OpenAI] Run status: {run.status}")

            if progress_callback:
                await asyncio.get_event_loop().run_in_executor(
                    None, progress_callback, "Generando letra de la canción..."
                )

            # Check if run completed
            if run.status == 'completed':
                print("[OpenAI] Run completado, obteniendo mensajes...")
                # Get messages
                messages = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.client.beta.threads.messages.list(thread_id=thread.id)
                )
                print(f"[OpenAI] Mensajes obtenidos: {len(messages.data)} mensajes")

                # Get the assistant's response
                for message in messages.data:
                    print(f"[OpenAI] Mensaje - Role: {message.role}, ID: {message.id}")
                    if message.role == "assistant":
                        if message.content and len(message.content) > 0:
                            # Handle text content
                            for content in message.content:
                                print(f"[OpenAI] Contenido tipo: {content.type}")
                                if content.type == 'text':
                                    lyrics = content.text.value
                                    print(f"[OpenAI] Letra generada (primeros 100 chars): {lyrics[:100]}...")

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
                print(f"[OpenAI] ERROR: {error_msg}")

                usage.success = False
                usage.error_message = error_msg
                self.tracker.track_usage(usage)
                raise Exception(error_msg)

        except Exception as e:
            print(f"[OpenAI] EXCEPCIÓN CAPTURADA:")
            print(f"[OpenAI] Tipo: {type(e).__name__}")
            print(f"[OpenAI] Mensaje: {str(e)}")
            print(f"[OpenAI] Traceback completo:")
            traceback.print_exc()

            if usage.success is None:  # Solo registrar si no se ha registrado ya
                usage.success = False
                usage.error_message = str(e)
                self.tracker.track_usage(usage)

            raise Exception(f"Error al generar letra: {str(e)}")