# 可攜版只收錄正式前端；設定與文件由發布腳本以明確清單複製。
from pathlib import Path

root = Path(SPECPATH)
a = Analysis(
    [str(root / "scripts" / "portable_launcher.py")],
    pathex=[str(root / "src")],
    binaries=[],
    datas=[(str(root / "src/cmp180_evm/web/static"), "cmp180_evm/web/static")],
    hiddenimports=["RsInstrument"],
    hookspath=[],
    hooksconfig={"matplotlib": {"backends": ["Agg"]}},
    runtime_hooks=[],
    excludes=["pytest", "tkinter"],
    noarchive=False,
)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="CMP180", console=True)
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name="CMP180")
