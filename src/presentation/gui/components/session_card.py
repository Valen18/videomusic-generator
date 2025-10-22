import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
from datetime import datetime
from typing import Optional, Callable
import pygame
import threading
import time

from ..styles import ThemeManager, create_status_badge


class SessionCard(ttk.Frame):
    def __init__(self, parent, session, on_play_callback=None, on_generate_image_callback=None, on_generate_video_callback=None, on_loop_video_callback=None):
        super().__init__(parent, style='Card.TFrame')
        self.session = session
        self.on_play_callback = on_play_callback
        self.on_generate_image_callback = on_generate_image_callback
        self.on_generate_video_callback = on_generate_video_callback
        self.on_loop_video_callback = on_loop_video_callback
        self.is_playing = False
        self.audio_loaded = False
        self.current_track_index = 0
        self.available_tracks = []
        self.is_processing_video = False  # Flag to prevent multiple clicks
        self.is_processing_image = False  # Flag to prevent multiple clicks
        self.is_processing_loop = False  # Flag to prevent multiple clicks
        
        # Initialize pygame mixer for audio (only once globally)
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except:
            pass
        
        self.setup_ui()
    
    def setup_ui(self):
        # Configure card style
        self.configure(padding=10, relief='raised', borderwidth=1)
        
        # Main container
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True)
        
        # Left side - Image thumbnail
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side='left', padx=(0, 15))
        
        self.image_label = ttk.Label(left_frame)
        self.image_label.pack()
        
        # Load and display image thumbnail or placeholder
        self.load_thumbnail()
        
        # Right side - Content
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side='left', fill='both', expand=True)
        
        # Title and metadata
        title_frame = ttk.Frame(right_frame)
        title_frame.pack(fill='x', pady=(0, 5))
        
        # Title (bold and larger)
        title_label = ttk.Label(
            title_frame, 
            text=self.session.request.title, 
            font=('Segoe UI', 12, 'bold'),
            foreground='#2c3e50'
        )
        title_label.pack(anchor='w')
        
        # Subtitle with style and model
        subtitle_text = f"{self.session.request.style} • {self.session.request.model.value}"
        if self.session.request.instrumental:
            subtitle_text += " • Instrumental"
        
        subtitle_label = ttk.Label(
            title_frame, 
            text=subtitle_text,
            font=('Segoe UI', 9),
            foreground='#7f8c8d'
        )
        subtitle_label.pack(anchor='w')
        
        # Status badges
        status_frame = ttk.Frame(right_frame)
        status_frame.pack(fill='x', pady=(5, 10))
        
        # Music status badge
        music_status = "completed" if (self.session.response and self.session.response.is_completed) else "processing"
        music_badge = create_status_badge(status_frame, music_status)
        music_badge.pack(side='left', padx=(0, 10))
        
        # Image status badge
        image_status = "with_image" if (self.session.image_response and self.session.image_response.has_images) else "without_image"
        image_badge = create_status_badge(status_frame, image_status)
        image_badge.pack(side='left')
        
        # Date
        date_str = datetime.fromtimestamp(self.session.timestamp).strftime("%d/%m/%Y %H:%M")
        date_label = ttk.Label(
            status_frame,
            text=date_str,
            font=('Segoe UI', 8),
            foreground='#95a5a6'
        )
        date_label.pack(side='right')
        
        # Controls frame
        controls_frame = ttk.Frame(right_frame)
        controls_frame.pack(fill='x', pady=(5, 0))
        
        # Audio controls (only if audio exists)
        if self.has_audio():
            tracks = self.get_available_tracks()
            
            if len(tracks) <= 1:
                # Single track - simple play button
                self.play_button = ttk.Button(
                    controls_frame,
                    text="▶ Reproducir",
                    command=self.toggle_audio,
                    style='Success.TButton'
                )
                self.play_button.pack(side='left', padx=(0, 10))
            else:
                # Multiple tracks - intuitive track controls
                audio_frame = ttk.Frame(controls_frame)
                audio_frame.pack(side='left', padx=(0, 10))
                
                # Track info label
                self.track_label = ttk.Label(
                    audio_frame,
                    text=f"Track 1/{len(tracks)}",
                    font=('Segoe UI', 8),
                    foreground='#666'
                )
                self.track_label.pack(pady=(0, 2))
                
                # Controls row
                controls_row = ttk.Frame(audio_frame)
                controls_row.pack()
                
                # Previous track button
                self.prev_button = ttk.Button(
                    controls_row,
                    text="⏮",
                    command=self.previous_track,
                    style='Small.TButton',
                    width=3
                )
                self.prev_button.pack(side='left', padx=(0, 2))
                
                # Main play/pause button
                self.play_button = ttk.Button(
                    controls_row,
                    text="▶ Reproducir",
                    command=self.toggle_audio,
                    style='Success.TButton'
                )
                self.play_button.pack(side='left', padx=(2, 2))
                
                # Next track button
                self.next_button = ttk.Button(
                    controls_row,
                    text="⏭",
                    command=self.next_track,
                    style='Small.TButton',
                    width=3
                )
                self.next_button.pack(side='left', padx=(2, 0))
                
                # Update initial button text
                self.update_play_button_text()
                self.update_track_navigation_buttons()
        
        # Generate image button (only if no image exists)
        if not (self.session.image_response and self.session.image_response.has_images):
            self.generate_image_btn = ttk.Button(
                controls_frame,
                text="🎨 Generar Imagen",
                command=self.generate_image,
                style='Primary.TButton'
            )
            self.generate_image_btn.pack(side='left', padx=(0, 10))
        
        # Video controls based on current state
        elif (self.session.image_response and self.session.image_response.has_images):
            video_frame = ttk.Frame(controls_frame)
            video_frame.pack(side='left', padx=(0, 10))
            
            has_video_response = self.session.video_response and self.session.video_response.has_video
            has_video_file = self.session.video_path and os.path.exists(self.session.video_path)
            has_original_video = self._has_original_video()
            
            if not has_video_response:
                # No video generated yet - show generate button
                self.generate_video_btn = ttk.Button(
                    video_frame,
                    text="🎬 Animar Portada",
                    command=self.generate_video,
                    style='Warning.TButton'
                )
                self.generate_video_btn.pack()
            
            elif has_video_response and not has_video_file:
                # Video was generated but loop not created or failed
                if has_original_video:
                    # Original exists, offer to create loop
                    self.loop_btn = ttk.Button(
                        video_frame,
                        text="🔄 Crear Bucle",
                        command=self.create_video_loop,
                        style='Info.TButton'
                    )
                    self.loop_btn.pack()
                else:
                    # Need to regenerate everything
                    generate_video_btn = ttk.Button(
                        video_frame,
                        text="🎬 Regenerar Video",
                        command=self.generate_video,
                        style='Warning.TButton'
                    )
                    generate_video_btn.pack()
            
            else:
                # Everything is working - show status and options
                video_controls = ttk.Frame(video_frame)
                video_controls.pack()
                
                status_label = ttk.Label(
                    video_controls,
                    text="✅ Video listo",
                    font=('Segoe UI', 9),
                    foreground='#27ae60'
                )
                status_label.pack(side='left', padx=(0, 5))
                
                # Options to regenerate loop
                self.regenerate_loop_btn = ttk.Button(
                    video_controls,
                    text="🔄",
                    command=self.create_video_loop,
                    style='Small.TButton',
                    width=3
                )
                self.regenerate_loop_btn.pack(side='left', padx=(2, 2))
                
                # Button for subtitles toggle
                subtitles_btn = ttk.Button(
                    video_controls,
                    text="🎤",
                    command=self.toggle_subtitles_info,
                    style='Small.TButton',
                    width=3
                )
                subtitles_btn.pack(side='left', padx=(0, 0))
        
        # Details button
        details_btn = ttk.Button(
            controls_frame,
            text="📋 Detalles",
            command=self.show_details,
            style='Small.TButton'
        )
        details_btn.pack(side='left', padx=(0, 10))
        
        # Open folder button
        if self.session.local_path and os.path.exists(self.session.local_path):
            folder_btn = ttk.Button(
                controls_frame,
                text="📁 Abrir",
                command=self.open_folder,
                style='Small.TButton'
            )
            folder_btn.pack(side='right')
    
    def load_thumbnail(self):
        """Load and display image thumbnail or placeholder"""
        try:
            if self.session.image_path and os.path.exists(self.session.image_path):
                # Load actual image
                image = Image.open(self.session.image_path)
                image = image.resize((120, 68), Image.Resampling.LANCZOS)  # 16:9 aspect ratio
                self.thumbnail = ImageTk.PhotoImage(image)
                self.image_label.configure(image=self.thumbnail)
            else:
                # Create placeholder
                self.create_placeholder()
        except Exception as e:
            print(f"Error loading thumbnail: {e}")
            self.create_placeholder()
    
    def create_placeholder(self):
        """Create a placeholder image"""
        try:
            # Create a simple colored rectangle as placeholder
            placeholder = Image.new('RGB', (120, 68), '#ecf0f1')
            
            # You could add text or icons here if PIL supports it
            self.thumbnail = ImageTk.PhotoImage(placeholder)
            self.image_label.configure(image=self.thumbnail)
        except Exception as e:
            print(f"Error creating placeholder: {e}")
            # Fallback to text label
            self.image_label.configure(text="🎵\nSin\nImagen", background='#ecf0f1')
    
    def has_audio(self):
        """Check if the session has downloadable audio"""
        return (
            self.session.response and 
            self.session.response.has_downloadable_tracks and
            self.session.local_path and 
            os.path.exists(self.session.local_path)
        )
    
    def get_available_tracks(self):
        """Get all available audio files"""
        if not self.has_audio():
            return []
        
        if self.available_tracks:  # Cache results
            return self.available_tracks
        
        try:
            tracks = []
            for file in sorted(os.listdir(self.session.local_path)):
                if file.endswith(('.mp3', '.wav', '.ogg')):
                    full_path = os.path.join(self.session.local_path, file)
                    # Extract track number from filename if possible
                    track_name = file.replace('.mp3', '').replace('.wav', '').replace('.ogg', '')
                    tracks.append({
                        'path': full_path,
                        'filename': file,
                        'display_name': track_name
                    })
            self.available_tracks = tracks
            return tracks
        except:
            return []
    
    def get_current_audio_file(self):
        """Get the currently selected audio file"""
        tracks = self.get_available_tracks()
        if tracks and self.current_track_index < len(tracks):
            return tracks[self.current_track_index]['path']
        return None
    
    def toggle_audio(self):
        """Play or pause audio"""
        try:
            if not self.is_playing:
                audio_file = self.get_current_audio_file()
                if audio_file:
                    pygame.mixer.music.load(audio_file)
                    pygame.mixer.music.play()
                    self.is_playing = True
                    self.update_play_button_text()
                    
                    # Start monitoring thread
                    threading.Thread(target=self.monitor_playback, daemon=True).start()
            else:
                pygame.mixer.music.stop()
                self.is_playing = False
                self.update_play_button_text()
        except Exception as e:
            print(f"Error playing audio: {e}")
    
    def play_track(self, track_index):
        """Play a specific track"""
        tracks = self.get_available_tracks()
        if track_index < len(tracks):
            # Stop current playback if any
            if self.is_playing:
                pygame.mixer.music.stop()
                self.is_playing = False
            
            self.current_track_index = track_index
            self.update_track_selection_ui()  # Update visual indicators
            self.toggle_audio()  # Start playing the new track
    
    def previous_track(self):
        """Switch to previous track"""
        tracks = self.get_available_tracks()
        if len(tracks) > 1:
            new_index = (self.current_track_index - 1) % len(tracks)
            self.play_track(new_index)
    
    def next_track(self):
        """Switch to next track"""
        tracks = self.get_available_tracks()
        if len(tracks) > 1:
            new_index = (self.current_track_index + 1) % len(tracks)
            self.play_track(new_index)
    
    def update_track_navigation_buttons(self):
        """Update the state of navigation buttons"""
        tracks = self.get_available_tracks()
        if len(tracks) <= 1:
            return
        
        if hasattr(self, 'prev_button') and hasattr(self, 'next_button'):
            # Always enable both buttons for cycling through tracks
            self.prev_button.configure(state='normal')
            self.next_button.configure(state='normal')
        
        if hasattr(self, 'track_label'):
            track_num = self.current_track_index + 1
            self.track_label.configure(text=f"Track {track_num}/{len(tracks)}")
    
    def update_track_selection_ui(self):
        """Update track selection UI"""
        self.update_track_navigation_buttons()
        self.update_play_button_text()
    
    def update_play_button_text(self):
        """Update play button text with track info"""
        if hasattr(self, 'play_button'):
            tracks = self.get_available_tracks()
            if len(tracks) <= 1:
                # Single track - simple play/pause
                if self.is_playing:
                    self.play_button.configure(text="⏸ Pausar")
                else:
                    self.play_button.configure(text="▶ Reproducir")
            else:
                # Multiple tracks - simple play/pause (track info is in label)
                if self.is_playing:
                    self.play_button.configure(text="⏸ Pausar")
                else:
                    self.play_button.configure(text="▶ Reproducir")
    
    def monitor_playback(self):
        """Monitor audio playback to update button state"""
        while self.is_playing:
            if not pygame.mixer.music.get_busy():
                self.is_playing = False
                # Update button in main thread
                self.after(0, self.update_play_button_text)
                break
            time.sleep(0.5)
    
    def generate_image(self):
        """Trigger image generation for this session"""
        if self.is_processing_image:
            return  # Prevent multiple clicks

        if self.on_generate_image_callback:
            self.is_processing_image = True
            if hasattr(self, 'generate_image_btn'):
                self.generate_image_btn.config(state='disabled', text="⏳ Generando...")
            self.on_generate_image_callback(self.session)
    
    def generate_video(self):
        """Trigger video generation for this session"""
        if self.is_processing_video:
            return  # Prevent multiple clicks

        if self.on_generate_video_callback:
            self.is_processing_video = True
            if hasattr(self, 'generate_video_btn'):
                self.generate_video_btn.config(state='disabled', text="⏳ Animando...")
            self.on_generate_video_callback(self.session)
    
    def create_video_loop(self):
        """Trigger video loop creation for this session"""
        if self.is_processing_loop:
            return  # Prevent multiple clicks

        if self.on_loop_video_callback:
            self.is_processing_loop = True
            if hasattr(self, 'loop_btn'):
                self.loop_btn.config(state='disabled', text="⏳ Creando bucle...")
            if hasattr(self, 'regenerate_loop_btn'):
                self.regenerate_loop_btn.config(state='disabled')
            self.on_loop_video_callback(self.session)
    
    def _has_original_video(self) -> bool:
        """Check if the original video file exists"""
        if not self.session.local_path:
            return False
        
        original_video_path = os.path.join(
            self.session.local_path, 
            f"{self.session.session_id}_animation_original.mp4"
        )
        return os.path.exists(original_video_path)
    
    def toggle_subtitles_info(self):
        """Show information about subtitle features"""
        import tkinter.messagebox as msgbox
        msgbox.showinfo(
            "Subtítulos Karaoke", 
            "🎤 ¡Nuevos subtítulos animados!\n\n"
            "• Los videos ahora incluyen letras tipo karaoke\n"
            "• El texto se rellena progresivamente\n" 
            "• Efectos de baile sincronizados\n"
            "• Posición centrada en la parte baja\n\n"
            "Usa el botón 🔄 para recrear el bucle con las últimas mejoras."
        )
    
    def show_details(self):
        """Show detailed information in a popup"""
        details_window = tk.Toplevel()
        details_window.title(f"Detalles - {self.session.request.title}")
        details_window.geometry("600x500")
        details_window.configure(bg='white')
        
        # Create scrollable text widget
        text_frame = ttk.Frame(details_window)
        text_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, font=('Segoe UI', 10))
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Generate details text
        details = self.generate_details_text()
        text_widget.insert(1.0, details)
        text_widget.configure(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Close button
        close_btn = ttk.Button(
            details_window,
            text="Cerrar",
            command=details_window.destroy
        )
        close_btn.pack(pady=10)
    
    def generate_details_text(self):
        """Generate detailed text information"""
        details = f"🎵 INFORMACIÓN DE LA CANCIÓN\n{'='*50}\n\n"
        details += f"Título: {self.session.request.title}\n"
        details += f"Estilo: {self.session.request.style}\n"
        details += f"Modelo: {self.session.request.model.value}\n"
        details += f"Modo personalizado: {'Sí' if self.session.request.custom_mode else 'No'}\n"
        details += f"Instrumental: {'Sí' if self.session.request.instrumental else 'No'}\n\n"
        
        details += f"📝 LETRA:\n{'-'*20}\n{self.session.request.prompt}\n\n"
        
        if self.session.response:
            details += f"🎼 ESTADO DE GENERACIÓN\n{'-'*30}\n"
            details += f"Estado: {self.session.response.status}\n"
            details += f"ID de petición: {self.session.response.request_id}\n"
            details += f"Número de tracks: {len(self.session.response.tracks)}\n"
            if self.session.local_path:
                details += f"Ruta local: {self.session.local_path}\n"
        
        if self.session.image_response:
            details += f"\n🖼 INFORMACIÓN DE IMAGEN\n{'-'*30}\n"
            details += f"Estado: {self.session.image_response.status}\n"
            details += f"ID de predicción: {self.session.image_response.prediction_id}\n"
            if self.session.image_response.has_images:
                details += f"Imágenes generadas: {len(self.session.image_response.image_urls)}\n"
            if self.session.image_path:
                details += f"Ruta imagen: {self.session.image_path}\n"
        else:
            details += f"\n🖼 INFORMACIÓN DE IMAGEN\n{'-'*30}\n"
            details += "Sin imagen generada\n"
        
        if self.session.video_response:
            details += f"\n🎬 INFORMACIÓN DE VIDEO\n{'-'*30}\n"
            details += f"Estado: {self.session.video_response.status}\n"
            details += f"ID de predicción: {self.session.video_response.prediction_id}\n"
            if self.session.video_response.has_video:
                details += f"Video URL: {self.session.video_response.video_url}\n"
            if self.session.video_path:
                details += f"Ruta video: {self.session.video_path}\n"
            if self.session.video_response.error:
                details += f"Error: {self.session.video_response.error}\n"
        else:
            details += f"\n🎬 INFORMACIÓN DE VIDEO\n{'-'*30}\n"
            details += "Sin video animado generado\n"
        
        return details
    
    def reset_processing_state(self):
        """Reset all processing states - called after operations complete or fail"""
        self.is_processing_video = False
        self.is_processing_image = False
        self.is_processing_loop = False

    def open_folder(self):
        """Open the session folder in file explorer"""
        if self.session.local_path and os.path.exists(self.session.local_path):
            try:
                import subprocess
                import platform

                if platform.system() == "Windows":
                    subprocess.Popen(f'explorer "{self.session.local_path}"')
                elif platform.system() == "Darwin":  # macOS
                    subprocess.Popen(['open', self.session.local_path])
                else:  # Linux
                    subprocess.Popen(['xdg-open', self.session.local_path])
            except Exception as e:
                print(f"Error opening folder: {e}")