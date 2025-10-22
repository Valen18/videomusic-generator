import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import asyncio
import threading
from typing import Optional

from ...domain.entities.song_request import SongRequest, ModelVersion
from ...infrastructure.config.settings import Settings
from ...infrastructure.adapters.suno_api_client import SunoAPIClient
from ...infrastructure.adapters.local_file_storage import LocalFileStorage
from ...infrastructure.adapters.replicate_image_client import ReplicateImageClient
from ...infrastructure.adapters.replicate_video_client import ReplicateVideoClient
from ...infrastructure.adapters.openai_lyrics_client import OpenAILyricsClient
from ...application.use_cases.generate_song import GenerateSongUseCase
from ...application.use_cases.list_sessions import ListSessionsUseCase
from .history_tab import HistoryTab
from .styles import ThemeManager
from .settings_window import SettingsWindow
from ...infrastructure.config.settings import ConfigManager
from ...infrastructure.adapters.usage_tracker import get_tracker, APIUsage


class MainWindow:
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("VideoMusic Generator - SunoAPI")
        self.root.geometry("800x700")

        # Configure styles after creating the main window
        ThemeManager.setup_styles()

        # Initialize config manager and usage tracker
        self.config_manager = ConfigManager()
        self.usage_tracker = get_tracker()

        # Intentar cargar configuración desde variables de entorno
        try:
            self.settings = Settings.from_env()
            self.has_valid_config = True
        except ValueError as e:
            # Si no hay configuración válida, usar valores por defecto
            print(f"Configuración incompleta: {str(e)}")
            self.settings = None
            self.has_valid_config = False

        # Inicializar clientes solo si hay configuración válida
        if self.has_valid_config:
            self.suno_client = SunoAPIClient(self.settings.suno_api_key)
            self.file_storage = LocalFileStorage(self.settings.output_directory)
        else:
            self.suno_client = None
            # Usar directorio por defecto si no hay configuración
            self.file_storage = LocalFileStorage("output")

        # Initialize OpenAI client
        import os
        openai_api_key = os.getenv('OPENAI_API_KEY')
        openai_assistant_id = os.getenv('OPENAI_ASSISTANT_ID', 'asst_tR6OL8QLpSsDDlc6hKdBmVNU')

        if openai_api_key:
            self.openai_client = OpenAILyricsClient(
                api_key=openai_api_key,
                assistant_id=openai_assistant_id
            )
            self.openai_available = True
        else:
            self.openai_client = None
            self.openai_available = False
            print("Warning: OPENAI_API_KEY no configurado. Generación de letras con IA no disponible.")
        
        # Inicializar clientes de Replicate si existe el token
        self.image_client = None
        self.video_client = None
        self.replicate_available = False
        try:
            import os
            replicate_token = os.getenv('REPLICATE_API_TOKEN')
            print(f"DEBUG: REPLICATE_API_TOKEN = {'***' if replicate_token else 'None'}")
            if replicate_token and replicate_token.strip():
                self.image_client = ReplicateImageClient(replicate_token)
                self.video_client = ReplicateVideoClient(replicate_token)
                self.replicate_available = True
                print("DEBUG: Replicate clients initialized successfully")
            else:
                print("DEBUG: REPLICATE_API_TOKEN not found or empty")
        except Exception as e:
            print(f"Warning: No se pudo inicializar Replicate clients: {str(e)}")
            self.replicate_available = False
        
        # Inicializar caso de uso solo si hay configuración válida
        if self.has_valid_config:
            self.generate_use_case = GenerateSongUseCase(
                self.suno_client,
                self.file_storage,
                self.image_client
            )
        else:
            self.generate_use_case = None
        self.list_sessions_use_case = ListSessionsUseCase(self.file_storage)
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create menu bar
        self.create_menu()

        # Si no hay configuración válida, mostrar mensaje informativo
        if not self.has_valid_config:
            info_frame = ttk.Frame(self.root)
            info_frame.pack(fill='x', padx=10, pady=5)

            info_label = ttk.Label(
                info_frame,
                text="⚠️ Configuración requerida: Ve a Archivo → Configuración para agregar tus API keys",
                foreground="orange",
                font=("Arial", 10, "bold")
            )
            info_label.pack(pady=5)

        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)

        self.create_generation_tab(notebook)
        self.create_new_history_tab(notebook)

    def create_menu(self):
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="⚙️ Configuración", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.root.quit)

        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        tools_menu.add_command(label="📊 Dashboard de Gastos", command=self.open_dashboard)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Acerca de", command=self.show_about)

    def open_settings(self):
        SettingsWindow(self.root, self.on_settings_changed)

    def on_settings_changed(self):
        """Callback cuando se actualizan las configuraciones"""
        # Intentar recargar configuración
        try:
            # Recargar configuración desde variables de entorno y archivos
            self.config_manager = ConfigManager()
            api_settings = self.config_manager.get_api_settings()

            # Si tenemos una API key de Suno válida, crear configuración
            if api_settings.suno_api_key and api_settings.suno_api_key.strip():
                # Crear configuración temporal
                import os
                os.environ['SUNO_API_KEY'] = api_settings.suno_api_key
                if api_settings.suno_base_url:
                    os.environ['SUNO_BASE_URL'] = api_settings.suno_base_url

                try:
                    self.settings = Settings.from_env()
                    self.has_valid_config = True

                    # Reinicializar clientes
                    self.suno_client = SunoAPIClient(self.settings.suno_api_key)
                    self.file_storage = LocalFileStorage(self.settings.output_directory)

                    # Reinicializar caso de uso
                    self.generate_use_case = GenerateSongUseCase(
                        self.suno_client,
                        self.file_storage,
                        self.image_client
                    )

                    messagebox.showinfo("Configuración", "Configuración actualizada exitosamente. ¡Ya puedes generar música!")
                    return

                except ValueError:
                    pass

            messagebox.showinfo("Configuración", "Configuración guardada. Asegúrate de completar todas las API keys requeridas.")

        except Exception as e:
            messagebox.showerror("Error", f"Error al actualizar configuración: {str(e)}")

    def open_dashboard(self):
        # Abrir solo la pestaña de dashboard
        settings_window = SettingsWindow(self.root)
        # Cambiar a la pestaña de dashboard programáticamente
        # (esto se puede mejorar en la implementación de SettingsWindow)

    def show_about(self):
        messagebox.showinfo(
            "Acerca de",
            "VideoMusic Generator\n\n"
            "Generador de música y videos con IA\n"
            "Usando SunoAPI, Replicate y OpenAI\n\n"
            "© 2024"
        )
        
    def create_generation_tab(self, parent):
        generation_frame = ttk.Frame(parent)
        parent.add(generation_frame, text="Generar Canción")
        
        main_frame = ttk.Frame(generation_frame)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # AI Generation frame
        ai_frame = ttk.LabelFrame(main_frame, text="Generación con IA")
        ai_frame.pack(fill='x', pady=(0, 10))

        # Description input
        desc_frame = ttk.Frame(ai_frame)
        desc_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(desc_frame, text="Descripción para generar letra:").pack(anchor='w', pady=(0, 5))

        desc_input_frame = ttk.Frame(desc_frame)
        desc_input_frame.pack(fill='x')

        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(desc_input_frame, textvariable=self.description_var, width=50)
        self.description_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))

        self.generate_lyrics_button = ttk.Button(desc_input_frame, text="Generar Letra con IA",
                                                command=self.generate_lyrics_with_ai)
        self.generate_lyrics_button.pack(side='left')

        # Disable button if OpenAI is not available
        if not self.openai_available:
            self.generate_lyrics_button.config(state='disabled')
            ttk.Label(desc_frame, text="(Requiere OPENAI_API_KEY en .env)",
                     foreground="red").pack(anchor='w', padx=(10, 0))

        # Lyrics input
        ttk.Label(main_frame, text="Letra generada:").pack(anchor='w', pady=(10, 5))
        self.lyrics_text = scrolledtext.ScrolledText(main_frame, height=8, wrap=tk.WORD)
        self.lyrics_text.pack(fill='both', expand=True, pady=(0, 10))
        
        # Configuration frame
        config_frame = ttk.LabelFrame(main_frame, text="Configuración")
        config_frame.pack(fill='x', pady=(0, 10))
        
        # Row 1: Title and Style
        row1_frame = ttk.Frame(config_frame)
        row1_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(row1_frame, text="Título:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.title_var = tk.StringVar()
        ttk.Entry(row1_frame, textvariable=self.title_var, width=25).grid(row=0, column=1, padx=(0, 20))
        
        ttk.Label(row1_frame, text="Estilo:").grid(row=0, column=2, sticky='w', padx=(0, 5))
        self.style_var = tk.StringVar()
        style_combo = ttk.Combobox(row1_frame, textvariable=self.style_var, width=25)
        style_combo['values'] = (
            "children's song, playful, educational",
            "nursery rhyme, gentle, soothing",
            "kids pop, upbeat, fun",
            "disney-style, magical, orchestral",
            "lullaby, soft, calming",
            "animated musical, cheerful, energetic",
            "children's folk, acoustic, simple",
            "kids rock, energetic, catchy",
            "preschool song, repetitive, easy to sing",
            "cartoon theme, bouncy, memorable"
        )
        style_combo.grid(row=0, column=3)
        
        # Row 2: Model and Checkboxes
        row2_frame = ttk.Frame(config_frame)
        row2_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(row2_frame, text="Modelo:").grid(row=0, column=0, sticky='w', padx=(0, 5))
        self.model_var = tk.StringVar(value="V4_5")
        model_combo = ttk.Combobox(row2_frame, textvariable=self.model_var,
                                  values=["V3_5", "V4", "V4_5"], state="readonly", width=10)
        model_combo.grid(row=0, column=1, padx=(0, 20))

        self.custom_mode_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(row2_frame, text="Modo personalizado",
                       variable=self.custom_mode_var).grid(row=0, column=2, padx=(0, 10))
        
        self.instrumental_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(row2_frame, text="Instrumental", 
                       variable=self.instrumental_var).grid(row=0, column=3)
        
        # Row 3: Generate Image checkbox
        row3_frame = ttk.Frame(config_frame)
        row3_frame.pack(fill='x', padx=10, pady=5)
        
        self.generate_image_var = tk.BooleanVar(value=self.replicate_available)
        image_checkbox = ttk.Checkbutton(row3_frame, text="Generar imagen de portada (16:9)", 
                                       variable=self.generate_image_var)
        image_checkbox.grid(row=0, column=0, sticky='w')
        
        # Deshabilitar si no hay cliente de imagen
        if not self.replicate_available:
            image_checkbox.config(state='disabled')
            ttk.Label(row3_frame, text="(Requiere REPLICATE_API_TOKEN)", 
                     foreground="red").grid(row=0, column=1, padx=(10, 0), sticky='w')
        else:
            ttk.Label(row3_frame, text="✓ Replicate disponible", 
                     foreground="green").grid(row=0, column=1, padx=(10, 0), sticky='w')
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill='x', pady=(0, 10))
        
        self.generate_button = ttk.Button(buttons_frame, text="Generar Canción", 
                                        command=self.start_generation)
        self.generate_button.pack(side='left', padx=(0, 10))
        
        ttk.Button(buttons_frame, text="Limpiar", command=self.clear_form).pack(side='left')
        
        # Progress frame
        progress_frame = ttk.LabelFrame(main_frame, text="Progreso")
        progress_frame.pack(fill='x')
        
        self.progress_var = tk.StringVar(value="Listo para generar")
        ttk.Label(progress_frame, textvariable=self.progress_var).pack(padx=10, pady=5)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', padx=10, pady=(0, 10))
    
    def create_new_history_tab(self, parent):
        """Create the new modern history tab"""
        self.history_tab = HistoryTab(
            parent, 
            self.list_sessions_use_case,
            generate_image_callback=self.generate_image_for_session_callback,
            generate_video_callback=self.generate_video_for_session_callback,
            loop_video_callback=self.loop_video_for_session_callback
        )
        parent.add(self.history_tab, text="🎵 Historial")
    
    def generate_image_for_session_callback(self, session):
        """Callback to handle image generation from history tab"""
        try:
            if not self.replicate_available:
                messagebox.showerror("Error", "Replicate no está disponible. Configura REPLICATE_API_TOKEN")
                return False
            
            # Verify session doesn't have image already
            if session.image_response and session.image_response.has_images:
                messagebox.showinfo("Información", "Esta sesión ya tiene una imagen generada")
                return False
            
            # Confirm with user
            result = messagebox.askyesno(
                "Confirmar", 
                f"¿Generar imagen para la canción '{session.request.title}'?"
            )
            
            if not result:
                return False
            
            # Run generation in background thread
            thread = threading.Thread(
                target=self.run_image_generation_for_session, 
                args=(session,),
                daemon=True
            )
            thread.start()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar generación de imagen: {str(e)}")
            return False
    
    def generate_video_for_session_callback(self, session):
        """Callback to handle video generation from history tab"""
        try:
            if not self.replicate_available:
                messagebox.showerror("Error", "Replicate no está disponible. Configura REPLICATE_API_TOKEN")
                return False
            
            # Verify session has an image but no video
            if not (session.image_response and session.image_response.has_images):
                messagebox.showerror("Error", "Esta sesión necesita una imagen primero para generar el video")
                return False
            
            if session.video_response and session.video_response.has_video:
                messagebox.showinfo("Información", "Esta sesión ya tiene un video animado generado")
                return False
            
            # Confirm with user
            result = messagebox.askyesno(
                "Confirmar", 
                f"¿Animar la portada de la canción '{session.request.title}'?\n\nEsto creará un video en bucle que dura lo mismo que la canción."
            )
            
            if not result:
                return False
            
            # Run generation in background thread
            thread = threading.Thread(
                target=self.run_video_generation_for_session, 
                args=(session,),
                daemon=True
            )
            thread.start()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar generación de video: {str(e)}")
            return False
    
    def loop_video_for_session_callback(self, session):
        """Callback to handle video loop creation from history tab"""
        try:
            if not self.replicate_available:
                messagebox.showerror("Error", "Replicate no está disponible. Configura REPLICATE_API_TOKEN")
                return False
            
            # Verify session has video response but needs loop
            if not (session.video_response and session.video_response.has_video):
                messagebox.showerror("Error", "Esta sesión necesita tener un video generado primero")
                return False
            
            # Confirm with user
            result = messagebox.askyesno(
                "Confirmar", 
                f"¿Recrear el bucle de video para '{session.request.title}'?\n\nEsto creará un nuevo bucle con la duración de la canción."
            )
            
            if not result:
                return False
            
            # Run loop creation in background thread
            thread = threading.Thread(
                target=self.run_loop_video_for_session, 
                args=(session,),
                daemon=True
            )
            thread.start()
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al iniciar creación de bucle: {str(e)}")
            return False
        
    # Old history tab implementation - kept for reference
    # def create_history_tab_old(self, parent):
    #     history_frame = ttk.Frame(parent)
    #     parent.add(history_frame, text="Historial")
    #     
    #     # ... old implementation ...
    
    def generate_lyrics_with_ai(self):
        """Generate lyrics using OpenAI assistant"""
        if not self.openai_available:
            messagebox.showerror("Error", "OpenAI no está configurado. Por favor, configura OPENAI_API_KEY en el archivo .env")
            return

        description = self.description_var.get().strip()

        if not description:
            messagebox.showerror("Error", "Por favor, ingresa una descripción para generar la letra")
            return

        try:
            self.generate_lyrics_button.config(state='disabled')
            self.progress_var.set("Generando letra con IA...")
            self.progress_bar.start()

            # Run generation in background thread
            thread = threading.Thread(
                target=self.run_lyrics_generation,
                args=(description,),
                daemon=True
            )
            thread.start()

        except Exception as e:
            messagebox.showerror("Error", f"Error al generar letra: {str(e)}")
            self.generate_lyrics_button.config(state='normal')

    def run_lyrics_generation(self, description: str):
        """Run lyrics generation in background thread"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            lyrics = loop.run_until_complete(
                self.openai_client.generate_lyrics(
                    description,
                    self.update_progress,
                    session_id="lyrics_generation"
                )
            )

            self.root.after(0, self.lyrics_generation_completed, lyrics)

        except Exception as e:
            self.root.after(0, self.lyrics_generation_failed, str(e))
        finally:
            loop.close()

    def lyrics_generation_completed(self, lyrics: str):
        """Handle successful lyrics generation"""
        self.progress_bar.stop()
        self.generate_lyrics_button.config(state='normal')
        self.progress_var.set("Letra generada exitosamente")

        # Clear and update lyrics text
        self.lyrics_text.delete(1.0, tk.END)
        self.lyrics_text.insert(1.0, lyrics)

    def lyrics_generation_failed(self, error_message: str):
        """Handle failed lyrics generation"""
        self.progress_bar.stop()
        self.generate_lyrics_button.config(state='normal')
        self.progress_var.set("Error al generar letra")

        messagebox.showerror("Error", f"Error al generar letra:\n{error_message}")

    def clear_form(self):
        self.description_var.set("")
        self.lyrics_text.delete(1.0, tk.END)
        self.title_var.set("")
        self.style_var.set("")
        self.model_var.set("V4_5")
        self.custom_mode_var.set(True)
        self.instrumental_var.set(False)
        self.generate_image_var.set(self.replicate_available)
    
    def start_generation(self):
        # Verificar si hay configuración válida
        if not self.has_valid_config:
            messagebox.showerror(
                "Configuración requerida",
                "Debes configurar las API keys antes de generar música.\n\nVe a Archivo → Configuración para agregar tus claves."
            )
            return

        lyrics = self.lyrics_text.get(1.0, tk.END).strip()
        title = self.title_var.get().strip()
        style = self.style_var.get().strip()

        if not lyrics:
            messagebox.showerror("Error", "Por favor, ingresa la letra de la canción")
            return

        if not title:
            messagebox.showerror("Error", "Por favor, ingresa un título")
            return

        if not style:
            messagebox.showerror("Error", "Por favor, ingresa un estilo musical")
            return
        
        try:
            request = SongRequest(
                prompt=lyrics,
                title=title,
                style=style,
                model=ModelVersion(self.model_var.get()),
                custom_mode=self.custom_mode_var.get(),
                instrumental=self.instrumental_var.get(),
                callback_url=self.settings.callback_url
            )
            
            self.generate_button.config(state='disabled')
            self.progress_bar.start()
            
            thread = threading.Thread(target=self.run_generation, args=(request,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear la petición: {str(e)}")
    
    def run_generation(self, request: SongRequest):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            session = loop.run_until_complete(
                self.generate_use_case.execute(
                    request, 
                    self.update_progress, 
                    self.generate_image_var.get()
                )
            )
            
            self.root.after(0, self.generation_completed, session)
            
        except Exception as e:
            self.root.after(0, self.generation_failed, str(e))
        finally:
            loop.close()
    
    def update_progress(self, message: str):
        self.root.after(0, lambda: self.progress_var.set(message))
    
    def generation_completed(self, session):
        self.progress_bar.stop()
        self.generate_button.config(state='normal')
        self.progress_var.set("¡Generación completada!")
        
        messagebox.showinfo("Éxito", 
                          f"Canción generada exitosamente.\nGuardada en: {session.output_directory}")
        
        self.refresh_history()
    
    def generation_failed(self, error_message: str):
        self.progress_bar.stop()
        self.generate_button.config(state='normal')
        self.progress_var.set("Error en la generación")
        
        messagebox.showerror("Error", f"Error al generar la canción:\n{error_message}")
    
    # Obsolete method - replaced by new history tab
    # def refresh_history(self):
    #     ... old implementation ...
    
    # Obsolete method - replaced by new history tab
    # def on_session_select(self, event):
    #     ... old implementation ...
    
    # Obsolete method - replaced by new history tab
    # def generate_image_for_selected(self):
    #     ... old implementation ...
    
    def run_image_generation_for_session(self, session):
        """
        Ejecuta la generación de imagen para una sesión específica en un hilo separado
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Crear caso de uso de imagen
            from ...application.use_cases.generate_image import GenerateImageUseCase
            generate_image_use_case = GenerateImageUseCase(self.image_client, self.file_storage)
            
            # Crear prompt basado en la información de la canción
            image_prompt = f"{session.request.title}: {session.request.prompt}"
            
            # Generar imagen
            updated_session = loop.run_until_complete(
                generate_image_use_case.execute(
                    session, 
                    image_prompt, 
                    self.update_image_generation_progress
                )
            )
            
            self.root.after(0, self.image_generation_completed, updated_session)
            
        except Exception as e:
            self.root.after(0, self.image_generation_failed, str(e))
        finally:
            loop.close()
    
    def update_image_generation_progress(self, message: str):
        """
        Actualiza el progreso de generación de imagen
        """
        # Actualizar en el hilo principal
        def update_ui():
            # Puedes mostrar el progreso en la barra de estado o en un diálogo
            print(f"Progreso imagen: {message}")
        
        self.root.after(0, update_ui)
    
    def image_generation_completed(self, session):
        """
        Callback cuando la generación de imagen se completa exitosamente
        """
        # Habilitar botón nuevamente (aunque quedará deshabilitado por tener imagen)
        if hasattr(self, 'generate_image_button'):
            self.generate_image_button.config(state='disabled')

        messagebox.showinfo(
            "Éxito",
            f"Imagen generada exitosamente para '{session.request.title}'"
        )

        # Reset processing state in the card
        self.reset_card_processing_state(session)

        # Refrescar historial para mostrar los nuevos datos
        self.refresh_history()
        
        # Actualizar detalles si esta sesión sigue seleccionada
        selection = self.sessions_tree.selection()
        if selection:
            item = self.sessions_tree.item(selection[0])
            if item['values'][0] == session.session_id:
                # Simular selección para actualizar detalles
                self.on_session_select(None)
    
    def image_generation_failed(self, error_message: str):
        """
        Callback cuando la generación de imagen falla
        """
        # Habilitar botón nuevamente
        if hasattr(self, 'generate_image_button'):
            self.generate_image_button.config(state='normal')

        # Reset processing state in all cards
        self.reset_all_cards_processing_state()
        messagebox.showerror("Error", f"Error al generar imagen:\n{error_message}")
    
    def run_video_generation_for_session(self, session):
        """
        Ejecuta la generación de video para una sesión específica en un hilo separado
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Crear caso de uso de video
            from ...application.use_cases.generate_video import GenerateVideoUseCase
            generate_video_use_case = GenerateVideoUseCase(self.video_client, self.file_storage)
            
            # Generar video animado
            updated_session = loop.run_until_complete(
                generate_video_use_case.execute(
                    session, 
                    self.update_video_generation_progress
                )
            )
            
            self.root.after(0, self.video_generation_completed, updated_session)
            
        except Exception as e:
            self.root.after(0, self.video_generation_failed, str(e))
        finally:
            loop.close()
    
    def update_video_generation_progress(self, message: str):
        """
        Actualiza el progreso de generación de video
        """
        # Actualizar en el hilo principal
        def update_ui():
            # Puedes mostrar el progreso en la barra de estado o en un diálogo
            print(f"Progreso video: {message}")
        
        self.root.after(0, update_ui)
    
    def video_generation_completed(self, session):
        """
        Callback cuando la generación de video se completa exitosamente
        """
        messagebox.showinfo(
            "Éxito",
            f"Video animado generado exitosamente para '{session.request.title}'"
        )

        # Reset processing state in the card
        self.reset_card_processing_state(session)

        # Refrescar historial para mostrar los nuevos datos
        self.refresh_history()
    
    def video_generation_failed(self, error_message: str):
        """
        Callback cuando la generación de video falla
        """
        # Reset processing state in all cards
        self.reset_all_cards_processing_state()
        messagebox.showerror("Error", f"Error al generar video:\n{error_message}")
    
    def run_loop_video_for_session(self, session):
        """
        Ejecuta la creación de bucle de video para una sesión específica en un hilo separado
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Crear caso de uso de bucle de video
            from ...application.use_cases.loop_video import LoopVideoUseCase
            loop_video_use_case = LoopVideoUseCase(self.video_client, self.file_storage)
            
            # Crear bucle de video
            updated_session = loop.run_until_complete(
                loop_video_use_case.execute(
                    session, 
                    self.update_loop_video_progress
                )
            )
            
            self.root.after(0, self.loop_video_completed, updated_session)
            
        except Exception as e:
            self.root.after(0, self.loop_video_failed, str(e))
        finally:
            loop.close()
    
    def update_loop_video_progress(self, message: str):
        """
        Actualiza el progreso de creación de bucle de video
        """
        # Actualizar en el hilo principal
        def update_ui():
            print(f"Progreso bucle: {message}")
        
        self.root.after(0, update_ui)
    
    def loop_video_completed(self, session):
        """
        Callback cuando la creación de bucle se completa exitosamente
        """
        messagebox.showinfo(
            "Éxito",
            f"Bucle de video creado exitosamente para '{session.request.title}'"
        )

        # Reset processing state in the card
        self.reset_card_processing_state(session)

        # Refrescar historial para mostrar los nuevos datos
        self.refresh_history()
    
    def loop_video_failed(self, error_message: str):
        """
        Callback cuando la creación de bucle falla
        """
        # Reset processing state in all cards
        self.reset_all_cards_processing_state()
        messagebox.showerror("Error", f"Error al crear bucle de video:\n{error_message}")
    
    def reset_card_processing_state(self, session):
        """Reset processing state for a specific session card"""
        if hasattr(self, 'history_tab'):
            for card in self.history_tab.session_cards:
                if card.session.session_id == session.session_id:
                    card.reset_processing_state()
                    break

    def reset_all_cards_processing_state(self):
        """Reset processing state for all cards"""
        if hasattr(self, 'history_tab'):
            for card in self.history_tab.session_cards:
                card.reset_processing_state()

    def refresh_history(self):
        """Refresh history tab"""
        if hasattr(self, 'history_tab'):
            self.history_tab.refresh_history()
    
    def run(self):
        self.root.mainloop()