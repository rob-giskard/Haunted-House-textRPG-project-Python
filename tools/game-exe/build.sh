#!/usr/bin/env bash
# Builds HauntedHouse.exe in the repo root: the game window as one standalone program,
# with its own Python (including tkinter) and walkthrough.txt bundled. No console window.
# Needs: bash, curl, tar, Go and Python. On Windows, run it from Git Bash.
# Run it again whenever the game code or the walkthrough changes.
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
rm -rf include libs Scripts
for d in test idlelib turtledemo ensurepip lib2to3 pydoc_data unittest/test sqlite3 venv tkinter/test; do rm -rf "Lib/$d"; done
rm -rf Lib/site-packages/*
rm -f DLLs/_test*.pyd DLLs/_ctypes_test.pyd DLLs/sqlite3.dll DLLs/_sqlite3.pyd DLLs/_msi.pyd
# tkinter stays (the game window needs it); only Tcl/Tk extras go: Tix, demos, time zones, build files
rm -rf tcl/tix8.4.3 tcl/nmake tcl/tk8.6/demos tcl/tcl8.6/tzdata tcl/*.lib tcl/*.sh
find . -name __pycache__ -type d -prune -exec rm -rf {} +
cd "$work"
"$PY" -m zipfile -c runtime.zip python/
cd "$here"

cp "$work/runtime.zip" runtime.zip
echo "Packing the game..."
rm -f game.zip
(cd ../.. && "$PY" -c "import zipfile, glob; z = zipfile.ZipFile('tools/game-exe/game.zip', 'w', zipfile.ZIP_DEFLATED); [z.write(f) for f in ['HauntedHouse.py', 'walkthrough.txt'] + sorted(glob.glob('haunted_house/*.py'))]; z.close()")
echo "Building HauntedHouse.exe..."
# -H windowsgui: a window program, so Windows doesn't open a console next to the game
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w -H windowsgui" -o ../../HauntedHouse.exe .
echo "Done: $(cd ../.. && pwd)/HauntedHouse.exe"
