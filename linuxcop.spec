# linuxcop.spec

import sys, os
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None
datas = [
    ('docs', 'docs'),
]

hiddenimports = collect_submodules('src')
hiddenimports += [
    'langchain_experimental',
    'wikipedia',
    'duckduckgo_search',
    'arxiv',
    'google_search_results',
    'youtube_search_python'
]

a = Analysis(
    ['app.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='linuxcop',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='linuxcop'
)
