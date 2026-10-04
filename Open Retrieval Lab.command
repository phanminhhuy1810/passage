#!/usr/bin/env bash
set -euo pipefail
PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$PROJECT_DIR"

if [[ ! -x .venv/bin/python ]]; then
  printf '%s\n' 'Dự án chưa được cài đặt. Trong Terminal, vào thư mục này rồi chạy: bash setup.sh'
  printf '%s\n' 'Xem README.md nếu chưa biết mở Terminal. Trình mở này không tự tải mô hình.'
  exit 1
fi

exec .venv/bin/python - <<'PY'
import json
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path.cwd()
HOST, PORT = "127.0.0.1", 8765
URL = f"http://{HOST}:{PORT}"
APP = "vietnamese-retrieval-lab"
process = None


def status():
    try:
        with urllib.request.urlopen(f"{URL}/api/status", timeout=2) as response:
            return json.load(response)
    except (OSError, ValueError, urllib.error.URLError):
        return None


def stop_owned_server():
    if process is not None and process.poll() is None:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=4)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def interrupted(signum, frame):
    print("\nĐang dừng Retrieval Lab…", flush=True)
    stop_owned_server()
    raise SystemExit(0)


signal.signal(signal.SIGINT, interrupted)
signal.signal(signal.SIGTERM, interrupted)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
    probe.settimeout(1)
    occupied = probe.connect_ex((HOST, PORT)) == 0

if occupied:
    initial = status()
    if not isinstance(initial, dict) or initial.get("app") != APP:
        sys.exit(f"Cổng {PORT} đang được một ứng dụng khác dùng. Hãy dừng ứng dụng đó hoặc chạy server.py với --port khác. Không có ứng dụng nào bị tắt.")
    print("Retrieval Lab đã chạy. Đợi trạng thái sẵn sàng…", flush=True)
else:
    if not (ROOT / "server.py").is_file():
        sys.exit("Thiếu server.py. Hãy tải đầy đủ thư mục dự án.")
    print("Đang mở Retrieval Lab. Giữ Terminal này mở; Ctrl+C để dừng.\n", flush=True)
    process = subprocess.Popen(
        [sys.executable, "-u", "server.py", "--host", HOST, "--port", str(PORT)],
        cwd=ROOT,
        start_new_session=True,
    )

deadline = time.monotonic() + 180
try:
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            sys.exit(f"Máy chủ đã dừng (mã {process.returncode}). Đọc lỗi phía trên. Nếu thiếu dữ liệu/thư viện/mô hình, chạy: bash setup.sh")
        current = status()
        if isinstance(current, dict) and current.get("app") == APP and current.get("ready"):
            print(f"\nSẵn sàng: {URL}", flush=True)
            if not webbrowser.open(URL, new=2):
                print("Không mở được trình duyệt tự động; hãy mở địa chỉ ở trên.", flush=True)
            if process is None:
                print("Đã dùng lại máy chủ đang chạy. Dừng ở Terminal đã mở máy chủ đó.", flush=True)
                sys.exit(0)
            sys.exit(process.wait())
        time.sleep(0.4)
    sys.exit("Chưa sẵn sàng sau 3 phút. Kiểm tra lỗi ở Terminal và chạy lại bash setup.sh nếu quá trình chuẩn bị chưa hoàn tất.")
finally:
    stop_owned_server()
PY
