import os
import subprocess
import tempfile
import json
import re
from typing import List, Dict, Tuple
import math


class SubtitleAnimator:
    """
    Crea subtítulos animados tipo karaoke para videos
    """
    
    def __init__(self):
        self.font_size = 36
        self.font_color = "white"
        self.outline_color = "black"
        self.outline_width = 2
        
    def add_subtitles_to_video(
        self, 
        video_path: str, 
        output_path: str, 
        lyrics: str, 
        audio_duration: float,
        audio_path: str = None
    ) -> bool:
        """
        Añade subtítulos animados tipo karaoke al video
        """
        try:
            # Limpiar y preparar las letras
            lines = self._prepare_lyrics(lyrics)
            if not lines:
                print("No hay letras para procesar")
                return False
            
            # Ya no necesitamos archivo ASS - usar drawtext directamente
            # Aplicar subtítulos al video usando FFmpeg
            success = self._apply_subtitles_to_video(video_path, output_path, lyrics, audio_path, audio_duration)
            
            return success
            
        except Exception as e:
            print(f"Error añadiendo subtítulos: {str(e)}")
            return False
    
    def _prepare_lyrics(self, lyrics: str) -> List[str]:
        """
        Prepara las letras dividiéndolas en líneas apropiadas
        """
        # Limpiar el texto
        clean_lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remover etiquetas como [Verse], [Chorus]
        clean_lyrics = re.sub(r'\n+', '\n', clean_lyrics)  # Normalizar saltos de línea
        clean_lyrics = clean_lyrics.strip()
        
        if not clean_lyrics:
            return []
        
        # Dividir en líneas y filtrar vacías
        lines = [line.strip() for line in clean_lyrics.split('\n') if line.strip()]
        
        # Limitar líneas muy largas
        processed_lines = []
        for line in lines:
            if len(line) > 60:  # Si la línea es muy larga, dividirla
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 60:
                        current_line += (" " + word) if current_line else word
                    else:
                        if current_line:
                            processed_lines.append(current_line)
                        current_line = word
                if current_line:
                    processed_lines.append(current_line)
            else:
                processed_lines.append(line)
        
        return processed_lines[:20]  # Máximo 20 líneas para evitar sobrecarga
    
    def _create_ass_subtitle_file(self, lyrics: str, duration: float) -> str:
        """
        Crea un archivo ASS con subtítulos animados tipo karaoke
        """
        try:
            lines = self._prepare_lyrics(lyrics)
            if not lines:
                return None

            # Crear archivo temporal ASS
            with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as f:
                ass_file_path = f.name

                # Escribir header mejorado con estilos karaoke
                f.write(self._get_enhanced_ass_header())

                # Calcular timing para cada línea
                time_per_line = duration / len(lines) if lines else 5

                for i, line in enumerate(lines):
                    start_time = i * time_per_line
                    end_time = (i + 1) * time_per_line

                    # Crear línea con efectos karaoke mejorados
                    subtitle_line = self._create_enhanced_karaoke_line(line, start_time, end_time, i)
                    f.write(subtitle_line)

            return ass_file_path

        except Exception as e:
            print(f"Error creando archivo ASS: {str(e)}")
            return None

    def _get_enhanced_ass_header(self) -> str:
        """
        Retorna el header del archivo ASS con estilos mejorados para karaoke
        """
        return """[Script Info]
Title: Karaoke Subtitles
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H00FFFF00,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,3,2,2,30,30,40,1
Style: Karaoke,Arial,45,&H00FFFFFF,&H0000FFFF,&H00FF0000,&H80000000,1,0,0,0,105,105,0,0,1,3,2,2,30,30,40,1
Style: KaraokeActive,Arial,48,&H0000FFFF,&H00FFFFFF,&H00FF0000,&H80000000,1,0,0,0,110,110,0,0,1,4,3,2,30,30,40,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def _create_enhanced_karaoke_line(self, text: str, start_time: float, end_time: float, line_index: int) -> str:
        """
        Crea una línea de subtítulo con efectos karaoke mejorados y animaciones
        """
        # Convertir tiempo a formato ASS
        start_ass = self._seconds_to_ass_time(start_time)
        end_ass = self._seconds_to_ass_time(end_time)

        # Limpiar texto
        clean_text = self._clean_text_for_ass(text)

        # Calcular duración de la línea en centésimas
        line_duration = (end_time - start_time) * 100

        # Dividir texto en sílabas/palabras para efecto karaoke
        words = clean_text.split()
        if not words:
            return ""

        karaoke_text = ""
        time_per_word = line_duration / len(words) if words else line_duration

        # Crear efectos de transformación y karaoke
        # Movimiento vertical (pos) y cambio de color progresivo
        effects = []

        # Efecto de entrada con fade
        effects.append(r"{\fad(200,200)}")

        # Posición con movimiento vertical ondulante
        y_base = 650  # Posición Y base (cerca del fondo)
        y_offset = 10 * (1 + (line_index % 3))  # Variación por línea

        # Movimiento dinámico
        effects.append(r"{\move(640," + str(y_base) + ",640," + str(y_base - y_offset) + ")}")

        # Efectos de karaoke por palabra
        for word in words:
            # K-timing para efecto karaoke (relleno progresivo)
            karaoke_text += r"{\k" + str(int(time_per_word)) + "}" + word + " "

        # Combinar efectos
        full_text = "".join(effects) + karaoke_text.strip()

        # Usar estilo apropiado
        style = "Karaoke" if line_index % 2 == 0 else "KaraokeActive"

        return f"Dialogue: 0,{start_ass},{end_ass},{style},,0,0,0,,{full_text}\n"

    def _clean_text_for_ass(self, text: str) -> str:
        """
        Limpia texto para uso en archivos ASS
        """
        # Eliminar caracteres problemáticos pero mantener legibilidad
        import re
        text = re.sub(r'\[.*?\]', '', text)  # Quitar etiquetas
        text = text.replace('\\', '')
        text = text.replace('{', '')
        text = text.replace('}', '')
        # Mantener puntuación básica para legibilidad
        text = re.sub(r'[^\w\s,.\-!?áéíóúñÁÉÍÓÚÑ]', '', text)
        return text.strip()

    def _create_animated_subtitle_file(self, lines: List[str], duration: float) -> str:
        """
        Crea un archivo ASS con subtítulos animados tipo karaoke
        """
        # Crear archivo temporal ASS
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ass', delete=False, encoding='utf-8') as f:
            ass_file_path = f.name
            
            # Escribir header del archivo ASS
            f.write(self._get_ass_header())
            
            # Calcular timing para cada línea
            time_per_line = duration / len(lines) if lines else 1
            
            for i, line in enumerate(lines):
                start_time = i * time_per_line
                end_time = (i + 1) * time_per_line
                
                # Crear línea de subtítulo con efectos karaoke
                subtitle_line = self._create_karaoke_line(line, start_time, end_time, i)
                f.write(subtitle_line)
        
        return ass_file_path
    
    def _get_ass_header(self) -> str:
        """
        Retorna el header del archivo ASS con estilos
        """
        return """[Script Info]
