# Runtime hook for onnxruntime DLL loading in PyInstaller frozen apps
import os
import sys

def _add_dll_directory():
    """Add onnxruntime capi directory to DLL search path."""
    if sys.platform != 'win32':
        return

    # Find the base path for frozen app
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        return

    # Add onnxruntime capi directory to DLL search path
    ort_capi_dir = os.path.join(base_path, 'onnxruntime', 'capi')
    if os.path.exists(ort_capi_dir):
        # On Python 3.8+, use os.add_dll_directory
        if hasattr(os, 'add_dll_directory'):
            os.add_dll_directory(ort_capi_dir)
        # Also prepend to PATH as fallback
        os.environ['PATH'] = ort_capi_dir + os.pathsep + os.environ.get('PATH', '')

_add_dll_directory()
