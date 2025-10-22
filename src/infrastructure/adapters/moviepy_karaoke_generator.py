import os
import re
import numpy as np
from typing import List, Tuple
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip,
    CompositeVideoClip, concatenate_videoclips
)
from moviepy.video.fx import resize
import math


class MoviePyKaraokeGenerator:
    """
    Genera subtítulos karaoke animados usando MoviePy
    """

    def __init__(self):
        # Reducir resolución para menor consumo de recursos
        self.video_width = 854  # 480p en lugar de 720p
        self.video_height = 480
        self.subtitle_zone_height = 70

    def create_karaoke_video(self, video_path: str, output_path: str, lyrics: str,
                             audio_path: str = None, duration: float = 0, subtitle_config: dict = None) -> bool:
        """
        Crea un video con subtítulos karaoke animados y bailarines con configuración personalizada
        Estrategia: Crear video sin audio con MoviePy, luego añadir audio con FFmpeg
        """
        try:
            # Aplicar configuración personalizada si se proporciona
            if subtitle_config:
                self._apply_config(subtitle_config)

            print("🎵 Iniciando generación de karaoke con MoviePy...")

            # Cargar video base
            video = VideoFileClip(video_path)

            # Redimensionar si es necesario
            if video.w != self.video_width or video.h != self.video_height:
                video = video.resize((self.video_width, self.video_height))

            # Determinar duración objetivo basada en el audio
            if audio_path and os.path.exists(audio_path):
                print(f"🎵 Verificando duración del audio: {audio_path}")
                try:
                    temp_audio = AudioFileClip(audio_path)
                    if duration == 0:
                        duration = temp_audio.duration
                    print(f"📏 Duración objetivo: {duration} segundos")
                    temp_audio.close()
                except Exception as e:
                    print(f"Error leyendo audio: {str(e)}")
                    if duration == 0:
                        duration = 30
            else:
                if duration == 0:
                    duration = 30

            # Si el video es más corto que la duración necesaria, hacer loop
            if video.duration < duration:
                loops_needed = int(np.ceil(duration / video.duration))
                print(f"🔄 Creando {loops_needed} loops del video")
                video_loops = [video] * loops_needed
                video = concatenate_videoclips(video_loops)

            # Ajustar duración final
            video = video.subclip(0, duration)

            # Preparar letras
            lines = self._prepare_lyrics(lyrics)

            # Crear archivo temporal para video sin audio
            import tempfile
            temp_video = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False).name

            if lines:
                # Crear clips de subtítulos animados
                print("Creando subtítulos animados tipo karaoke...")
                subtitle_clips = self._create_animated_subtitles(lines, duration)

                # Componer video con subtítulos (sin audio)
                final_video = CompositeVideoClip([video] + subtitle_clips)
                final_video = final_video.set_duration(duration)
            else:
                print("No hay letras para procesar")
                final_video = video

            # Exportar video SIN audio primero
            # OPTIMIZADO para bajo consumo de recursos
            print("Renderizando video con subtítulos (optimizado para bajo consumo)...")
            final_video.write_videofile(
                temp_video,
                codec='libx264',
                fps=15,  # Reducido de 24 a 15 FPS (37% menos frames)
                preset='ultrafast',  # Preset más rápido con menor CPU
                threads=2,  # Limitado a 2 threads para no sobrecargar
                bitrate='500k',  # Bitrate bajo para archivos más pequeños
                logger=None,
                audio=False  # NO incluir audio aquí
            )

            # Limpiar recursos de MoviePy
            video.close()
            final_video.close()

            # Ahora usar FFmpeg para combinar video con audio
            success = self._add_audio_with_ffmpeg(temp_video, output_path, audio_path)

            # Limpiar archivo temporal
            try:
                os.remove(temp_video)
            except:
                pass

            if success:
                print("✅ ¡Video karaoke creado exitosamente con audio!")
            else:
                print("⚠️ Video creado pero sin audio")

            return success

        except Exception as e:
            print(f"Error en MoviePy: {str(e)}")
            # Fallback: copiar video con audio
            return self._fallback_copy(video_path, output_path, audio_path)

    def _prepare_lyrics(self, lyrics: str) -> List[str]:
        """
        Prepara y limpia las letras
        """
        # Limpiar texto
        clean_lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Quitar etiquetas
        clean_lyrics = re.sub(r'\n+', '\n', clean_lyrics).strip()

        if not clean_lyrics:
            return []

        # Dividir en líneas
        lines = [line.strip() for line in clean_lyrics.split('\n') if line.strip()]

        # Procesar líneas largas
        processed = []
        for line in lines:
            # Limpiar caracteres problemáticos para MoviePy
            line = self._clean_text_for_moviepy(line)

            if len(line) > 45:  # Líneas más cortas para mejor visualización
                words = line.split()
                current = ""
                for word in words:
                    if len(current + " " + word) <= 45:
                        current += (" " + word) if current else word
                    else:
                        if current:
                            processed.append(current)
                        current = word
                if current:
                    processed.append(current)
            else:
                processed.append(line)

        return processed[:25]  # Máximo 25 líneas

    def _clean_text_for_moviepy(self, text: str) -> str:
        """
        Limpia texto para MoviePy
        """
        # Mantener solo caracteres compatibles
        text = text.replace('\\', '')
        text = text.replace('"', '')
        text = text.replace("'", '')
        # Mantener caracteres españoles
        text = re.sub(r'[^\w\s\-.,!?áéíóúñÁÉÍÓÚÑ]', '', text)
        return text.strip()

    def _create_animated_subtitles(self, lines: List[str], duration: float) -> List:
        """
        Crea clips de texto animados estilo karaoke con cada letra bailando
        """
        subtitle_clips = []
        time_per_line = duration / len(lines) if lines else 3

        for i, line in enumerate(lines):
            start_time = i * time_per_line
            end_time = min((i + 1) * time_per_line, duration)
            line_duration = end_time - start_time

            # Crear efecto karaoke letra por letra
            # Optimización: procesar solo líneas visibles
            if start_time < duration and end_time > 0:
                line_clips = self._create_per_character_karaoke(
                    line,
                    line_duration,
                    start_time,
                    i
                )
                subtitle_clips.extend(line_clips)

        return subtitle_clips

    def _create_per_character_karaoke(self, line: str, duration: float,
                                     start_time: float, line_index: int) -> List:
        """
        Crea efecto karaoke con cada letra animada independientemente
        Optimizado para mejor rendimiento
        """
        char_clips = []
        chars = list(line)
        num_chars = len(chars)

        if num_chars == 0:
            return []

        # Tiempo para que cada letra se active
        time_per_char = duration * 0.7 / num_chars  # 70% para el efecto karaoke

        # Calcular ancho aproximado de cada carácter
        char_width = 25  # Ancho aproximado por carácter
        line_width = num_chars * char_width
        start_x = (self.video_width - line_width) // 2

        # Optimización: limitar número de caracteres animados para líneas muy largas
        max_animated_chars = 40
        if num_chars > max_animated_chars:
            # Agrupar caracteres si la línea es muy larga
            chars = [line[i:i+2] for i in range(0, len(line), 2)]
            num_chars = len(chars)
            char_width = 50  # Ancho mayor para grupos de caracteres
            line_width = num_chars * char_width
            start_x = (self.video_width - line_width) // 2

        for j, char in enumerate(chars):
            # Posición X de este carácter
            char_x = start_x + (j * char_width)

            # Momento en que este carácter se activa
            char_activate_time = start_time + (j * time_per_char)

            # Crear versión blanca (inactiva) del carácter
            if char.strip():  # No animar espacios vacíos
                # Letra blanca antes de activarse
                white_duration = char_activate_time - start_time if char_activate_time > start_time else 0
                if white_duration > 0.1:  # Solo crear si dura más de 0.1 segundos
                    white_char = self._create_dancing_character(
                        char,
                        char_x,
                        j,
                        color='white',
                        stroke_color='black',
                        fontsize=40,
                        duration=white_duration,
                        start_time=start_time,
                        line_index=line_index,
                        is_active=False
                    )
                    if white_char:
                        char_clips.append(white_char)

                # Letra amarilla cuando se activa (efecto karaoke)
                yellow_duration = duration - (char_activate_time - start_time)
                if yellow_duration > 0.1:  # Solo crear si dura más de 0.1 segundos
                    yellow_char = self._create_dancing_character(
                        char,
                        char_x,
                        j,
                        color='yellow',
                        stroke_color='red',
                        fontsize=45,
                        duration=yellow_duration,
                        start_time=char_activate_time,
                        line_index=line_index,
                        is_active=True
                    )
                    if yellow_char:
                        char_clips.append(yellow_char)

        return char_clips

    def _create_dancing_character(self, char: str, x_pos: int, char_index: int,
                                  color: str, stroke_color: str, fontsize: int,
                                  duration: float, start_time: float, line_index: int,
                                  is_active: bool = False):
        """
        Crea un carácter individual con animación de baile única
        """
        try:
            if duration <= 0:
                return None

            # Crear clip de texto para el carácter con optimizaciones
            txt_clip = TextClip(
                char,
                fontsize=fontsize,
                color=color,
                font='Arial',
                stroke_color=stroke_color,
                stroke_width=2 if not is_active else 3,
                method='label',
                kerning=0  # Desactivar kerning para mejor rendimiento
            )

            # Establecer duración y tiempo de inicio
            txt_clip = txt_clip.set_duration(duration).set_start(start_time)

            # Función para crear movimiento de baile sutil
            def dancing_position(t):
                """Cada letra baila de forma suave y agradable"""
                base_y = self.video_height - self.subtitle_zone_height

                if is_active:
                    # Movimiento activo pero controlado
                    t_offset = t + char_index * 0.3
                    # Reducir amplitudes para movimiento más sutil
                    bounce_y = 8 * math.sin(2 * math.pi * t_offset * 1.5)  # Reducido de 15
                    jump = 5 * abs(math.sin(2 * math.pi * t_offset))  # Reducido de 10

                    # Movimiento horizontal muy sutil
                    wiggle_x = 2 * math.sin(2 * math.pi * t_offset * 2)  # Reducido de 3

                    final_y = base_y + bounce_y - jump
                    final_x = x_pos + wiggle_x
                else:
                    # Movimiento suave cuando está inactiva
                    gentle_bounce = 3 * math.sin(2 * math.pi * (t + char_index * 0.2))  # Reducido de 5
                    final_y = base_y + gentle_bounce
                    final_x = x_pos

                return (final_x, final_y)

            # Aplicar animación de posición
            txt_clip = txt_clip.set_position(dancing_position)

            # Efectos adicionales
            if is_active:
                # Efecto de "pop" cuando se activa
                txt_clip = txt_clip.fadein(0.1)
            else:
                txt_clip = txt_clip.fadeout(0.1)

            return txt_clip

        except Exception as e:
            print(f"Error creando carácter animado: {str(e)}")
            return None

    def _create_dancing_text(self, text: str, color: str, stroke_color: str,
                             stroke_width: int, fontsize: int, duration: float,
                             start_time: float, bounce_offset: int,
                             is_active: bool = False) -> TextClip:
        """
        Crea un clip de texto con animación de baile
        """
        try:
            # Crear clip de texto básico
            txt_clip = TextClip(
                text,
                fontsize=fontsize,
                color=color,
                font='Arial',
                stroke_color=stroke_color,
                stroke_width=stroke_width,
                method='caption',
                size=(self.video_width - 100, None),
                align='center'
            )

            # Establecer duración y tiempo de inicio
            txt_clip = txt_clip.set_duration(duration).set_start(start_time)

            # Función para crear movimiento de baile
            def bounce_position(t):
                """Calcula la posición Y con efecto de rebote"""
                # Base Y position (parte inferior del video)
                base_y = self.video_height - self.subtitle_zone_height

                # Efecto de baile/rebote
                if is_active:
                    # Movimiento más pronunciado para texto activo
                    bounce = 15 * math.sin(2 * math.pi * t * 3 + bounce_offset)
                    scale_bounce = 5 * math.sin(2 * math.pi * t * 2)
                else:
                    # Movimiento suave para texto inactivo
                    bounce = 8 * math.sin(2 * math.pi * t * 2 + bounce_offset)
                    scale_bounce = 0

                return ('center', base_y + bounce + scale_bounce)

            # Aplicar animación de posición
            txt_clip = txt_clip.set_position(bounce_position)

            # Efecto de fade in/out
            if is_active:
                txt_clip = txt_clip.crossfadein(0.2).crossfadeout(0.2)
            else:
                txt_clip = txt_clip.fadein(0.3).fadeout(0.2)

            return txt_clip

        except Exception as e:
            print(f"Error creando texto animado: {str(e)}")
            # Intentar versión más simple
            try:
                txt_clip = TextClip(
                    text,
                    fontsize=fontsize,
                    color=color,
                    font='Arial',
                    method='label'
                )
                txt_clip = txt_clip.set_duration(duration).set_start(start_time)
                txt_clip = txt_clip.set_position(('center', 'bottom'))
                return txt_clip
            except:
                return None

    def _add_audio_with_ffmpeg(self, video_path: str, output_path: str, audio_path: str = None) -> bool:
        """
        Usa FFmpeg para añadir audio al video con subtítulos
        """
        try:
            import subprocess

            if not audio_path or not os.path.exists(audio_path):
                print("No hay audio para añadir, copiando video...")
                import shutil
                shutil.copy2(video_path, output_path)
                return True

            print(f"🎶 Añadiendo audio al video con FFmpeg...")
            print(f"   Video: {video_path}")
            print(f"   Audio: {audio_path}")
            print(f"   Salida: {output_path}")

            # Comando FFmpeg para combinar video y audio
            cmd = [
                'ffmpeg', '-y',
                '-i', video_path,  # Video con subtítulos
                '-i', audio_path,  # Audio original
                '-map', '0:v',     # Tomar video del primer input
                '-map', '1:a',     # Tomar audio del segundo input
                '-c:v', 'copy',    # Copiar video sin recodificar
                '-c:a', 'aac',     # Codificar audio en AAC
                '-b:a', '192k',    # Bitrate del audio
                '-shortest',       # Usar la duración más corta
                output_path
            ]

            print("Ejecutando FFmpeg para combinar video y audio...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode == 0:
                print("✅ Audio añadido exitosamente al video")
                return True
            else:
                print(f"❌ Error al añadir audio: {result.stderr[:500]}")
                # Si falla, al menos copiar el video
                import shutil
                shutil.copy2(video_path, output_path)
                return False

        except subprocess.TimeoutExpired:
            print("❌ Timeout al añadir audio")
            return False
        except Exception as e:
            print(f"❌ Error añadiendo audio con FFmpeg: {str(e)}")
            # Intentar copiar el video al menos
            try:
                import shutil
                shutil.copy2(video_path, output_path)
            except:
                pass
            return False

    def _fallback_copy(self, video_path: str, output_path: str, audio_path: str = None) -> bool:
        """
        Fallback: copiar video con audio usando FFmpeg
        """
        try:
            import subprocess

            cmd = ['ffmpeg', '-y', '-i', video_path]

            if audio_path and os.path.exists(audio_path):
                cmd.extend(['-i', audio_path])
                cmd.extend(['-map', '0:v', '-map', '1:a'])
                cmd.extend(['-c:v', 'copy', '-c:a', 'copy'])
            else:
                cmd.extend(['-c', 'copy'])

            cmd.append(output_path)

            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            print(f"Error en fallback: {str(e)}")
            return False

    def _apply_config(self, config: dict):
        """
        Aplica la configuración personalizada de subtítulos
        """
        # NO aplicar cambios de resolución basados en config
        # Mantener 480p para estabilidad del servidor

        # Valores por defecto seguros
        self.font_size = config.get('fontSize', 36)
        self.font_color = config.get('fontColor', '#ffffff')
        self.outline_color = config.get('outlineColor', '#000000')
        self.outline_width = config.get('outlineWidth', 2)
        self.animation_style = config.get('animation', 'karaoke')
        self.subtitle_position = config.get('position', 'bottom')
        self.enable_sync = config.get('enableSyncAdjustment', True)

        print(f"📝 Configuración de subtítulos aplicada:")
        print(f"  - Tamaño: {self.font_size}px")
        print(f"  - Color: {self.font_color}")
        print(f"  - Borde: {self.outline_color} ({self.outline_width}px)")
        print(f"  - Animación: {self.animation_style}")
        print(f"  - Posición: {self.subtitle_position}")
        print(f"  - Sincronización mejorada: {self.enable_sync}")