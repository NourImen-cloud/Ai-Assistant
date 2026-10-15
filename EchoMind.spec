# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

datas = [
    ('frontend/dist', 'frontend/dist'),
    ('.env', '.'),
]

# Collect data files from relevant packages
datas += collect_data_files('trafilatura')
datas += collect_data_files('pypdf')

hiddenimports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'pyttsx3.drivers',
    'pyttsx3.drivers.sapi5',
    'speech_recognition',
    'psutil',
    'pypdf',
    'docx',
    'pandas',
    'matplotlib',
    'openpyxl',
    'bs4',
    'trafilatura',
    'ddgs',
    'openai',
]
hiddenimports += collect_submodules('assistant')

a = Analysis(
    ['desktop_app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'unittest',
        'pytest',
        'torch',
        'transformers',
        'tensorflow',
        'scipy',
        'IPython',
        'notebook',
        'jupyter',
        'torchvision',
        'torchaudio',
        'tensorboard',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='EchoMind',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='EchoMind',
)
