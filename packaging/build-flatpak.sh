#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR/build-flatpak"
REPO_DIR="$SCRIPT_DIR/flatpak-repo"
APP_ID="com.github.andrebfarias.pdfforge"
MANIFEST="$SCRIPT_DIR/flatpak/$APP_ID.yml"

echo "Construindo pacote Flatpak..."

if ! command -v flatpak-builder &> /dev/null; then
    echo "Erro: flatpak-builder nao encontrado."
    echo "Instale com: sudo apt install flatpak-builder"
    exit 1
fi

if ! command -v flatpak &> /dev/null; then
    echo "Erro: flatpak nao encontrado."
    echo "Instale com: sudo apt install flatpak"
    exit 1
fi

if [ ! -f "$MANIFEST" ]; then
    echo "Erro: manifesto nao encontrado: $MANIFEST"
    exit 1
fi

rm -rf "$BUILD_DIR"

flatpak-builder --force-clean "$BUILD_DIR" "$MANIFEST"

flatpak-builder --repo="$REPO_DIR" --force-clean "$BUILD_DIR" "$MANIFEST"

flatpak build-bundle "$REPO_DIR" "$SCRIPT_DIR/pdfforge.flatpak" "$APP_ID"

echo "Pacote criado: $SCRIPT_DIR/pdfforge.flatpak"

rm -rf "$BUILD_DIR" "$REPO_DIR"
