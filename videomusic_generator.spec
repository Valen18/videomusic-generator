# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
import sys
import os

# Get the directory containing this spec file
spec_dir = os.path.dirname(os.path.abspath(SPEC))

block_cipher = None

# Collect data files for matplotlib
matplotlib_data = collect_data_files('matplotlib')

# Collect data files for tkinter and other GUI libraries
tkinter_data = collect_data_files('tkinter')

# Additional data files to include
added_files = [
    ('src', 'src'),  # Include source code
    ('requirements.txt', '.'),
    ('README.md', '.'),
    ('CONFIGURACION_APIS.md', '.'),
    ('.env.example', '.'),
]

# Hidden imports - libraries that PyInstaller might miss
hidden_imports = [
    'tkinter',
    'tkinter.ttk',
    'tkinter.scrolledtext',
    'tkinter.messagebox',
    'tkinter.filedialog',
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_tkagg',
    'matplotlib.dates',
    'matplotlib.figure',
    'PIL',
    'PIL.Image',
    'PIL.ImageTk',
    'pygame',
    'requests',
    'aiohttp',
    'asyncio',
    'sqlite3',
    'json',
    'dataclasses',
    'pathlib',
    'datetime',
    'threading',
    'concurrent.futures',
    'openai',
    'dotenv',
    'src.presentation.gui.main_window',
    'src.presentation.gui.settings_window',
    'src.presentation.gui.history_tab',
    'src.presentation.gui.styles',
    'src.infrastructure.config.settings',
    'src.infrastructure.adapters.usage_tracker',
    'src.infrastructure.adapters.suno_api_client',
    'src.infrastructure.adapters.replicate_image_client',
    'src.infrastructure.adapters.replicate_video_client',
    'src.infrastructure.adapters.openai_lyrics_client',
    'src.infrastructure.adapters.local_file_storage',
    'src.domain.entities.song_request',
    'src.domain.entities.song_response',
    'src.domain.entities.image_request',
    'src.domain.entities.image_response',
    'src.domain.entities.video_request',
    'src.domain.entities.video_response',
    'src.domain.entities.generation_session',
    'src.application.use_cases.generate_song',
    'src.application.use_cases.generate_image',
    'src.application.use_cases.generate_video',
    'src.application.use_cases.list_sessions',
]

a = Analysis(
    ['main.py'],
    pathex=[spec_dir],
    binaries=[],
    datas=added_files + matplotlib_data + tkinter_data,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'pytest',
        'unittest',
        '_pytest',
        'PyQt5',
        'PySide2',
        'PyQt6',
        'PySide6',
        'qt',
        'QtCore',
        'QtGui',
        'QtWidgets',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VideoMusic Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to False to hide console window
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # You can add an icon file here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VideoMusic Generator',
)