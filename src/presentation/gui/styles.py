"""
Configuración de estilos y temas para la interfaz gráfica
"""

import tkinter as tk
from tkinter import ttk


class ThemeManager:
    """Gestor de temas y estilos para la aplicación"""
    
    # Color palette
    COLORS = {
        'primary': '#3498db',
        'secondary': '#2c3e50', 
        'success': '#27ae60',
        'warning': '#f39c12',
        'danger': '#e74c3c',
        'info': '#17a2b8',
        'light': '#f8f9fa',
        'dark': '#343a40',
        'white': '#ffffff',
        'gray_100': '#f8f9fa',
        'gray_200': '#e9ecef',
        'gray_300': '#dee2e6',
        'gray_400': '#ced4da',
        'gray_500': '#adb5bd',
        'gray_600': '#6c757d',
        'gray_700': '#495057',
        'gray_800': '#343a40',
        'gray_900': '#212529'
    }
    
    @classmethod
    def setup_styles(cls):
        """Configura todos los estilos personalizados"""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')
        
        # Button styles
        cls._setup_button_styles(style)
        
        # Frame styles
        cls._setup_frame_styles(style)
        
        # Label styles
        cls._setup_label_styles(style)
        
        # Entry styles
        cls._setup_entry_styles(style)
        
        return style
    
    @classmethod
    def _setup_button_styles(cls, style):
        """Configura estilos de botones"""
        
        # Primary button
        style.configure(
            'Primary.TButton',
            background=cls.COLORS['primary'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(12, 8),
            relief='flat'
        )
        style.map(
            'Primary.TButton',
            background=[('active', '#2980b9'), ('pressed', '#2471a3')]
        )
        
        # Success button
        style.configure(
            'Success.TButton',
            background=cls.COLORS['success'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(12, 8),
            relief='flat'
        )
        style.map(
            'Success.TButton',
            background=[('active', '#229954'), ('pressed', '#1e8449')]
        )
        
        # Warning button
        style.configure(
            'Warning.TButton',
            background=cls.COLORS['warning'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(12, 8),
            relief='flat'
        )
        
        # Danger button
        style.configure(
            'Danger.TButton',
            background=cls.COLORS['danger'],
            foreground='white',
            font=('Segoe UI', 10, 'bold'),
            padding=(12, 8),
            relief='flat'
        )
        
        # Small button
        style.configure(
            'Small.TButton',
            font=('Segoe UI', 9),
            padding=(8, 4)
        )
        
        # Icon button
        style.configure(
            'Icon.TButton',
            font=('Segoe UI', 12),
            padding=(8, 8),
            relief='flat'
        )
    
    @classmethod
    def _setup_frame_styles(cls, style):
        """Configura estilos de frames"""
        
        # Card frame
        style.configure(
            'Card.TFrame',
            background=cls.COLORS['white'],
            relief='solid',
            borderwidth=1,
            padding=15
        )
        
        # Header frame
        style.configure(
            'Header.TFrame',
            background=cls.COLORS['gray_100'],
            padding=20
        )
        
        # Sidebar frame
        style.configure(
            'Sidebar.TFrame',
            background=cls.COLORS['gray_200'],
            padding=10
        )
    
    @classmethod
    def _setup_label_styles(cls, style):
        """Configura estilos de labels"""
        
        # Title label
        style.configure(
            'Title.TLabel',
            font=('Segoe UI', 16, 'bold'),
            foreground=cls.COLORS['secondary'],
            background=cls.COLORS['white']
        )
        
        # Subtitle label
        style.configure(
            'Subtitle.TLabel',
            font=('Segoe UI', 12, 'bold'),
            foreground=cls.COLORS['gray_700'],
            background=cls.COLORS['white']
        )
        
        # Body label
        style.configure(
            'Body.TLabel',
            font=('Segoe UI', 10),
            foreground=cls.COLORS['gray_800'],
            background=cls.COLORS['white']
        )
        
        # Caption label
        style.configure(
            'Caption.TLabel',
            font=('Segoe UI', 9),
            foreground=cls.COLORS['gray_600'],
            background=cls.COLORS['white']
        )
        
        # Badge labels
        for badge_type, color in [
            ('Success', cls.COLORS['success']),
            ('Warning', cls.COLORS['warning']),
            ('Danger', cls.COLORS['danger']),
            ('Info', cls.COLORS['info'])
        ]:
            style.configure(
                f'{badge_type}Badge.TLabel',
                background=color,
                foreground='white',
                font=('Segoe UI', 8, 'bold'),
                padding=(8, 4),
                relief='solid',
                borderwidth=0
            )
    
    @classmethod
    def _setup_entry_styles(cls, style):
        """Configura estilos de campos de entrada"""
        
        style.configure(
            'Modern.TEntry',
            fieldbackground=cls.COLORS['white'],
            borderwidth=1,
            relief='solid',
            padding=8
        )
        
        style.configure(
            'Search.TEntry',
            fieldbackground=cls.COLORS['gray_100'],
            borderwidth=1,
            relief='solid',
            padding=10,
            font=('Segoe UI', 10)
        )


def create_badge_label(parent, text, badge_type='info', **kwargs):
    """
    Crea un label con estilo de badge
    
    Args:
        parent: Widget padre
        text: Texto del badge
        badge_type: Tipo de badge ('success', 'warning', 'danger', 'info')
        **kwargs: Argumentos adicionales para el Label
    """
    style_name = f"{badge_type.title()}Badge.TLabel"
    
    label = ttk.Label(parent, text=text, style=style_name, **kwargs)
    return label


def create_status_badge(parent, status, **kwargs):
    """
    Crea un badge de estado apropiado
    
    Args:
        parent: Widget padre
        status: Estado ('completed', 'processing', 'error', etc.)
        **kwargs: Argumentos adicionales
    """
    status_map = {
        'completed': ('✓ Completado', 'success'),
        'processing': ('⏳ Procesando', 'warning'), 
        'error': ('✗ Error', 'danger'),
        'with_image': ('🖼 Con imagen', 'success'),
        'without_image': ('📭 Sin imagen', 'info')
    }
    
    text, badge_type = status_map.get(status, (status, 'info'))
    return create_badge_label(parent, text, badge_type, **kwargs)


# Note: Styles will be configured when MainWindow is created
# to avoid creating extra Tk windows