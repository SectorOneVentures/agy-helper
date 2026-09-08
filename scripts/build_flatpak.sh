#!/usr/bin/env bash
# Build Flatpak bundle for Agy Helper
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$ROOT_DIR"

echo "=== Building Agy Helper Flatpak ==="

if ! command -v flatpak-builder &> /dev/null; then
    echo "Error: flatpak-builder is not installed."
    echo "Install it with: sudo apt install flatpak-builder"
    exit 1
fi

# Ensure Flathub remote is added
flatpak remote-add --user --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo || true

# Install GNOME Runtime & SDK if needed
flatpak install --user -y flathub org.gnome.Platform//46 org.gnome.Sdk//46 || true

# Build into flatpak_build/
rm -rf flatpak_build flatpak_repo
flatpak-builder --user --install-deps-from=flathub --force-clean flatpak_build flatpak/org.sectoroneventures.AgyHelper.yml --repo=flatpak_repo

# Export single-file .flatpak bundle
mkdir -p dist
flatpak build-bundle flatpak_repo dist/AgyHelper.flatpak org.sectoroneventures.AgyHelper

echo "=== Flatpak bundle generated: dist/AgyHelper.flatpak ==="
