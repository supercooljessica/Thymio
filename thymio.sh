#!/bin/sh
# macOS/Linux launcher for tools/thymio.py. Sets up .venv on first run.
# Usage: ./thymio.sh list
ROOT="$(cd "$(dirname "$0")" && pwd)"
PY="$ROOT/.venv/bin/python"

if ! "$PY" -c "import tdmclient" 2>/dev/null; then
    echo "Setting up the Python environment in .venv (first run only)..."
    python3 -m venv "$ROOT/.venv" || exit 1
    "$PY" -m pip install --quiet --disable-pip-version-check -r "$ROOT/requirements.txt" || exit 1
fi

exec "$PY" "$ROOT/tools/thymio.py" "$@"
