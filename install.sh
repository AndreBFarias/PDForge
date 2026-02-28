#!/bin/bash
set -e

APP_NAME="pdfforge"
INSTALL_DIR="$HOME/.local/$APP_NAME"
APP_DIR="$INSTALL_DIR/app"
VENV_DIR="$INSTALL_DIR/venv"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_PATH="/usr/local/bin/$APP_NAME"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Instalando dependências do sistema..."
sudo apt-get update -qq
sudo apt-get install -y \
    python3 python3-venv python3-pip \
    libgl1-mesa-glx libglib2.0-0 libxcb-xinerama0 \
    libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0 \
    libxcb-keysyms1 libxcb-randr0 libxcb-render-util0 \
    libxcb-xinerama0 libxcb-shape0 libdbus-1-3

echo "Criando diretórios..."
mkdir -p "$APP_DIR" "$VENV_DIR" "$ICON_DIR" "$DESKTOP_DIR"

echo "Copiando arquivos da aplicação..."
rsync -a --delete \
    --exclude="venv/" \
    --exclude=".venv/" \
    --exclude="__pycache__/" \
    --exclude=".git/" \
    --exclude="tests/" \
    --exclude="sprints/" \
    --exclude="QR-Code-Void-Generator/" \
    --exclude="sprint-*.md" \
    --exclude="*.pyc" \
    "$SCRIPT_DIR/" "$APP_DIR/"

echo "Criando ambiente virtual..."
python3 -m venv "$VENV_DIR"
"$VENV_DIR/bin/pip" install --upgrade pip -q
"$VENV_DIR/bin/pip" install -r "$APP_DIR/requirements.txt" -q

echo "Instalando ícone..."
if [ -f "$APP_DIR/assets/icon.png" ]; then
    cp "$APP_DIR/assets/icon.png" "$ICON_DIR/$APP_NAME.png"
fi

echo "Criando entrada .desktop..."
cat > "$DESKTOP_DIR/$APP_NAME.desktop" <<EOF
[Desktop Entry]
Name=PDForge
Comment=Editor de PDF com GUI e ML para Linux
Exec=$BIN_PATH %f
Icon=$APP_NAME
Type=Application
Categories=Office;Graphics;
MimeType=application/pdf;
StartupNotify=true
Terminal=false
EOF

echo "Criando wrapper em /usr/local/bin..."
sudo tee "$BIN_PATH" > /dev/null <<EOF
#!/bin/bash
exec "$VENV_DIR/bin/python" "$APP_DIR/main.py" "\$@"
EOF
sudo chmod +x "$BIN_PATH"

echo "Atualizando base de dados de aplicações..."
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
gtk-update-icon-cache -f -t "$HOME/.local/share/icons/hicolor" 2>/dev/null || true

if command -v gsettings &>/dev/null; then
    FAVORITES=$(gsettings get org.gnome.shell favorite-apps)
    if [[ "$FAVORITES" != *"$APP_NAME"* ]]; then
        NEW_FAV=$(echo "$FAVORITES" | sed "s/\]/, '$APP_NAME.desktop']/")
        gsettings set org.gnome.shell favorite-apps "$NEW_FAV" 2>/dev/null || true
    fi
fi

echo "Instalacao concluida. Execute: pdfforge"
