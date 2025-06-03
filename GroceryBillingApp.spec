# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all necessary data files and modules
streamlit_data = collect_data_files('streamlit')
plotly_data = collect_data_files('plotly')
pandas_data = collect_data_files('pandas')
sklearn_data = collect_data_files('sklearn')

# Add hidden imports
hidden_imports = [
    'streamlit',
    'pandas',
    'plotly',
    'plotly.express',
    'sklearn',
    'sklearn.linear_model',
    'numpy',
    'openpyxl',
    'email.mime.multipart',
    'email.mime.text',
    'email.mime.application',
    'smtplib'
]
hidden_imports.extend(collect_submodules('streamlit'))
hidden_imports.extend(collect_submodules('plotly'))

# Update this to match your main file name
main_file = 'app.py'  # Change this to your actual main file name

a = Analysis(
    ['standalone_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        (main_file, '.'),
        ('pages', 'pages'),
        ('utils', 'utils'),
        ('.streamlit', '.streamlit'),
    ] + streamlit_data + plotly_data + pandas_data + sklearn_data,
    hiddenimports=hidden_imports,
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
    name='GroceryBillingSystem',
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
    icon='NONE'
)