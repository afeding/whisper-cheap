# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/resources', 'resources'),
        # NO incluir config.json - contiene API keys del desarrollador
        # El programa crea uno vacío automáticamente si no existe
    ],
    hiddenimports=[
        # ONNX and ML
        'onnxruntime',
        'librosa',
        'numpy',
        # Audio
        'sounddevice',
        # UI and system
        'keyboard',
        'pystray',
        'PIL',
        'PIL.Image',
        # Windows APIs
        'win32api',
        'win32con',
        'win32gui',
        'win32event',
        'winerror',
        # Web settings
        'webview',
        # HTTP
        'httpx',
        'openai',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WhisperCheap',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='src/resources/icons/app.ico' if __import__('os').path.exists('src/resources/icons/app.ico') else None,
)
