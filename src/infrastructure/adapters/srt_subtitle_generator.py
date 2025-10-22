import os
import re
import tempfile
import subprocess
from typing import List, Tuple
from datetime import timedelta


class SRTSubtitleGenerator:
    """
    Genera subtítulos en formato SRT simple que FFmpeg puede procesar sin problemas
    """

    def create_subtitled_video(self, video_path: str, output_path: str, lyrics: str,
                               audio_path: str = None, duration: float = 0) -> bool:
        """
        Crea un video con subtítulos SRT incrustados (hardcoded)
        """
        try:
            print("Generando subtítulos en formato SRT...")

            # Preparar las letras
            lines = self._prepare_lyrics(lyrics)
            if not lines:
                print("No hay letras para procesar")
                return self._copy_with_audio(video_path, output_path, audio_path)

            # Crear archivo SRT
            srt_file = self._create_srt_file(lines, duration)
            if not srt_file:
                print("No se pudo crear archivo SRT")
                return self._copy_with_audio(video_path, output_path, audio_path)

            # Aplicar subtítulos con FFmpeg usando método simple
            success = self._apply_srt_subtitles(video_path, output_path, srt_file, audio_path)

            # Limpiar archivo temporal
            try:
                os.remove(srt_file)
            except:
                pass

            return success

        except Exception as e:
            print(f"Error en SRT generator: {str(e)}")
            return self._copy_with_audio(video_path, output_path, audio_path)

    def _prepare_lyrics(self, lyrics: str) -> List[str]:
        """
        Prepara las letras limpiando y dividiendo en líneas
        """
        # Limpiar el texto
        clean_lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remover etiquetas
        clean_lyrics = re.sub(r'\n+', '\n', clean_lyrics).strip()

        if not clean_lyrics:
            return []

        # Dividir en líneas
        lines = [line.strip() for line in clean_lyrics.split('\n') if line.strip()]

        # Procesar líneas largas
        processed = []
        for line in lines:
            # Limpiar caracteres problemáticos
            line = self._clean_text(line)
            if len(line) > 60:
                words = line.split()
                current = ""
                for word in words:
                    if len(current + " " + word) <= 60:
                        current += (" " + word) if current else word
                    else:
                        if current:
                            processed.append(current)
                        current = word
                if current:
                    processed.append(current)
            else:
                processed.append(line)

        return processed[:30]  # Máximo 30 líneas

    def _clean_text(self, text: str) -> str:
        """
        Limpia el texto para evitar problemas con caracteres especiales
        """
        # Mantener solo caracteres seguros
        text = text.replace('\\', '')
        text = text.replace('"', '')
        text = text.replace("'", '')
        text = text.replace('&', 'y')
        text = text.replace('<', '')
        text = text.replace('>', '')
        # Mantener acentos y ñ para español
        text = re.sub(r'[^\w\s\-.,!?áéíóúñÁÉÍÓÚÑ]', '', text)
        return text.strip()

    def _create_srt_file(self, lines: List[str], duration: float) -> str:
        """
        Crea un archivo SRT con los subtítulos
        """
        try:
            # Crear archivo temporal
            with tempfile.NamedTemporaryFile(mode='w', suffix='.srt', delete=False,
                                           encoding='utf-8-sig') as f:  # UTF-8 con BOM
                srt_path = f.name

                time_per_line = duration / len(lines) if lines and duration > 0 else 3

                for i, line in enumerate(lines):
                    # Número de subtítulo
                    f.write(f"{i + 1}\n")

                    # Tiempos
                    start_time = i * time_per_line
                    end_time = min((i + 1) * time_per_line, duration)

                    start_str = self._seconds_to_srt_time(start_time)
                    end_str = self._seconds_to_srt_time(end_time)

                    f.write(f"{start_str} --> {end_str}\n")

                    # Texto (con formato simple para visibilidad)
                    f.write(f"{line}\n\n")

                print(f"Archivo SRT creado: {srt_path}")
                return srt_path

        except Exception as e:
            print(f"Error creando SRT: {str(e)}")
            return None

    def _seconds_to_srt_time(self, seconds: float) -> str:
        """
        Convierte segundos a formato SRT (HH:MM:SS,mmm)
        """
        td = timedelta(seconds=seconds)
        hours = int(td.total_seconds() // 3600)
        minutes = int((td.total_seconds() % 3600) // 60)
        secs = int(td.total_seconds() % 60)
        millis = int((td.total_seconds() % 1) * 1000)

        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

    def _apply_srt_subtitles(self, video_path: str, output_path: str,
                             srt_file: str, audio_path: str = None) -> bool:
        """
        Aplica los subtítulos SRT al video de forma simple y robusta
        """
        try:
            # Construir comando FFmpeg muy simple
            ffmpeg_cmd = ['ffmpeg', '-y']

            # Input de video
            ffmpeg_cmd.extend(['-i', video_path])

            # Input de subtítulos
            ffmpeg_cmd.extend(['-i', srt_file])

            # Input de audio si existe
            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])
                print(f"Añadiendo audio: {audio_path}")

            # Mapear streams
            ffmpeg_cmd.extend(['-map', '0:v'])  # Video del primer input

            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-map', '2:a'])  # Audio del tercer input

            # Filtro de subtítulos muy simple
            # Usar subtítulos con configuración básica
            subtitle_style = (
                "FontName=Arial,"
                "FontSize=24,"
                "PrimaryColour=&H00FFFF00,"  # Amarillo
                "OutlineColour=&H00000000,"  # Negro
                "BorderStyle=3,"
                "Outline=2,"
                "Shadow=1,"
                "MarginV=30"
            )

            ffmpeg_cmd.extend([
                '-vf', f"subtitles={srt_file}:force_style='{subtitle_style}'",
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23'
            ])

            # Audio codec
            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
            else:
                ffmpeg_cmd.extend(['-an'])

            ffmpeg_cmd.append(output_path)

            print("Aplicando subtítulos SRT...")
            print(f"Comando: {' '.join(ffmpeg_cmd[:6])}...")  # Mostrar parte del comando

            # Ejecutar
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("✅ Subtítulos SRT aplicados exitosamente")
                return True
            else:
                # Si falla, intentar método aún más simple
                print("Primer intento falló, probando método ultra-simple...")
                return self._apply_simple_burn_subtitles(video_path, output_path, srt_file, audio_path)

        except subprocess.TimeoutExpired:
            print("Timeout aplicando subtítulos")
            return False
        except Exception as e:
            print(f"Error aplicando SRT: {str(e)}")
            return False

    def _apply_simple_burn_subtitles(self, video_path: str, output_path: str,
                                     srt_file: str, audio_path: str = None) -> bool:
        """
        Método ultra-simple para incrustar subtítulos
        """
        try:
            # Convertir paths a formato Windows
            srt_file_escaped = srt_file.replace('\\', '/').replace(':', '\\:')

            ffmpeg_cmd = ['ffmpeg', '-y', '-i', video_path]

            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])

            # Filtro más simple posible
            ffmpeg_cmd.extend([
                '-vf', f"subtitles='{srt_file_escaped}'",
                '-c:v', 'libx264',
                '-preset', 'veryfast',  # Más rápido
                '-crf', '25'  # Calidad ligeramente menor
            ])

            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-map', '0:v', '-map', '1:a', '-c:a', 'copy'])

            ffmpeg_cmd.append(output_path)

            print("Intentando método ultra-simple...")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("✅ Subtítulos aplicados con método simple")
                return True
            else:
                print(f"Error: {result.stderr[:200]}")
                return False

        except Exception as e:
            print(f"Error en método ultra-simple: {str(e)}")
            return False

    def _copy_with_audio(self, video_path: str, output_path: str, audio_path: str = None) -> bool:
        """
        Copia el video con audio como fallback final
        """
        try:
            ffmpeg_cmd = ['ffmpeg', '-y', '-i', video_path]

            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])
                ffmpeg_cmd.extend([
                    '-map', '0:v',
                    '-map', '1:a',
                    '-c:v', 'copy',
                    '-c:a', 'copy'
                ])
            else:
                ffmpeg_cmd.extend(['-c', 'copy'])

            ffmpeg_cmd.append(output_path)

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print("Video copiado con audio (sin subtítulos)")
                return True

            return False

        except Exception as e:
            print(f"Error en fallback: {str(e)}")
            return False