"""從 ZIP 解壓到中文路徑，以離線 HTTP 驗證實際 EXE。"""

import json
import socket
import subprocess
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    destination = ROOT / "output" / f"portable-check-{time.time_ns()}" / "中文路徑"
    with zipfile.ZipFile(ROOT / "dist/CMP180-Windows-x64.zip") as archive:
        # 發布檔不得夾帶開發機的量測 output 或私人設定。
        assert not any("/output/" in n or ".private." in n for n in archive.namelist())
        archive.extractall(destination)
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    base = f"http://127.0.0.1:{port}"
    install = destination / "CMP180"
    log_path = destination / "smoke.log"
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            [str(install / "CMP180.exe"), "--no-browser", "--port", str(port)],
            cwd=destination,
            stdout=log,
            stderr=log,
            creationflags=subprocess.CREATE_NO_WINDOW,
        )
        try:
            for _ in range(60):
                try:
                    with urllib.request.urlopen(base + "/api/status", timeout=2) as response:
                        status = json.load(response)
                    break
                except OSError:
                    if process.poll() is not None:
                        raise RuntimeError(log_path.read_text(encoding="utf-8")) from None
                    time.sleep(1)
            else:
                raise TimeoutError("EXE startup timed out")
            assert status["mode"] == "mock" and not status["hardware_enabled"]
            for path in ("/", "/app.js", "/assets/cmp180-hero.png", "/api/capabilities",
                         "/diagrams/system-architecture.html"):
                with urllib.request.urlopen(base + path, timeout=10) as response:
                    assert response.status == 200 and response.read()
            request = urllib.request.Request(
                base + "/api/mock/constellation",
                data=b'{"point_count":128,"test_name":"portable-smoke"}',
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(request, timeout=60) as response:
                result = json.load(response)
            assert (install / "output").is_dir()
            for path in result["artifact_urls"].values():
                with urllib.request.urlopen(base + path, timeout=10) as response:
                    assert response.status == 200 and response.read()
            print("PASS: ZIP extraction, Chinese path, alternate cwd, Mock lock, assets, configs, PNG/CSV/JSON artifacts")
        finally:
            # 此測試只啟動無儀器的 Mock 程序，完成後回收該子程序。
            process.terminate()
            process.wait(timeout=10)


if __name__ == "__main__":
    main()
