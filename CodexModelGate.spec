# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path
import tkinter as tk

# Do not silently publish a GUI executable when PyInstaller cannot collect Tk.
try:
    window = tk.Tk()
    window.withdraw()
    window.update_idletasks()
    window.destroy()
except tk.TclError as exc:
    raise RuntimeError('Tcl/Tk indisponível no ambiente de build; valide a interface antes de empacotar.') from exc

from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.win32.versioninfo import FixedFileInfo, StringFileInfo, StringTable, StringStruct, VarFileInfo, VarStruct, VSVersionInfo
from gate_models import APP_VERSION

version_numbers = tuple(int(part) for part in APP_VERSION.split('.')) + (0,)
version_info = VSVersionInfo(
    ffi=FixedFileInfo(filevers=version_numbers, prodvers=version_numbers,
                     mask=0x3f, flags=0, OS=0x40004, fileType=1, subtype=0, date=(0, 0)),
    kids=[StringFileInfo([StringTable('040904B0', [
        StringStruct('FileDescription', 'Codex Model Gate'),
        StringStruct('FileVersion', APP_VERSION),
        StringStruct('ProductName', 'Codex Model Gate'),
        StringStruct('ProductVersion', APP_VERSION),
        StringStruct('OriginalFilename', 'CodexModelGate.exe')])]),
        VarFileInfo([VarStruct('Translation', [1033, 1200])])])

PROJECT_ROOT = Path(SPECPATH)
APP_ICON = PROJECT_ROOT / "assets" / "CodexModelGate.ico"

datas = []
binaries = []
hiddenimports = []
tmp_ret = collect_all('pypdf')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('pdfplumber')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('reportlab')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('playwright')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
tmp_ret = collect_all('yaml')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]
datas.append((str(PROJECT_ROOT / 'docs' / 'manual'), 'docs/manual'))


a = Analysis(
    [str(PROJECT_ROOT / 'codex_model_gate_gui.py')],
    pathex=[str(PROJECT_ROOT)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='CodexModelGate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    version=version_info,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[str(APP_ICON)],
)
