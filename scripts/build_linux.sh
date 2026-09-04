#!/usr/bin/env bash
set -e

echo "=== Building Agy Helper for Linux ==="

# Check PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "Installing pyinstaller..."
    pip3 install pyinstaller
fi

# Build standalone binary
pyinstaller --clean packaging/agy_helper.spec

echo "Build complete! Linux standalone binary is at dist/AgyHelper"
