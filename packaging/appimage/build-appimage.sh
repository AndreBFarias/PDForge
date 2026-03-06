#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
APPDIR="$SCRIPT_DIR/PDForge.AppDir"
VERSION=$(grep -oP 'version = "\K[^"]+' "$PROJECT_DIR/pyproject.toml" | head -1)

echo "Construindo AppImage v${VERSION}..."

rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib" "$APPDIR/app"

rsync -a \
    --exclude="venv/" \
    --exclude=".venv/" \
    --exclude="__pycache__/" \
    --exclude=".git/" \
    --exclude=".github/" \
    --exclude="tests/" \
    --exclude="scripts/" \
    --exclude="packaging/" \
    --exclude="docs/sprints/" \
    --exclude="*.pyc" \
    "$PROJECT_DIR/" "$APPDIR/app/"

cp "$SCRIPT_DIR/AppRun" "$APPDIR/"
chmod +x "$APPDIR/AppRun"

cp "$SCRIPT_DIR/pdfforge.desktop" "$APPDIR/"

if [ -f "$PROJECT_DIR/assets/icon.png" ]; then
    cp "$PROJECT_DIR/assets/icon.png" "$APPDIR/pdfforge.png"
fi

cp "$(which python3)" "$APPDIR/usr/bin/python3"

PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
SITE_PACKAGES="/usr/lib/python${PYTHON_VERSION}"
if [ -d "$SITE_PACKAGES" ]; then
    cp -r "$SITE_PACKAGES" "$APPDIR/usr/lib/" 2>/dev/null || true
fi

if [ -d "$PROJECT_DIR/venv/lib" ]; then
    cp -r "$PROJECT_DIR/venv/lib/python${PYTHON_VERSION}/site-packages" "$APPDIR/usr/lib/python${PYTHON_VERSION}/" 2>/dev/null || true
fi

APPIMAGETOOL="$SCRIPT_DIR/appimagetool"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Baixando appimagetool..."
    ARCH=$(uname -m)
    wget -q "https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage" -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
fi

ARCH=$(uname -m) "$APPIMAGETOOL" "$APPDIR" "$SCRIPT_DIR/PDForge-${VERSION}-${ARCH}.AppImage"

echo "AppImage criado: $SCRIPT_DIR/PDForge-${VERSION}-$(uname -m).AppImage"

rm -rf "$APPDIR"
