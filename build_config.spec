# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

# Use PyInstaller's collect functions for robust package inclusion
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_dynamic_libs

block_cipher = None

# Collect ALL onnxruntime files (this is the reliable way)
ort_datas = []
ort_binaries = []
ort_hiddenimports = []
try:
    ort_datas, ort_binaries, ort_hiddenimports = collect_all('onnxruntime')
    print(f"Collected {len(ort_binaries)} onnxruntime binaries")
    print(f"Collected {len(ort_datas)} onnxruntime data files")
except Exception as e:
    print(f"WARNING: Failed to collect onnxruntime: {e}")

# CRITICAL: Also copy onnxruntime DLLs to root _internal folder for DLL loading
# This fixes "DLL load failed" errors on Windows
ort_root_binaries = []
try:
    import onnxruntime
    ort_capi = Path(onnxruntime.__file__).parent / "capi"
    for dll in ort_capi.glob("*.dll"):
        # Copy to root (empty destination = _internal root)
        ort_root_binaries.append((str(dll), '.'))
        print(f"Adding {dll.name} to root _internal")
    for pyd in ort_capi.glob("*.pyd"):
        ort_root_binaries.append((str(pyd), '.'))
        print(f"Adding {pyd.name} to root _internal")
except Exception as e:
    print(f"WARNING: Failed to add onnxruntime root binaries: {e}")

# Collect sounddevice with PortAudio
sd_datas = []
sd_binaries = []
sd_hiddenimports = []
try:
    sd_datas, sd_binaries, sd_hiddenimports = collect_all('sounddevice')
    print(f"Collected {len(sd_binaries)} sounddevice binaries")
except Exception as e:
    print(f"WARNING: Failed to collect sounddevice: {e}")

# Collect librosa and dependencies
librosa_datas = []
librosa_binaries = []
librosa_hiddenimports = []
try:
    librosa_datas, librosa_binaries, librosa_hiddenimports = collect_all('librosa')
except Exception as e:
    print(f"WARNING: Failed to collect librosa: {e}")

# Collect scipy
scipy_datas = []
scipy_binaries = []
scipy_hiddenimports = []
try:
    scipy_datas, scipy_binaries, scipy_hiddenimports = collect_all('scipy')
except Exception as e:
    print(f"WARNING: Failed to collect scipy: {e}")

# Collect certifi certificates (needed for SSL in httpx/openai)
certifi_datas = []
try:
    certifi_datas = collect_data_files('certifi')
    print(f"Collected {len(certifi_datas)} certifi data files")
except Exception as e:
    print(f"WARNING: Failed to collect certifi: {e}")

# Combine all collected items
all_binaries = ort_binaries + ort_root_binaries + sd_binaries + librosa_binaries + scipy_binaries
all_datas = ort_datas + sd_datas + librosa_datas + scipy_datas + certifi_datas
all_hiddenimports = ort_hiddenimports + sd_hiddenimports + librosa_hiddenimports + scipy_hiddenimports

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=all_binaries,
    datas=[
        ('src/resources', 'resources'),
        ('src/ui/web_settings/index.html', 'ui/web_settings'),
        ('src/ui/web_settings/app.js', 'ui/web_settings'),
        # NO incluir config.json - contiene API keys del desarrollador
        # El programa crea uno vacío automáticamente si no existe
    ] + all_datas,
    hiddenimports=[
        # ONNX and ML - explicit imports as backup
        'onnxruntime',
        'onnxruntime.capi',
        'onnxruntime.capi._pybind_state',
        'onnxruntime.capi.onnxruntime_pybind11_state',
        'librosa',
        'librosa.core',
        'librosa.util',
        'numpy',
        'scipy',
        'scipy.signal',
        'scipy.fft',
        'scipy.io',
        'scipy.io.wavfile',
        'numba',
        'llvmlite',
        'soxr',
        # Audio
        'sounddevice',
        '_sounddevice_data',
        # UI and system
        'pynput',
        'pynput.keyboard',
        'pynput._util',
        'pynput._util.win32',
        'pystray',
        'PIL',
        'PIL.Image',
        # Windows APIs
        'win32api',
        'win32con',
        'win32gui',
        'win32event',
        'winerror',
        'pywintypes',
        'pythoncom',
        # Web settings
        'webview',
        # HTTP and SSL
        'httpx',
        'openai',
        'certifi',
    ] + all_hiddenimports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=['hooks/rthook_onnxruntime.py'],
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
    exclude_binaries=True,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhisperCheap',
)
