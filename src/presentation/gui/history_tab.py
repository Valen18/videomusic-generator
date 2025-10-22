import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable, Optional
import threading
import asyncio

from .components.session_card import SessionCard
from .components.search_bar import SearchBar
from ...domain.entities.generation_session import GenerationSession


class HistoryTab(ttk.Frame):
    def __init__(self, parent, list_sessions_use_case, generate_image_callback=None, generate_video_callback=None, loop_video_callback=None):
        super().__init__(parent)
        self.list_sessions_use_case = list_sessions_use_case
        self.generate_image_callback = generate_image_callback
        self.generate_video_callback = generate_video_callback
        self.loop_video_callback = loop_video_callback
        self.all_sessions = []
        self.filtered_sessions = []
        self.session_cards = []
        
        self.setup_styles()
        self.setup_ui()
        self.refresh_history()
    
    def setup_styles(self):
        """Configure custom styles for the history tab"""
        style = ttk.Style()
        
        # Card style
        style.configure(
            'Card.TFrame',
            background='white',
            relief='solid',
            borderwidth=1
        )
        
        # Header style
        style.configure(
            'Header.TLabel',
            font=('Segoe UI', 14, 'bold'),
            foreground='#2c3e50'
        )
    
    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self)
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Header
        header_frame = ttk.Frame(main_container)
        header_frame.pack(fill='x', pady=(0, 20))
        
        header_label = ttk.Label(
            header_frame,
            text="🎵 Historial de Canciones",
            style='Header.TLabel'
        )
        header_label.pack(side='left')
        
        # Stats label
        self.stats_label = ttk.Label(
            header_frame,
            text="",
            font=('Segoe UI', 10),
            foreground='#7f8c8d'
        )
        self.stats_label.pack(side='right')
        
        # Search and filter bar
        self.search_bar = SearchBar(
            main_container,
            on_search_callback=self.on_search,
            on_filter_callback=self.on_filter
        )
        self.search_bar.pack(fill='x', pady=(0, 20))
        
        # Action buttons
        action_frame = ttk.Frame(main_container)
        action_frame.pack(fill='x', pady=(0, 10))
        
        refresh_btn = ttk.Button(
            action_frame,
            text="🔄 Actualizar",
            command=self.refresh_history,
            style='Accent.TButton'
        )
        refresh_btn.pack(side='left', padx=(0, 10))
        
        # Sessions container with scrollbar
        sessions_container = ttk.Frame(main_container)
        sessions_container.pack(fill='both', expand=True)
        
        # Create canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(sessions_container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(sessions_container, orient='vertical', command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mouse wheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.bind_all("<MouseWheel>", self._on_mousewheel)
        
        # Empty state label (hidden by default)
        self.empty_label = ttk.Label(
            self.scrollable_frame,
            text="📭 No hay canciones generadas aún\n\n¡Ve a la pestaña 'Generar Canción' para crear tu primera canción!",
            font=('Segoe UI', 12),
            foreground='#7f8c8d',
            justify='center'
        )
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def refresh_history(self):
        """Refresh the sessions list"""
        try:
            self.all_sessions = self.list_sessions_use_case.execute()
            self.apply_filters()
            self.update_stats()
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el historial: {str(e)}")
    
    def apply_filters(self):
        """Apply current search and filter criteria"""
        search_text = self.search_bar.get_search_text().lower()
        filter_data = self.search_bar.get_filter_data()
        
        # Start with all sessions
        filtered = self.all_sessions.copy()
        
        # Apply text search
        if search_text:
            filtered = [
                session for session in filtered
                if (search_text in session.request.title.lower() or 
                    search_text in session.request.style.lower() or
                    search_text in session.request.prompt.lower())
            ]
        
        # Apply filter
        filter_type = filter_data['filter']
        if filter_type == "Con música":
            filtered = [s for s in filtered if s.response and s.response.is_completed]
        elif filter_type == "Con imagen":
            filtered = [s for s in filtered if s.image_response and s.image_response.has_images]
        elif filter_type == "Sin imagen":
            filtered = [s for s in filtered if not (s.image_response and s.image_response.has_images)]
        elif filter_type == "Con video":
            filtered = [s for s in filtered if s.video_response and s.video_response.has_video]
        elif filter_type == "Sin video":
            filtered = [s for s in filtered if not (s.video_response and s.video_response.has_video)]
        elif filter_type == "Completadas":
            filtered = [s for s in filtered if s.response and s.response.is_completed]
        elif filter_type == "En proceso":
            filtered = [s for s in filtered if not (s.response and s.response.is_completed)]
        
        # Apply sorting
        sort_type = filter_data['sort']
        if sort_type == "Más recientes":
            filtered.sort(key=lambda s: s.timestamp, reverse=True)
        elif sort_type == "Más antiguos":
            filtered.sort(key=lambda s: s.timestamp)
        elif sort_type == "Alfabético A-Z":
            filtered.sort(key=lambda s: s.request.title.lower())
        elif sort_type == "Alfabético Z-A":
            filtered.sort(key=lambda s: s.request.title.lower(), reverse=True)
        
        self.filtered_sessions = filtered
        self.display_sessions()
    
    def display_sessions(self):
        """Display the filtered sessions as cards"""
        # Clear existing cards
        for card in self.session_cards:
            card.destroy()
        self.session_cards.clear()
        
        # Hide empty label
        self.empty_label.pack_forget()
        
        if not self.filtered_sessions:
            # Show empty state
            if not self.all_sessions:
                self.empty_label.pack(pady=50)
            else:
                # No results from filter
                no_results = ttk.Label(
                    self.scrollable_frame,
                    text="🔍 No se encontraron canciones con los filtros aplicados",
                    font=('Segoe UI', 11),
                    foreground='#7f8c8d'
                )
                no_results.pack(pady=30)
                self.session_cards.append(no_results)
            return
        
        # Create cards for each session
        for i, session in enumerate(self.filtered_sessions):
            card = SessionCard(
                self.scrollable_frame,
                session,
                on_generate_image_callback=self.on_generate_image_for_session,
                on_generate_video_callback=self.on_generate_video_for_session,
                on_loop_video_callback=self.on_loop_video_for_session
            )
            card.pack(fill='x', pady=(0, 15))
            self.session_cards.append(card)
        
        # Update canvas scroll region
        self.scrollable_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def update_stats(self):
        """Update the statistics label"""
        total = len(self.all_sessions)
        with_music = len([s for s in self.all_sessions if s.response and s.response.is_completed])
        with_image = len([s for s in self.all_sessions if s.image_response and s.image_response.has_images])
        with_video = len([s for s in self.all_sessions if s.video_response and s.video_response.has_video])
        
        stats_text = f"{total} canciones • {with_music} con música • {with_image} con imagen • {with_video} con video"
        self.stats_label.configure(text=stats_text)
    
    def on_search(self, search_text: str):
        """Handle search text changes"""
        self.apply_filters()
    
    def on_filter(self, filter_data: dict):
        """Handle filter/sort changes"""
        self.apply_filters()
    
    def on_generate_image_for_session(self, session: GenerationSession):
        """Handle image generation request for a session"""
        if self.generate_image_callback:
            # Run in thread to avoid blocking UI
            thread = threading.Thread(
                target=self._run_image_generation, 
                args=(session,),
                daemon=True
            )
            thread.start()
    
    def on_generate_video_for_session(self, session: GenerationSession):
        """Handle video generation request for a session"""
        if self.generate_video_callback:
            # Run in thread to avoid blocking UI
            thread = threading.Thread(
                target=self._run_video_generation, 
                args=(session,),
                daemon=True
            )
            thread.start()
    
    def _run_image_generation(self, session: GenerationSession):
        """Run image generation in background thread"""
        try:
            # Call the callback which should handle the async generation
            result = self.generate_image_callback(session)
            
            # Refresh history after generation
            self.after(100, self.refresh_history)
            
        except Exception as e:
            # Show error message in main thread
            self.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error al generar imagen: {str(e)}"
            ))
    
    def on_loop_video_for_session(self, session: GenerationSession):
        """Handle video loop creation request for a session"""
        if self.loop_video_callback:
            # Run in thread to avoid blocking UI
            thread = threading.Thread(
                target=self._run_loop_video, 
                args=(session,),
                daemon=True
            )
            thread.start()
    
    def _run_video_generation(self, session: GenerationSession):
        """Run video generation in background thread"""
        try:
            # Call the callback which should handle the async generation
            result = self.generate_video_callback(session)
            
            # Refresh history after generation
            self.after(100, self.refresh_history)
            
        except Exception as e:
            # Show error message in main thread
            self.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error al generar video: {str(e)}"
            ))
    
    def _run_loop_video(self, session: GenerationSession):
        """Run video loop creation in background thread"""
        try:
            # Call the callback which should handle the async loop creation
            result = self.loop_video_callback(session)
            
            # Refresh history after generation
            self.after(100, self.refresh_history)
            
        except Exception as e:
            # Show error message in main thread
            self.after(0, lambda: messagebox.showerror(
                "Error", 
                f"Error al crear bucle de video: {str(e)}"
            ))
    
    def get_selected_session(self) -> Optional[GenerationSession]:
        """Get the currently selected session (for compatibility)"""
        # This method is kept for compatibility with existing code
        # In the new design, each card handles its own actions
        return None