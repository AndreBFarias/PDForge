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
DEPS_DIR="$APPDIR/usr/lib/python${PYTHON_VERSION}/site-packages"
mkdir -p "$DEPS_DIR"

pip install --target="$DEPS_DIR" -r "$PROJECT_DIR/requirements-appimage.txt" --quiet

APPIMAGETOOL="$SCRIPT_DIR/appimagetool"
if [ ! -f "$APPIMAGETOOL" ]; then
    echo "Baixando appimagetool..."
    ARCH=$(uname -m)
    TOOL_URL="https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-${ARCH}.AppImage"
    wget -q "$TOOL_URL" -O "$APPIMAGETOOL"
    chmod +x "$APPIMAGETOOL"
    echo "appimagetool cacheado em $APPIMAGETOOL"
fi

ARCH=$(uname -m) "$APPIMAGETOOL" "$APPDIR" "$SCRIPT_DIR/PDForge-${VERSION}-${ARCH}.AppImage"

echo "AppImage criado: $SCRIPT_DIR/PDForge-${VERSION}-$(uname -m).AppImage"

rm -rf "$APPDIR"
