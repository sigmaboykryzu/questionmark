#!/usr/bin/env python3
"""
Build EXE using PyInstaller
"""

import subprocess
import os
import shutil

def build_exe():
    print("=" * 80)
    print("🎮 BUILDING ROLLING GAME EXECUTABLE")
    print("=" * 80)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print("✓ PyInstaller found")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.run(["pip", "install", "pyinstaller"], check=True)
    
    # Build spec file content for a nice exe
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['questionmark.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['tkinter'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
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
    name='RollingGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    
    # Write spec file
    with open('RollingGame.spec', 'w') as f:
        f.write(spec_content)
    
    print("\n[1/3] Building with PyInstaller...")
    result = subprocess.run([
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "RollingGame",
        "--icon=icon.ico" if os.path.exists('icon.ico') else "",
        "--add-data", ".",
        "questionmark.py"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✓ Build successful!")
    else:
        print("✗ Build failed:")
        print(result.stderr)
        return False
    
    # Check if exe was created
    exe_path = "dist/RollingGame.exe"
    if os.path.exists(exe_path):
        print(f"\n✅ EXE CREATED: {exe_path}")
        exe_size = os.path.getsize(exe_path) / 1024 / 1024
        print(f"   File size: {exe_size:.1f} MB")
        
        # Copy to root for easy access
        if os.path.exists(exe_path):
            shutil.copy(exe_path, "RollingGame.exe")
            print(f"\n✓ Copied to root: RollingGame.exe")
        
        return True
    else:
        print("✗ EXE not found after build")
        return False

if __name__ == "__main__":
    success = build_exe()
    if success:
        print("\n" + "=" * 80)
        print("✅ BUILD COMPLETE!")
        print("   Run: RollingGame.exe")
        print("=" * 80)
