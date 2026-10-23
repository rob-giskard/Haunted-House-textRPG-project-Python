#!/usr/bin/env bash
# Builds HauntedHouse.exe (standalone, with its own Python) in the repo root.
# Needs: bash, curl, tar, Go and Python. On Windows, run it from Git Bash.
# Run it again whenever the game code changes.
set -euo pipefail
cd "$(dirname "$0")"
here=$(pwd)
PY="${PYTHON:-python3}"; command -v "$PY" >/dev/null || PY=python

RELEASE=20241016
VERSION=3.12.7
URL="https://github.com/astral-sh/python-build-standalone/releases/download/$RELEASE/cpython-$VERSION+$RELEASE-x86_64-pc-windows-msvc-install_only_stripped.tar.gz"

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
echo "Downloading Python $VERSION for Windows..."
curl -sSL "$URL" -o "$work/python.tar.gz"
tar -xzf "$work/python.tar.gz" -C "$work"

echo "Trimming parts the game never uses..."
cd "$work/python"
rm -rf tcl include libs Scripts
for d in test idlelib tkinter turtledemo ensurepip lib2to3 pydoc_data unittest/test sqlite3 venv; do rm -rf "Lib/$d"; done
rm -rf Lib/site-packages/*
rm -f DLLs/_test*.pyd DLLs/_ctypes_test.pyd DLLs/_tkinter.pyd DLLs/tcl86t.dll DLLs/tk86t.dll DLLs/sqlite3.dll DLLs/_sqlite3.pyd DLLs/_msi.pyd
find . -name __pycache__ -type d -prune -exec rm -rf {} +
cd "$work"
"$PY" -m zipfile -c runtime.zip python/
cd "$here"

cp "$work/runtime.zip" runtime.zip
echo "Packing the game..."
rm -f game.zip
(cd ../.. && "$PY" -c "import zipfile, glob; z = zipfile.ZipFile('tools/game-exe/game.zip', 'w', zipfile.ZIP_DEFLATED); [z.write(f) for f in ['HauntedHouse.py'] + sorted(glob.glob('haunted_house/*.py'))]; z.close()")
echo "Building HauntedHouse.exe..."
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o ../../HauntedHouse.exe .
echo "Done: $(cd ../.. && pwd)/HauntedHouse.exe"
