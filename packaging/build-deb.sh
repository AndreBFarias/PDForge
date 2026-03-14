#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$SCRIPT_DIR/build-deb"
PKG_NAME="pdfforge"
VERSION=$(grep -oP 'version = "\K[^"]+' "$PROJECT_DIR/pyproject.toml" | head -1)

echo "Construindo pacote .deb v${VERSION}..."

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR/opt/$PKG_NAME"
mkdir -p "$BUILD_DIR/usr/local/bin"
mkdir -p "$BUILD_DIR/usr/share/applications"
mkdir -p "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$BUILD_DIR/DEBIAN"

cp "$SCRIPT_DIR/deb/DEBIAN/control" "$BUILD_DIR/DEBIAN/"
cp "$SCRIPT_DIR/deb/DEBIAN/postinst" "$BUILD_DIR/DEBIAN/"
cp "$SCRIPT_DIR/deb/DEBIAN/prerm" "$BUILD_DIR/DEBIAN/"
chmod 755 "$BUILD_DIR/DEBIAN/postinst" "$BUILD_DIR/DEBIAN/prerm"

sed -i "s/^Version:.*/Version: ${VERSION}/" "$BUILD_DIR/DEBIAN/control"

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
    "$PROJECT_DIR/" "$BUILD_DIR/opt/$PKG_NAME/"

cat > "$BUILD_DIR/usr/local/bin/$PKG_NAME" <<'WRAPPER'
#!/bin/bash
if [ -x /opt/pdfforge/venv/bin/python ]; then
    exec /opt/pdfforge/venv/bin/python /opt/pdfforge/main.py "$@"
else
    exec python3 /opt/pdfforge/main.py "$@"
fi
WRAPPER
chmod 755 "$BUILD_DIR/usr/local/bin/$PKG_NAME"

cat > "$BUILD_DIR/usr/share/applications/$PKG_NAME.desktop" <<EOF
[Desktop Entry]
Name=PDForge
Comment=Editor de PDF com GUI e ML para Linux
Exec=$PKG_NAME %f
Icon=$PKG_NAME
Type=Application
Categories=Office;Graphics;
MimeType=application/pdf;
StartupNotify=true
Terminal=false
EOF

if [ -f "$PROJECT_DIR/assets/icon.png" ]; then
    cp "$PROJECT_DIR/assets/icon.png" "$BUILD_DIR/usr/share/icons/hicolor/256x256/apps/$PKG_NAME.png"
fi

dpkg-deb --build "$BUILD_DIR" "$SCRIPT_DIR/${PKG_NAME}_${VERSION}_all.deb"
echo "Pacote criado: $SCRIPT_DIR/${PKG_NAME}_${VERSION}_all.deb"

rm -rf "$BUILD_DIR"
