# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_dynamic_libs

datas = [('C:\\Users\\duzho\\Desktop\\person_base\\backend\\static', 'backend/static'), ('C:\\Users\\duzho\\Desktop\\person_base\\backend/app', 'backend/app')]
binaries = [('C:\\ProgramData\\anaconda3\\Library\\bin\\sqlite3.dll', '.'), ('C:\\ProgramData\\anaconda3\\Library\\bin\\LIBBZ2.dll', '.'), ('C:\\ProgramData\\anaconda3\\Library\\bin\\libmpdec-4.dll', '.'), ('C:\\ProgramData\\anaconda3\\Library\\bin\\ffi.dll', '.'), ('C:\\ProgramData\\anaconda3\\Library\\bin\\libcrypto-3-x64.dll', '.'), ('C:\\ProgramData\\anaconda3\\Library\\bin\\libssl-3-x64.dll', '.')]
datas += collect_data_files('tiktoken_ext.openai_public')
datas += collect_data_files('unstructured')
datas += collect_data_files('nltk')
binaries += collect_dynamic_libs('sqlite3')
binaries += collect_dynamic_libs('ctypes')


a = Analysis(
    ['C:\\Users\\duzho\\Desktop\\person_base\\launcher_lyl.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=['uvicorn.logging', 'uvicorn.protocols.http', 'uvicorn.protocols.http.auto', 'uvicorn.protocols.websockets', 'uvicorn.protocols.websockets.auto', 'uvicorn.lifespan', 'uvicorn.lifespan.on', 'aiosqlite', 'sqlite3', '_sqlite3', 'tiktoken', 'tiktoken_ext', 'tiktoken_ext.openai_public', 'markdown', 'nltk', 'ctypes', '_ctypes'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PIL', 'matplotlib', 'scipy', 'numpy.distutils'],
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
    name='知识问答系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
