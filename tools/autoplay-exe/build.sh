#!/usr/bin/env bash
# Builds HauntedHouseAutoplay.exe in the repo root.
# Needs: bash and Go. On Windows, run it from Git Bash.
# It copies the current autoplay.py in at build time, so the exe never runs an outdated copy.
set -euo pipefail
cd "$(dirname "$0")"
cp ../../autoplay.py autoplay.py
echo "Building HauntedHouseAutoplay.exe..."
GOOS=windows GOARCH=amd64 CGO_ENABLED=0 go build -trimpath -ldflags "-s -w" -o ../../HauntedHouseAutoplay.exe .
echo "Done: $(cd ../.. && pwd)/HauntedHouseAutoplay.exe"
