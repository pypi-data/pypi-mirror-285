# -*- mode: python ; coding: utf-8 -*-
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--release", dest="release", help="release to include in generated zip file")
ns = parser.parse_args()


a = Analysis(
    ['imio/scan_helpers/main.py'],
    pathex=['.', 'imio/scan_helpers'],
    binaries=[],
    datas=[("imio/scan_helpers/version.txt", ".")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

from imio.scan_helpers.config import MAIN_EXE_NAME

exe0 = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name=MAIN_EXE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

from imio.scan_helpers.config import BUNDLE_NAME

coll = COLLECT(
    exe0,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name=BUNDLE_NAME,
)

# Archive everything into a zip file
zip_name = f'dist/{BUNDLE_NAME}'
if ns.release:
    zip_name += f'-{ns.release}'
print(f'Creating zip file {zip_name}.zip')
shutil.make_archive(zip_name, 'zip', f'dist/{BUNDLE_NAME}')
