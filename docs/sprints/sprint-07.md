# Sprint 07 — Main Window + Scripts de Instalação + Documentação

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`
**Pré-requisito:** Sprint 06 concluído e commitado.

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Task 1 — Atualizar ui/main_window.py

Ler o arquivo completo antes de editar. As mudanças são:

**1. Novos imports** (adicionar aos imports existentes):
```python
from ui.screens.page_merge import PageMerge
from ui.screens.page_split import PageSplit
from ui.screens.page_compress import PageCompress
from ui.screens.page_signature import PageSignature
from ui.screens.page_classifier import PageClassifier
from ui.widgets.pdf_page_viewer import PDFPageViewer
```

**2. `_SIDEBAR_ITEMS`** — substituir a lista existente por:
```python
_SIDEBAR_ITEMS = [
    "Editor",
    "Analisador",
    "OCR",
    "Mesclar",
    "Dividir",
    "Comprimir",
    "Assinaturas",
    "Classificar",
    "Lote",
]
```

**3. `__init__`** — substituir `self.setFixedSize(1300, 800)` por:
```python
self.setMinimumSize(1300, 800)
self.resize(1400, 860)
```

**4. `_setup_content()`** — adicionar as 5 novas telas:
```python
self._page_merge = PageMerge(use_gpu=self._use_gpu)
self._page_split = PageSplit(use_gpu=self._use_gpu)
self._page_compress = PageCompress(use_gpu=self._use_gpu)
self._page_signature = PageSignature(use_gpu=self._use_gpu)
self._page_classifier = PageClassifier(use_gpu=self._use_gpu)

self._stack.addWidget(self._page_merge)      # índice 3
self._stack.addWidget(self._page_split)      # índice 4
self._stack.addWidget(self._page_compress)   # índice 5
self._stack.addWidget(self._page_signature)  # índice 6
self._stack.addWidget(self._page_classifier) # índice 7
# _page_batch já existia no índice 3, agora passa para índice 8
```

Atenção: a ordem de `addWidget` deve corresponder à ordem de `_SIDEBAR_ITEMS`.
`_page_batch` deve ser o último adicionado (índice 8 = "Lote").

Também conectar `pdf_changed` nas novas telas que o possuírem:
```python
for page in (self._page_merge, self._page_split):
    page.pdf_changed.connect(self._load_pdf)
```

**5. `_setup_preview()`** — substituir o bloco do `QPlainTextEdit` por `PDFPageViewer`:
- Remover: `self._preview_text = QPlainTextEdit()` e tudo que o envolve (label "Texto da página", imports não mais necessários)
- Substituir por:
```python
self._pdf_viewer = PDFPageViewer()
self._pdf_viewer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
vbox.addWidget(self._pdf_viewer)
```
- Remover os botões de navegação manuais `_btn_prev`, `_btn_next`, `_lbl_page_nav` — o PDFPageViewer já tem navegação interna

**6. `_load_pdf()`** — substituir `self._update_page_preview()` por:
```python
self._pdf_viewer.load_document(path)
```

**7. `_refresh_all_pages()`** — adicionar as novas telas:
```python
for page in (
    self._page_editor, self._page_analyzer, self._page_ocr, self._page_batch,
    self._page_merge, self._page_split, self._page_compress,
    self._page_signature, self._page_classifier,
):
    page.refresh_state(self._current_pdf, self._output_dir)
```

Remover métodos que não são mais necessários: `_update_page_preview`, `_prev_page`, `_next_page`.

---

## Task 2 — install.sh

Criar `install.sh` com `chmod +x install.sh` após criar:

```bash
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
```

---

## Task 3 — uninstall.sh

Criar `uninstall.sh` com `chmod +x uninstall.sh` após criar:

```bash
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
```

---

## Task 4 — README.md

Criar `README.md`:

```markdown
# PDForge

[![CI](https://github.com/AndreBFarias/PDForge/actions/workflows/ci.yml/badge.svg)](https://github.com/AndreBFarias/PDForge/actions/workflows/ci.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)

Editor de PDF para Linux com interface Qt6 e recursos de ML.

## Funcionalidades

- Substituição de texto com suporte a regex
- OCR com EasyOCR (GPU/CPU automático)
- Mesclar múltiplos PDFs com drag-and-drop
- Dividir por range de páginas, tamanho ou marcadores
- Compressão inteligente com análise de conteúdo (3 perfis)
- Detecção e edição de assinaturas via visão computacional
- Classificação automática de documentos (ML + heurística PT-BR)
- Visualizador inline de páginas com zoom
- Processamento em lote

## Instalação

### Dependências

Python 3.10+ e as bibliotecas do sistema são instaladas automaticamente pelo script.

### Instalação rápida

```bash
git clone https://github.com/AndreBFarias/PDForge.git
cd PDForge
bash install.sh
```

Após a instalação, execute `pdfforge` no terminal ou pelo launcher do sistema.

### Ambiente de desenvolvimento

```bash
make dev
make test
make lint
```

## Uso via CLI

```bash
pdfforge --help
pdfforge arquivo.pdf
pdfforge --batch /pasta/pdfs --output /saida --debug
```

## Desinstalar

```bash
bash uninstall.sh
```

## Licença

GPL-3.0 — veja [LICENSE](LICENSE).
```

---

## Task 5 — Documentação em docs/

Criar `docs/guides/installation.md`, `docs/guides/features.md`, `docs/plans/architecture_v1.md`.

**`docs/guides/installation.md`**: passos detalhados de instalação, requisitos de sistema (Ubuntu 22.04+, Python 3.10+, GPU opcional), instalação manual sem o script, variáveis de ambiente (`PDFFORGE_DEBUG=1`).

**`docs/guides/features.md`**: descrição de cada tela (Editor, Analisador, OCR, Mesclar, Dividir, Comprimir, Assinaturas, Classificar, Lote) com casos de uso e limitações conhecidas.

**`docs/plans/architecture_v1.md`**: diagrama textual da arquitetura em camadas:
- `core/` — lógica de domínio pura (sem UI)
- `ui/` — apresentação (PyQt6, workers em QThread)
- `config/` — singleton de configuração
- `utils/` — utilitários transversais
- Fluxo de dados: tela → worker → core → resultado → worker.finished → tela

---

## Commit final do sprint

```bash
chmod +x install.sh uninstall.sh
git add ui/main_window.py install.sh uninstall.sh README.md docs/
git commit -m "feat: atualiza main window com 9 telas, scripts de instalação e documentação"
```

**Próximo sprint:** `sprint-08.md`
