# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for Pizzeria Management System
This file configures how to build the Windows executable.
"""

import sys
from pathlib import Path

# Get the project root directory
project_root = Path(SPECPATH)

# Data files to include
# Note: settings.json is optional (will be created automatically)
datas = []
required_files = ['menu.json', 'extras.json']
optional_files = ['straatnamen.json', 'straatnamen.csv']

for file in required_files:
    file_path = project_root / file
    if file_path.exists():
        datas.append((str(file_path), '.'))
    else:
        print(f"WARNING: Required file {file} not found!")

for file in optional_files:
    file_path = project_root / file
    if file_path.exists():
        datas.append((str(file_path), '.'))

# Icon file - must be in root directory
icon_file = project_root / 'logo.ico'
if not icon_file.exists():
    print(f"WARNING: Icon file logo.ico not found at {icon_file}")

# Hidden imports (modules that PyInstaller might not detect automatically)
hiddenimports = [
    'PIL._imaging',
    'PIL._tkinter_finder',
    'qrcode',
    'qrcode.image.pil',
    'win32print',
    'win32api',
    'win32con',
    'win32clipboard',  # For clipboard monitoring
    'tkinter',
    'tkinter.ttk',
    'tkinter.messagebox',
    'tkinter.simpledialog',
    'tkinter.scrolledtext',
    'phonenumbers',  # Phone number validation for EU countries
    'phonenumbers.data',  # Phone number metadata
]

# Analysis phase
a = Analysis(
    ['main.py'],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'pytest',
        'pytest-cov',
        'pytest-mock',
    ],
    noarchive=False,
    optimize=0,
)

# Create PYZ archive
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

# Create executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PizzeriaBestelformulier',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to False for windowed application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(icon_file) if icon_file.exists() else None,
)


