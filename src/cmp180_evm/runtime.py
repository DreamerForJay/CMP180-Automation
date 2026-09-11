"""執行時資源與可攜版資料目錄。"""

import sys
from pathlib import Path


def project_root() -> Path:
    # EXE 旁保留設定及輸出，避免寫入 PyInstaller 暫存或內部資源目錄。
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[2]
