#!/usr/bin/env bash
set -e

echo "=== Building Agy Helper for macOS (.app & .dmg) ==="

if ! command -v pyinstaller &> /dev/null; then
    pip3 install pyinstaller
fi

# Build .app bundle
pyinstaller --clean \
    --windowed \
    --name "AgyHelper" \
    --icon "assets/icon.png" \
    --add-data "assets:assets" \
    main.py

echo "Creating DMG package..."
if command -v create-dmg &> /dev/null; then
    mkdir -p dist/dmg
    create-dmg \
        --volname "Agy Helper Installer" \
        --window-pos 200 120 \
        --window-size 600 400 \
        --icon-size 100 \
        --icon "AgyHelper.app" 175 190 \
        --app-drop-link 425 190 \
        "dist/AgyHelper.dmg" \
        "dist/AgyHelper.app"
    echo "macOS DMG created successfully at dist/AgyHelper.dmg"
else
    echo "create-dmg not found. Created .app bundle in dist/AgyHelper.app"
    echo "To produce a .dmg, install create-dmg via brew: brew install create-dmg"
fi
