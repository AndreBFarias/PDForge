#!/bin/bash
set -e

if [ -z "$1" ]; then
    echo "Uso: $0 <versao>"
    echo "Exemplo: $0 1.1.0"
    exit 1
fi

VERSION="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Atualizando versao para ${VERSION}..."

sed -i "s/^version = .*/version = \"${VERSION}\"/" "$PROJECT_DIR/pyproject.toml"
echo "  pyproject.toml"

sed -i "s/^APP_VERSION = .*/APP_VERSION = \"${VERSION}\"/" "$PROJECT_DIR/config/settings.py"
echo "  config/settings.py"

sed -i "s/^Version:.*/Version: ${VERSION}/" "$SCRIPT_DIR/deb/DEBIAN/control"
echo "  packaging/deb/DEBIAN/control"

echo "Versao atualizada para ${VERSION} em 3 arquivos."