Title: Karaoke Subtitles
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Karaoke,Arial,36,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,1,0,0,0,100,100,0,0,1,2,0,2,30,30,20,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    
    def _create_karaoke_line(self, text: str, start_time: float, end_time: float, line_index: int) -> str:
        """
        Crea una línea de subtítulo con efectos karaoke y de baile
        """
        # Convertir tiempo a formato ASS (H:MM:SS.CC)
        start_ass = self._seconds_to_ass_time(start_time)
        end_ass = self._seconds_to_ass_time(end_time)
        
        # Crear efectos de baile (movimiento vertical sutil)
        dance_amplitude = 3  # Píxeles de movimiento
        dance_frequency = 2   # Oscilaciones por segundo
        
        # Efecto de karaoke (relleno progresivo)
        line_duration = end_time - start_time
        
        # Dividir texto en palabras para efecto karaoke
        words = text.split()
        karaoke_text = ""
        
        if words:
            time_per_word = line_duration / len(words)
            
            for i, word in enumerate(words):
                word_start = i * time_per_word * 100  # ASS usa centésimas de segundo
                # Efecto karaoke: \k{duration} hace que la palabra se "llene" gradualmente
                karaoke_text += f"\\k{int(time_per_word * 100)}{word} "
        else:
            karaoke_text = f"\\k{int(line_duration * 100)}{text}"
        
        # Efectos de baile usando transformaciones
        dance_effect = f"\\t(\\fry{-5 + (line_index % 3) * 3})\\t(0,{int(line_duration * 1000)},\\fry{5 - (line_index % 3) * 3})"
        
        # Efecto de rebote vertical
        bounce_offset = int(math.sin(line_index * 0.5) * 5)  # Offset vertical basado en la línea
        
        # Combinar todos los efectos
        formatted_text = f"{{\\pos(640,520)\\an2{dance_effect}\\move(640,{520 + bounce_offset},640,{520 - bounce_offset},{int(start_time * 1000)},{int(end_time * 1000)})}}{karaoke_text.strip()}"
        
        return f"Dialogue: 0,{start_ass},{end_ass},Karaoke,,0,0,0,,{formatted_text}\n"
    
    def _seconds_to_ass_time(self, seconds: float) -> str:
        """
        Convierte segundos a formato de tiempo ASS (H:MM:SS.CC)
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centiseconds = int((seconds % 1) * 100)
        
        return f"{hours}:{minutes:02d}:{secs:02d}.{centiseconds:02d}"
    
    def _apply_subtitles_to_video(self, video_path: str, output_path: str, lyrics: str, audio_path: str = None, audio_duration: float = 0) -> bool:
        """
        Aplica subtítulos karaoke animados al video usando MoviePy
        """
        try:
            print(f"🎤 Creando subtítulos karaoke animados para video infantil...")

            # Usar MoviePy para crear subtítulos karaoke animados
            from .moviepy_karaoke_generator import MoviePyKaraokeGenerator

            print("🎵 Generando karaoke con subtítulos bailarines...")
            karaoke_generator = MoviePyKaraokeGenerator()
            success = karaoke_generator.create_karaoke_video(
                video_path, output_path, lyrics, audio_path, audio_duration
            )

            if success:
                print("✨ ¡Subtítulos karaoke animados aplicados exitosamente!")
                return True

            # Si MoviePy falla, intentar con SRT simple como fallback
            print("⚠️ MoviePy falló, intentando método alternativo...")
            from .srt_subtitle_generator import SRTSubtitleGenerator

            srt_generator = SRTSubtitleGenerator()
            success = srt_generator.create_subtitled_video(
                video_path, output_path, lyrics, audio_path, audio_duration
            )

            if success:
                print("✅ Subtítulos básicos aplicados")
                return True

            # Si todo falla, crear video sin subtítulos pero con audio
            print("⚠️ No se pudieron aplicar subtítulos, creando video con audio...")
            success = self._create_video_with_audio_only(video_path, output_path, audio_path)

            return success

        except Exception as e:
            print(f"Error en _apply_subtitles_to_video: {str(e)}")
            # Intentar al menos copiar con audio
            try:
                return self._create_video_with_audio_only(video_path, output_path, audio_path)
            except:
                return False

    def _try_apply_subtitles(self, video_path: str, output_path: str, lyrics: str, audio_path: str = None, audio_duration: float = 0) -> bool:
        """
        Intenta aplicar subtítulos usando ASS con subtítulos incrustados
        """
        try:
            # Primero crear archivo de subtítulos ASS
            ass_file = self._create_ass_subtitle_file(lyrics, audio_duration)

            if not ass_file:
                print("No se pudo crear archivo de subtítulos")
                return False

            # Construir comando FFmpeg con subtítulos ASS
            ffmpeg_cmd = ['ffmpeg']

            # Configurar para evitar problemas de fontconfig
            import os
            env = os.environ.copy()
            env['FONTCONFIG_FILE'] = 'nul'  # Desactivar fontconfig en Windows

            # Input de video
            ffmpeg_cmd.extend(['-i', video_path])

            # Input de audio si está disponible
            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])
                print(f"Añadiendo audio: {audio_path}")

            # Aplicar subtítulos ASS con subtitles filter
            ffmpeg_cmd.extend([
                '-vf', f"subtitles='{ass_file}'",
            ])

            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-map', '0:v', '-map', '1:a', '-c:a', 'copy'])
            else:
                ffmpeg_cmd.extend(['-map', '0:v', '-an'])

            # Configuración de video
            ffmpeg_cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-y',
                output_path
            ])

            print(f"Aplicando subtítulos animados estilo karaoke con ASS...")

            # Ejecutar con entorno modificado
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, env=env, timeout=300)

            if result.returncode == 0:
                print(f"¡Subtítulos karaoke aplicados exitosamente!")
                # Limpiar archivo temporal
                try:
                    os.remove(ass_file)
                except:
                    pass
                return True
            else:
                print(f"Error aplicando subtítulos ASS: {result.stderr[:500]}")
                # Intentar con drawtext simple como fallback
                return self._try_simple_drawtext(video_path, output_path, lyrics, audio_path, audio_duration)

        except subprocess.TimeoutExpired:
            print("Timeout al aplicar subtítulos")
            return False
        except Exception as e:
            print(f"Error intentando aplicar subtítulos: {str(e)}")
            return False

    def _try_simple_drawtext(self, video_path: str, output_path: str, lyrics: str, audio_path: str = None, audio_duration: float = 0) -> bool:
        """
        Fallback con drawtext simple sin efectos complejos
        """
        try:
            ffmpeg_cmd = ['ffmpeg']

            # Input de video
            ffmpeg_cmd.extend(['-i', video_path])

            # Input de audio si está disponible
            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])

            # Crear filtros muy simples
            lines = self._prepare_lyrics(lyrics)
            if lines and len(lines) > 0:
                time_per_line = audio_duration / len(lines) if audio_duration > 0 else 5

                # Usar solo el primer par de líneas como ejemplo
                filters = []
                for i in range(min(3, len(lines))):
                    line = lines[i]
                    # Limpiar texto agresivamente
                    safe_text = ''.join(c for c in line if c.isalnum() or c.isspace())
                    if safe_text:
                        start_time = i * time_per_line
                        end_time = (i + 1) * time_per_line

                        # Filtro muy básico
                        filter_text = (
                            f"drawtext=text='{safe_text[:30]}':"
                            f"fontcolor=yellow:fontsize=24:"
                            f"x=(w-text_w)/2:y=h-50:"
                            f"enable='between(t,{start_time:.1f},{end_time:.1f})'"
                        )
                        filters.append(filter_text)

                if filters:
                    filter_complex = f"[0:v]{','.join(filters)}[v]"
                    ffmpeg_cmd.extend(['-filter_complex', filter_complex, '-map', '[v]'])
                else:
                    ffmpeg_cmd.extend(['-map', '0:v'])
            else:
                ffmpeg_cmd.extend(['-map', '0:v'])

            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-map', '1:a', '-c:a', 'copy'])
            else:
                ffmpeg_cmd.extend(['-an'])

            ffmpeg_cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-y',
                output_path
            ])

            print("Intentando con subtítulos básicos...")
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("Subtítulos básicos aplicados")
                return True
            else:
                print("No se pudieron aplicar ni siquiera subtítulos básicos")
                return False

        except Exception as e:
            print(f"Error en fallback simple: {str(e)}")
            return False

    def _create_video_with_audio_only(self, video_path: str, output_path: str, audio_path: str = None) -> bool:
        """
        Crea video con audio pero sin subtítulos como fallback
        """
        try:
            ffmpeg_cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'error']

            # Input de video
            ffmpeg_cmd.extend(['-i', video_path])

            # Input de audio si está disponible
            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])
                ffmpeg_cmd.extend([
                    '-map', '0:v',
                    '-map', '1:a',
                    '-c:v', 'copy',  # Copiar video sin recodificar
                    '-c:a', 'copy',  # Copiar audio sin recodificar
                ])
            else:
                ffmpeg_cmd.extend([
                    '-map', '0:v',
                    '-c:v', 'copy',
                    '-an'
                ])

            ffmpeg_cmd.extend(['-y', output_path])

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print(f"Video creado exitosamente (sin subtítulos): {output_path}")
                return True
            else:
                print(f"Error creando video: {result.stderr}")
                return False

        except Exception as e:
            print(f"Error en fallback: {str(e)}")
            return False
    
    def _create_windows_animated_filters(self, lyrics: str, duration: float) -> str:
        """
        Crea filtros drawtext animados estilo karaoke para Windows
        Sin dependencias de Fontconfig
        """
        try:
            # Preparar letras
            lines = self._prepare_lyrics(lyrics)
            if not lines:
                return ""

            # Crear cadena de filtros con animaciones
            filter_chain = ""
            time_per_line = duration / len(lines) if lines else 1

            for i, line in enumerate(lines):
                start_time = i * time_per_line
                end_time = (i + 1) * time_per_line
                mid_time = (start_time + end_time) / 2

                # Limpiar texto para Windows/FFmpeg
                safe_text = self._clean_text_for_windows(line)
                if not safe_text:
                    continue

                # Efecto 1: Texto blanco que baila (primera mitad)
                white_dancing = (
                    f"drawtext="
                    f"text='{safe_text}':"
                    f"fontcolor=white:"
                    f"fontsize=32:"
                    f"borderw=2:"
                    f"bordercolor=black:"
                    f"x=(w-text_w)/2:"
                    f"y=h-80+10*sin(2*PI*t*2):"  # Movimiento ondulatorio
                    f"enable='between(t,{start_time:.2f},{mid_time:.2f})'"
                )

                # Efecto 2: Texto amarillo karaoke (segunda mitad)
                yellow_karaoke = (
                    f"drawtext="
                    f"text='{safe_text}':"
                    f"fontcolor=yellow:"
                    f"fontsize=36:"  # Más grande cuando está activo
                    f"borderw=3:"
                    f"bordercolor=red:"
                    f"x=(w-text_w)/2:"
                    f"y=h-80+15*sin(2*PI*t*3):"  # Baile más pronunciado
                    f"enable='between(t,{mid_time:.2f},{end_time:.2f})'"
                )

                # Efecto 3: Sombra/glow para el texto activo
                glow_effect = (
                    f"drawtext="
                    f"text='{safe_text}':"
                    f"fontcolor=orange:"
                    f"fontsize=38:"
                    f"borderw=1:"
                    f"bordercolor=yellow:"
                    f"alpha=0.5:"  # Semi-transparente
                    f"x=(w-text_w)/2:"
                    f"y=h-82+15*sin(2*PI*t*3):"
                    f"enable='between(t,{mid_time:.2f},{end_time:.2f})'"
                )

                # Añadir filtros
                if filter_chain:
                    filter_chain += ","

                # Añadir los tres efectos para crear el karaoke animado
                filter_chain += white_dancing + "," + yellow_karaoke + "," + glow_effect

            return filter_chain

        except Exception as e:
            print(f"Error creando filtros animados: {str(e)}")
            return ""

    def _clean_text_for_windows(self, text: str) -> str:
        """
        Limpia el texto para que funcione en Windows con FFmpeg
        """
        # Mantener solo caracteres seguros
        import re

        # Eliminar etiquetas como [Verse], [Chorus]
        text = re.sub(r'\[.*?\]', '', text)

        # Reemplazar caracteres problemáticos
        replacements = {
            "'": "",
            '"': "",
            "¡": "",
            "!": "",
            "¿": "",
            "?": "",
            ",": " ",
            ":": " ",
            ";": " ",
            "\\": "",
            "/": " ",
            "(": "",
            ")": "",
            "[": "",
            "]": "",
            "{": "",
            "}": "",
            "&": "y",
            "%": " por ciento",
            "$": "",
            "#": "",
            "@": "a",
            "*": "",
            "+": " mas ",
            "=": " igual ",
            "|": " ",
            "<": "",
            ">": "",
            "~": "",
            "`": "",
            "^": "",
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Limpiar espacios múltiples
        text = re.sub(r'\s+', ' ', text).strip()

        # Si el texto queda vacío, usar un placeholder
        if not text:
            text = "..."

        return text

    def _create_simple_drawtext_filters(self, lyrics: str, duration: float) -> str:
        """
        Crea filtros drawtext muy simplificados sin dependencias de fuentes
        """
        try:
            # Preparar letras
            lines = self._prepare_lyrics(lyrics)
            if not lines:
                return ""

            # Crear cadena de filtros muy simple
            filter_chain = ""
            time_per_line = duration / len(lines) if lines else 1

            for i, line in enumerate(lines):
                start_time = i * time_per_line
                end_time = (i + 1) * time_per_line

                # Escapar texto de manera muy conservadora
                safe_text = line.replace("'", "")  # Quitar apóstrofes
                safe_text = safe_text.replace('"', "")  # Quitar comillas
                safe_text = safe_text.replace(':', " ")  # Reemplazar : con espacio
                safe_text = safe_text.replace(',', " ")  # Reemplazar , con espacio
                safe_text = safe_text.replace('\\', "")  # Quitar backslashes
                safe_text = safe_text.replace('¡', "")  # Quitar caracteres especiales
                safe_text = safe_text.replace('!', "")
                safe_text = safe_text.replace('¿', "")
                safe_text = safe_text.replace('?', "")
                safe_text = safe_text.replace('[', "")
                safe_text = safe_text.replace(']', "")
                safe_text = safe_text.replace('{', "")
                safe_text = safe_text.replace('}', "")
                safe_text = safe_text.replace('(', "")
                safe_text = safe_text.replace(')', "")

                # Filtro muy simple sin efectos complejos
                simple_filter = (
                    f"drawtext="
                    f"text='{safe_text}':"
                    f"fontcolor=white:"
                    f"fontsize=24:"
                    f"x=(w-text_w)/2:"
                    f"y=h-50:"
                    f"enable='between(t,{start_time:.1f},{end_time:.1f})'"
                )

                if filter_chain:
                    filter_chain += ","
                filter_chain += simple_filter

            return filter_chain

        except Exception as e:
            print(f"Error creando filtros simples: {str(e)}")
            return ""

    def _create_drawtext_filters(self, lyrics: str, duration: float) -> str:
        """
        Crea filtros drawtext para subtítulos animados tipo karaoke con efectos dinámicos
        """
        try:
            # Preparar letras
            lines = self._prepare_lyrics(lyrics)
            if not lines:
                return ""

            # Crear cadena de filtros
            filter_chain = ""
            time_per_line = duration / len(lines) if lines else 1

            for i, line in enumerate(lines):
                start_time = i * time_per_line
                end_time = (i + 1) * time_per_line
                mid_time = (start_time + end_time) / 2

                # Escapar caracteres especiales para FFmpeg
                safe_text = self._escape_text_for_ffmpeg(line)

                # Crear múltiples efectos para cada línea

                # 1. Texto blanco con efecto de baile (aparece primero)
                white_filter = (
                    f"drawtext="
                    f"fontsize=28:"
                    f"x=(w-text_w)/2:"
                    f"y=h-70+8*sin(2*PI*(t-{start_time:.2f})*2):"  # Baile dinámico
                    f"fontcolor=white:"  # Blanco sólido
                    f"borderw=3:"
                    f"bordercolor=black:"
                    f"text='{safe_text}':"
                    f"enable='between(t,{start_time:.2f},{mid_time:.2f})'"
                )

                # 2. Texto amarillo con efecto karaoke (aparece después)
                yellow_filter = (
                    f"drawtext="
                    f"fontsize=30:"  # Ligeramente más grande cuando está activo
                    f"x=(w-text_w)/2:"
                    f"y=h-72+10*sin(2*PI*(t-{start_time:.2f})*1.5):"  # Baile más pronunciado
                    f"fontcolor=yellow:"  # Amarillo sólido
                    f"borderw=3:"
                    f"bordercolor=red:"  # Borde rojo para destacar
                    f"text='{safe_text}':"
                    f"enable='between(t,{mid_time:.2f},{end_time:.2f})'"
                )

                # Añadir los filtros para esta línea
                if filter_chain:
                    filter_chain += ","
                filter_chain += white_filter + "," + yellow_filter

            return filter_chain

        except Exception as e:
            print(f"Error creando filtros drawtext: {str(e)}")
            return ""
    
    def _escape_text_for_ffmpeg(self, text: str) -> str:
        """
        Escapa caracteres especiales para uso en filtros FFmpeg
        """
        # Escapar caracteres problemáticos para FFmpeg de manera más robusta
        text = text.replace("\\", "\\\\")  # Backslashes primero
        text = text.replace("'", "'\\'\\''")  # Comillas simples
        text = text.replace(":", "\\:")    # Dos puntos
        text = text.replace(",", "\\,")    # Comas
        text = text.replace("[", "\\[")    # Corchetes
        text = text.replace("]", "\\]")    # Corchetes
        text = text.replace("(", "\\(")    # Paréntesis
        text = text.replace(")", "\\)")    # Paréntesis
        text = text.replace("{", "\\{")    # Llaves
        text = text.replace("}", "\\}")    # Llaves
        return text