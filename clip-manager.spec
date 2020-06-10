# -*- mode: python ; coding: utf-8 -*-
import os 
import pyfiglet.fonts
import wcwidth

block_cipher = None


a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[
                 (os.path.join(os.path.dirname(pyfiglet.fonts.__file__), "*.f*"), os.path.join("pyfiglet", "fonts")),
                 (os.path.dirname(wcwidth.__file__), 'wcwidth')                 
                 ],
             hiddenimports=['tkinter', 'pyfiglet.fonts'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='clip-manager',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True )