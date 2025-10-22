import os
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import tempfile
import subprocess
from typing import List, Tuple
import math


class ImageSubtitleGenerator:
    """
    Genera subtítulos como imágenes PNG con transparencia para superponer en video
    Evita problemas de Fontconfig en Windows
    """

    def __init__(self):
        self.width = 1280
        self.height = 720
        self.subtitle_height = 150

    def create_subtitle_overlay(self, video_path: str, output_path: str, lyrics: str,
                                audio_path: str = None, duration: float = 0) -> bool:
        """
        Crea un video con subtítulos renderizados como imágenes
        """
        try:
            # Preparar las letras
            lines = self._prepare_lyrics(lyrics)
            if not lines:
                print("No hay letras para procesar")
                return self._copy_with_audio(video_path, output_path, audio_path)

            # Crear directorio temporal para las imágenes de subtítulos
            temp_dir = tempfile.mkdtemp(prefix='subtitles_')

            # Generar imágenes de subtítulos
            print("Generando imágenes de subtítulos karaoke...")
            subtitle_images = self._generate_subtitle_images(lines, duration, temp_dir)

            if not subtitle_images:
                print("No se pudieron generar imágenes de subtítulos")
                return self._copy_with_audio(video_path, output_path, audio_path)

            # Aplicar subtítulos al video
            success = self._apply_image_subtitles(video_path, output_path, subtitle_images, audio_path)

            # Limpiar archivos temporales
            self._cleanup_temp_files(temp_dir)

            return success

        except Exception as e:
            print(f"Error creando subtítulos con imágenes: {str(e)}")
            return self._copy_with_audio(video_path, output_path, audio_path)

    def _prepare_lyrics(self, lyrics: str) -> List[str]:
        """
        Prepara las letras dividiéndolas en líneas apropiadas
        """
        import re
        # Limpiar el texto
        clean_lyrics = re.sub(r'\[.*?\]', '', lyrics)  # Remover etiquetas
        clean_lyrics = re.sub(r'\n+', '\n', clean_lyrics)  # Normalizar saltos
        clean_lyrics = clean_lyrics.strip()

        if not clean_lyrics:
            return []

        # Dividir en líneas y filtrar vacías
        lines = [line.strip() for line in clean_lyrics.split('\n') if line.strip()]

        # Procesar líneas muy largas
        processed_lines = []
        for line in lines:
            if len(line) > 50:  # Si es muy larga, dividirla
                words = line.split()
                current_line = ""
                for word in words:
                    if len(current_line + " " + word) <= 50:
                        current_line += (" " + word) if current_line else word
                    else:
                        if current_line:
                            processed_lines.append(current_line)
                        current_line = word
                if current_line:
                    processed_lines.append(current_line)
            else:
                processed_lines.append(line)

        return processed_lines[:20]  # Máximo 20 líneas

    def _generate_subtitle_images(self, lines: List[str], duration: float, temp_dir: str) -> List[dict]:
        """
        Genera imágenes PNG con los subtítulos estilo karaoke
        """
        subtitle_images = []
        time_per_line = duration / len(lines) if lines and duration > 0 else 5

        try:
            # Intentar usar una fuente del sistema o usar fuente por defecto
            try:
                font_large = ImageFont.truetype("arial.ttf", 48)
                font_medium = ImageFont.truetype("arial.ttf", 42)
            except:
                # Si no encuentra arial, usar fuente por defecto
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                print("Usando fuente por defecto (puede verse pequeña)")

            for i, line in enumerate(lines):
                start_time = i * time_per_line
                end_time = (i + 1) * time_per_line
                mid_time = (start_time + end_time) / 2

                # Generar 3 versiones del subtítulo (para efecto karaoke)

                # 1. Versión blanca (primera mitad)
                img_white = self._create_text_image(
                    line, font_medium,
                    text_color=(255, 255, 255),
                    outline_color=(0, 0, 0),
                    outline_width=3,
                    y_offset=self._calculate_bounce(i, 0)
                )
                white_path = os.path.join(temp_dir, f"subtitle_{i:04d}_white.png")
                img_white.save(white_path)

                subtitle_images.append({
                    'path': white_path,
                    'start': start_time,
                    'end': mid_time,
                    'type': 'white'
                })

                # 2. Versión amarilla (segunda mitad)
                img_yellow = self._create_text_image(
                    line, font_large,
                    text_color=(255, 255, 0),
                    outline_color=(255, 0, 0),
                    outline_width=4,
                    y_offset=self._calculate_bounce(i, 1)
                )
                yellow_path = os.path.join(temp_dir, f"subtitle_{i:04d}_yellow.png")
                img_yellow.save(yellow_path)

                subtitle_images.append({
                    'path': yellow_path,
                    'start': mid_time,
                    'end': end_time,
                    'type': 'yellow'
                })

            return subtitle_images

        except Exception as e:
            print(f"Error generando imágenes de subtítulos: {str(e)}")
            return []

    def _create_text_image(self, text: str, font, text_color: Tuple[int, int, int],
                          outline_color: Tuple[int, int, int], outline_width: int,
                          y_offset: int = 0) -> Image:
        """
        Crea una imagen PNG con texto y transparencia
        """
        # Crear imagen transparente
        img = Image.new('RGBA', (self.width, self.subtitle_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Calcular posición del texto
        try:
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
        except:
            # Fallback para versiones antiguas de Pillow
            text_width, text_height = draw.textsize(text, font=font)

        x = (self.width - text_width) // 2
        y = (self.subtitle_height - text_height) // 2 + y_offset

        # Dibujar outline (borde)
        for dx in range(-outline_width, outline_width + 1):
            for dy in range(-outline_width, outline_width + 1):
                if dx != 0 or dy != 0:
                    draw.text((x + dx, y + dy), text, font=font, fill=outline_color + (255,))

        # Dibujar texto principal
        draw.text((x, y), text, font=font, fill=text_color + (255,))

        return img

    def _calculate_bounce(self, line_index: int, phase: int) -> int:
        """
        Calcula el desplazamiento vertical para efecto de baile
        """
        amplitude = 10 + (line_index % 3) * 5
        offset = math.sin(line_index * 0.5 + phase * math.pi) * amplitude
        return int(offset)

    def _apply_image_subtitles(self, video_path: str, output_path: str,
                              subtitle_images: List[dict], audio_path: str = None) -> bool:
        """
        Aplica las imágenes de subtítulos al video usando FFmpeg
        """
        try:
            # Construir filtro complejo para superponer las imágenes
            filter_parts = []

            for i, subtitle in enumerate(subtitle_images):
                # Cada imagen se superpone en su tiempo específico
                filter_parts.append(
                    f"[{i+1}:v]format=rgba,colorchannelmixer=aa=1.0[sub{i}];"
                    f"[0:v][sub{i}]overlay=x=0:y=H-{self.subtitle_height}:"
                    f"enable='between(t,{subtitle['start']:.2f},{subtitle['end']:.2f})'[v{i}]"
                )

            # Construir comando FFmpeg
            ffmpeg_cmd = ['ffmpeg']

            # Video input
            ffmpeg_cmd.extend(['-i', video_path])

            # Imagen inputs
            for subtitle in subtitle_images:
                ffmpeg_cmd.extend(['-loop', '1', '-t', '1', '-i', subtitle['path']])

            # Audio input si existe
            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])

            # Si hay subtítulos, aplicar filtros
            if filter_parts:
                # Conectar todos los filtros en cadena
                filter_complex = ""
                last_output = "0:v"

                for i, subtitle in enumerate(subtitle_images):
                    if i == 0:
                        filter_complex += f"[1:v]format=rgba[sub0];"
                        filter_complex += f"[0:v][sub0]overlay=x=0:y=H-{self.subtitle_height}:"
                        filter_complex += f"enable='between(t,{subtitle['start']:.2f},{subtitle['end']:.2f})'"
                    else:
                        filter_complex += f"[{i+1}:v]format=rgba[sub{i}];"
                        filter_complex += f"[v{i-1}][sub{i}]overlay=x=0:y=H-{self.subtitle_height}:"
                        filter_complex += f"enable='between(t,{subtitle['start']:.2f},{subtitle['end']:.2f})'"

                    if i < len(subtitle_images) - 1:
                        filter_complex += f"[v{i}];"

                ffmpeg_cmd.extend(['-filter_complex', filter_complex])
                ffmpeg_cmd.extend(['-map', f'[v{len(subtitle_images)-1}]'])
            else:
                ffmpeg_cmd.extend(['-map', '0:v'])

            # Mapear audio si existe
            if audio_path and os.path.exists(audio_path):
                audio_index = len(subtitle_images) + 1
                ffmpeg_cmd.extend(['-map', f'{audio_index}:a', '-c:a', 'copy'])

            # Configuración de salida
            ffmpeg_cmd.extend([
                '-c:v', 'libx264',
                '-preset', 'fast',
                '-crf', '23',
                '-pix_fmt', 'yuv420p',
                '-y',
                output_path
            ])

            print("Aplicando subtítulos renderizados como imágenes...")

            # Ejecutar comando
            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, timeout=300)

            if result.returncode == 0:
                print("¡Subtítulos karaoke aplicados exitosamente!")
                return True
            else:
                print(f"Error aplicando subtítulos: {result.stderr[:500]}")
                return False

        except Exception as e:
            print(f"Error en _apply_image_subtitles: {str(e)}")
            return False

    def _copy_with_audio(self, video_path: str, output_path: str, audio_path: str = None) -> bool:
        """
        Copia el video con audio como fallback
        """
        try:
            ffmpeg_cmd = ['ffmpeg', '-i', video_path]

            if audio_path and os.path.exists(audio_path):
                ffmpeg_cmd.extend(['-i', audio_path])
                ffmpeg_cmd.extend([
                    '-map', '0:v',
                    '-map', '1:a',
                    '-c:v', 'copy',
                    '-c:a', 'copy'
                ])
            else:
                ffmpeg_cmd.extend(['-c:v', 'copy', '-an'])

            ffmpeg_cmd.extend(['-y', output_path])

            result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True)
            return result.returncode == 0

        except Exception as e:
            print(f"Error en fallback: {str(e)}")
            return False

    def _cleanup_temp_files(self, temp_dir: str):
        """
        Limpia los archivos temporales
        """
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
        except:
            pass