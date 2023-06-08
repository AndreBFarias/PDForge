#!/bin/bash
set -e

APP_NAME="pdfforge"
INSTALL_DIR="$HOME/.local/$APP_NAME"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
DESKTOP_DIR="$HOME/.local/share/applications"
BIN_PATH="/usr/local/bin/$APP_NAME"

echo "Removendo $APP_NAME..."

[ -d "$INSTALL_DIR" ] && rm -rf "$INSTALL_DIR" && echo "Removido: $INSTALL_DIR"
[ -f "$ICON_DIR/$APP_NAME.png" ] && rm -f "$ICON_DIR/$APP_NAME.png"
[ -f "$DESKTOP_DIR/$APP_NAME.desktop" ] && rm -f "$DESKTOP_DIR/$APP_NAME.desktop"
[ -f "$BIN_PATH" ] && sudo rm -f "$BIN_PATH" && echo "Removido: $BIN_PATH"

update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

if command -v gsettings &>/dev/null; then
    FAVORITES=$(gsettings get org.gnome.shell favorite-apps)
    if [[ "$FAVORITES" == *"$APP_NAME"* ]]; then
        NEW_FAV=$(echo "$FAVORITES" | sed "s/, '$APP_NAME.desktop'//;s/'$APP_NAME.desktop', //;s/'$APP_NAME.desktop'//")
        gsettings set org.gnome.shell favorite-apps "$NEW_FAV" 2>/dev/null || true
    fi
fi

echo "Desinstalacao concluida."
