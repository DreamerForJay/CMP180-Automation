"""建立 Windows EXE 與可分享的 ZIP，不攜帶本機量測紀錄。"""

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "PyInstaller", "--noconfirm", "CMP180.spec"],
        cwd=ROOT,
        check=True,
    )
    target = ROOT / "dist" / "CMP180"
    # 僅發布範例設定，排除 private/local 設定與 output 實機證據。
    config_dir = target / "configs"
    config_dir.mkdir(exist_ok=True)
    for source in sorted((ROOT / "configs").glob("*.example.*")):
        shutil.copy2(source, config_dir / source.name)
    shutil.copy2(ROOT / "configs/scpi_command_map.yaml", config_dir)
    for name in ("hardware-test-sop.md", "user-guide.md", "windows-portable.md"):
        destination = target / "docs" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "docs" / name, destination)
    diagrams = target / "docs/diagrams"
    diagrams.mkdir(parents=True, exist_ok=True)
    for name in ("system-architecture.html", "single-measurement-lifecycle.html"):
        shutil.copy2(ROOT / "docs/diagrams" / name, diagrams)
    shutil.copy2(ROOT / "docs/windows-portable.md", target / "使用說明.txt")
    # 原始專案若提供授權檔則一併發布，不自行生成或更改授權條款。
    for license_file in ROOT.glob("LICENSE*"):
        if license_file.is_file():
            shutil.copy2(license_file, target)
    shutil.make_archive(str(ROOT / "dist/CMP180-Windows-x64"), "zip", ROOT / "dist", "CMP180")


if __name__ == "__main__":
    main()
