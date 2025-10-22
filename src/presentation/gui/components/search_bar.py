import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class SearchBar(ttk.Frame):
    def __init__(self, parent, on_search_callback: Callable[[str], None] = None, 
                 on_filter_callback: Callable[[str], None] = None):
        super().__init__(parent)
        self.on_search_callback = on_search_callback
        self.on_filter_callback = on_filter_callback
        self.setup_ui()
    
    def setup_ui(self):
        # Search frame
        search_frame = ttk.Frame(self)
        search_frame.pack(fill='x', pady=(0, 10))
        
        # Search label and entry
        ttk.Label(search_frame, text="🔍 Buscar:", font=('Segoe UI', 10)).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self._on_search_change)
        
        search_entry = ttk.Entry(
            search_frame, 
            textvariable=self.search_var,
            font=('Segoe UI', 10),
            width=30
        )
        search_entry.pack(side='left', padx=(0, 20))
        
        # Filter dropdown
        ttk.Label(search_frame, text="📊 Filtrar:", font=('Segoe UI', 10)).pack(side='left', padx=(0, 10))
        
        self.filter_var = tk.StringVar(value="Todas")
        filter_combo = ttk.Combobox(
            search_frame,
            textvariable=self.filter_var,
            values=["Todas", "Con música", "Con imagen", "Sin imagen", "Con video", "Sin video", "Completadas", "En proceso"],
            state="readonly",
            width=15,
            font=('Segoe UI', 10)
        )
        filter_combo.pack(side='left', padx=(0, 20))
        filter_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Sort dropdown
        ttk.Label(search_frame, text="📅 Ordenar:", font=('Segoe UI', 10)).pack(side='left', padx=(0, 10))
        
        self.sort_var = tk.StringVar(value="Más recientes")
        sort_combo = ttk.Combobox(
            search_frame,
            textvariable=self.sort_var,
            values=["Más recientes", "Más antiguos", "Alfabético A-Z", "Alfabético Z-A"],
            state="readonly",
            width=15,
            font=('Segoe UI', 10)
        )
        sort_combo.pack(side='left')
        sort_combo.bind('<<ComboboxSelected>>', self._on_filter_change)
        
        # Clear button
        clear_btn = ttk.Button(
            search_frame,
            text="✖ Limpiar",
            command=self.clear_search,
            width=10
        )
        clear_btn.pack(side='right', padx=(10, 0))
    
    def _on_search_change(self, *args):
        """Handle search text changes"""
        if self.on_search_callback:
            search_text = self.search_var.get().strip()
            self.on_search_callback(search_text)
    
    def _on_filter_change(self, event=None):
        """Handle filter/sort changes"""
        if self.on_filter_callback:
            filter_data = {
                'filter': self.filter_var.get(),
                'sort': self.sort_var.get()
            }
            self.on_filter_callback(filter_data)
    
    def clear_search(self):
        """Clear all search and filters"""
        self.search_var.set("")
        self.filter_var.set("Todas")
        self.sort_var.set("Más recientes")
        self._on_filter_change()
    
    def get_search_text(self) -> str:
        """Get current search text"""
        return self.search_var.get().strip()
    
    def get_filter_data(self) -> dict:
        """Get current filter and sort data"""
        return {
            'filter': self.filter_var.get(),
            'sort': self.sort_var.get()
        }