# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller specification file for Tok-Transcript.

Build command:
    pyinstaller pyinstaller.spec --clean
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect faster-whisper and ctranslate2 data files
datas = [
    ('assets', 'assets'),
]
datas += collect_data_files('faster_whisper')
datas += collect_data_files('ctranslate2')
datas += collect_data_files('imageio_ffmpeg')

hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'faster_whisper',
    'ctranslate2',
    'imageio_ffmpeg',
    'yt_dlp',
    'av',
]
hiddenimports += collect_submodules('yt_dlp.extractor')

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'torchvision', 'torchaudio'],
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
    name='TokTranscript',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,  # Set to True if console logs are needed during testing
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icons/app_icon.ico' if Path('assets/icons/app_icon.ico').exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='TokTranscript',
)
