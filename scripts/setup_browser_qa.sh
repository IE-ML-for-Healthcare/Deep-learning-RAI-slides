#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_DIR="${ROOT_DIR}/.venv-reveal-qa"

if [ -z "${PYTHON_BIN:-}" ]; then
  for candidate in python3 python py; do
    if command -v "${candidate}" >/dev/null 2>&1 && "${candidate}" -c "import sys" >/dev/null 2>&1; then
      PYTHON_BIN="${candidate}"
      break
    fi
  done
fi

if [ -z "${PYTHON_BIN:-}" ]; then
  echo "No working Python interpreter found (tried python3, python, py)." >&2
  echo "On Windows, a bare python3/python that prints a Microsoft Store prompt is not a real interpreter." >&2
  echo "Install Python from https://www.python.org/downloads/ with 'Add python.exe to PATH' checked, then re-run this script." >&2
  exit 1
fi

echo "Using Python interpreter: ${PYTHON_BIN}"

cd "${ROOT_DIR}"

# venv layout differs by OS: POSIX uses bin/python, native Windows uses Scripts/python.exe
if [ ! -x "${VENV_DIR}/bin/python" ] && [ ! -x "${VENV_DIR}/Scripts/python.exe" ]; then
  "${PYTHON_BIN}" -m venv "${VENV_DIR}"
fi

if [ -x "${VENV_DIR}/bin/python" ]; then
  VENV_PYTHON="${VENV_DIR}/bin/python"
elif [ -x "${VENV_DIR}/Scripts/python.exe" ]; then
  VENV_PYTHON="${VENV_DIR}/Scripts/python.exe"
else
  echo "Could not find a Python interpreter inside ${VENV_DIR} after creating it." >&2
  exit 1
fi

"${VENV_PYTHON}" -m pip install --upgrade pip
"${VENV_PYTHON}" -m pip install -r requirements-qa.txt

if ! "${VENV_PYTHON}" -m playwright install chromium; then
  "${VENV_PYTHON}" -m playwright install --with-deps chromium
fi

"${VENV_PYTHON}" -c "from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    p.chromium.launch().close()
print('Chromium launch passed')"

echo "Browser QA is ready"
echo "Run: ${VENV_PYTHON} scripts/check_browser_qa.py"
