"""Windows 可攜版入口；雙擊預設只啟用離線示範。"""

import argparse
import os
import webbrowser
from threading import Timer

from cmp180_evm.runtime import project_root


def main() -> None:
    parser = argparse.ArgumentParser(description="CMP180 Windows portable workstation")
    parser.add_argument("--hardware", action="store_true", help="Enable guarded hardware endpoints")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    # 固定工作目錄讓既有相對設定路徑不受捷徑或啟動位置影響。
    os.chdir(project_root())
    from cmp180_evm.web.server import Cmp180WebHandler, ExclusiveThreadingHTTPServer

    # 雙擊不授權實機操作；僅明確旗標開啟既有安全閘門，且只綁定本機。
    Cmp180WebHandler.hardware_enabled = args.hardware
    Cmp180WebHandler.custom_hardware_enabled = args.hardware
    server = ExclusiveThreadingHTTPServer(("127.0.0.1", args.port), Cmp180WebHandler)
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"CMP180: {url}", flush=True)
    print("Hardware enabled" if args.hardware else "DEMO / MOCK ONLY", flush=True)
    print("Press Ctrl+C to stop. Results: output/", flush=True)
    timer = None
    try:
        if not args.no_browser:
            # 先成功綁定埠號才開啟瀏覽器，避免誤開另一個工作站。
            timer = Timer(0.5, webbrowser.open, args=(url,))
            timer.daemon = True
            timer.start()
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        # 中斷時清理延遲開頁與 HTTP socket；實機 RF cleanup 仍由原 workflow 負責。
        if timer is not None:
            timer.cancel()
        server.server_close()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"Startup failed: {exc}", flush=True)
        input("Press Enter to exit...")
        raise SystemExit(1) from exc
