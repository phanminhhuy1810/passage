#!/usr/bin/env bash
# Install only into this project's virtual environment.
set -euo pipefail

PROJECT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$PROJECT_DIR"

fail() {
  printf '\n%s\n' "$1" >&2
  exit 1
}

supported_python() {
  "$1" -c 'import sys; raise SystemExit(not ((3, 12) <= sys.version_info[:2] < (3, 14)))' >/dev/null 2>&1
}

if [[ -n "${PYTHON_BIN:-}" ]]; then
  command -v "$PYTHON_BIN" >/dev/null 2>&1 || fail "Không tìm thấy PYTHON_BIN: $PYTHON_BIN"
  supported_python "$PYTHON_BIN" || fail "Cần Python 3.12–3.13; PYTHON_BIN hiện không tương thích. Khuyến nghị Python 3.12."
  PROJECT_PYTHON="$PYTHON_BIN"
elif [[ -x .venv/bin/python ]] && supported_python .venv/bin/python; then
  PROJECT_PYTHON="$PROJECT_DIR/.venv/bin/python"
else
  PROJECT_PYTHON=""
  for candidate in python3.12 python3.13 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && supported_python "$candidate"; then
      PROJECT_PYTHON="$(command -v "$candidate")"
      break
    fi
  done
  [[ -n "$PROJECT_PYTHON" ]] || fail "Chưa tìm thấy Python 3.12–3.13. Cài Python 3.12 từ python.org, rồi chạy lại; hoặc đặt PYTHON_BIN=/đường/dẫn/python3.12. Python 3.14 chưa được hỗ trợ trong bản này."
fi

[[ -f requirements-lock.txt ]] || fail "Thiếu requirements-lock.txt. Hãy tải đầy đủ thư mục dự án rồi chạy lại."

if [[ -e .venv && ! -x .venv/bin/python ]]; then
  fail "Thư mục .venv đã tồn tại nhưng không dùng được. Hãy đổi tên nó để giữ bản cũ, rồi chạy lại setup.sh."
fi
if [[ -x .venv/bin/python ]]; then
  supported_python .venv/bin/python || fail ".venv hiện dùng Python không tương thích. Hãy đổi tên .venv, rồi chạy lại với Python 3.12."
else
  printf '%s\n' 'Tạo môi trường Python riêng cho dự án…'
  "$PROJECT_PYTHON" -m venv .venv
fi

trap 'printf "\nCài đặt dừng vì có lỗi. Đọc thông báo phía trên, sửa nguyên nhân rồi chạy lại bash setup.sh. Các lần tải thành công được giữ lại.\n" >&2' ERR
printf '\n%s\n' '1/3 · Cài thư viện vào .venv (lần đầu cần Internet)…'
.venv/bin/python -m pip install -r requirements-lock.txt
printf '\n%s\n' '2/3 · Chuẩn bị bộ dữ liệu tiếng Việt…'
.venv/bin/python dataset.py
printf '\n%s\n' '3/3 · Tải mô hình và chuẩn bị vector đoạn văn (lần đầu có thể mất vài phút)…'
.venv/bin/python setup_model.py

printf '\n%s\n' 'Đã chuẩn bị xong. Trên macOS: mở “Open Retrieval Lab.command”.'
printf '%s\n' 'Hoặc chạy: .venv/bin/python server.py --host 127.0.0.1 --port 8765'
printf '%s\n' 'Sau đó mở http://127.0.0.1:8765. Dừng máy chủ bằng Ctrl+C trong Terminal.'
