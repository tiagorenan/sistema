# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all

# ⚠️ PASSO 1: SUBSTITUA COM SEU CAMINHO RAIZ ABSOLUTO ⚠️
NEXUS_PATH = 'C:\\Users\\Tiago Renan\\Documents\\TIAGO\\Faculdade\\ADS_UNIT\\4º Período\\Residência\\nexus_pesquisa'

# ⚠️ PASSO 2: SUBSTITUA COM SEU CAMINHO SITE-PACKAGES ABSOLUTO ⚠️
SITE_PACKAGES_PATH = 'C:\\Users\\Tiago Renan\\Documents\\TIAGO\\Faculdade\\ADS_UNIT\\4º Período\\Residência\\nexus_pesquisa\\venv\\Lib\\site-packages'


datas = [('interface/imagens', 'interface/imagens')]
binaries = []
hiddenimports = []

# Tentativa de coletar automaticamente todas as dependências do PySide6
tmp_ret = collect_all('PySide6')
datas += tmp_ret[0]; binaries += tmp_ret[1]; hiddenimports += tmp_ret[2]


a = Analysis(
    ['__main__.py'],
    # AQUI ESTÁ A CORREÇÃO FINAL: Pathex deve incluir a raiz e o site-packages!
    pathex=[NEXUS_PATH, SITE_PACKAGES_PATH],
    
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
    name='NEXUS_PESQUISA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['nexus_icon.ico'],
)