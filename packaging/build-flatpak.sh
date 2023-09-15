#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR/build-flatpak"
REPO_DIR="$SCRIPT_DIR/flatpak-repo"
APP_ID="com.github.andrebfarias.pdfforge"

echo "Construindo pacote Flatpak..."

rm -rf "$BUILD_DIR"

flatpak-builder --force-clean "$BUILD_DIR" "$SCRIPT_DIR/flatpak/$APP_ID.yml"

flatpak-builder --repo="$REPO_DIR" --force-clean "$BUILD_DIR" "$SCRIPT_DIR/flatpak/$APP_ID.yml"

flatpak build-bundle "$REPO_DIR" "$SCRIPT_DIR/pdfforge.flatpak" "$APP_ID"

echo "Pacote criado: $SCRIPT_DIR/pdfforge.flatpak"

rm -rf "$BUILD_DIR" "$REPO_DIR"
