# PDForge — Referência Rápida

## Visão Geral

Editor/manipulador de PDF para Linux com GUI PyQt6 e tema Dracula.
9 telas funcionais, ML para classificacao, OCR com CUDA, processamento em lote.

## Comandos

```bash
# Testes
python3 -m pytest tests/ -v --tb=short

# Validar sintaxe (sem PyQt6 disponível)
python3 -c "import ast, pathlib; [ast.parse(f.read_text()) for f in pathlib.Path('.').rglob('*.py')]"

# Executar
python3 main.py
python3 main.py --debug arquivo.pdf
python3 main.py --batch diretorio/
PDFFORGE_DEBUG=1 python3 main.py

# Lint
make lint

# Packaging
make package-deb
make package-appimage
make package-flatpak
```

## Arquitetura

```
PDForge/
  main.py              # Entry point CLI (click)
  config/
    settings.py        # Settings singleton, UserPreferences, constantes
  core/                # Lógica de negócio (sem dependência de UI)
    pdf_reader.py      # Leitura e inspeção
    pdf_editor.py      # Edição de texto (busca/substituição)
    pdf_merger.py      # Mesclagem de PDFs
    pdf_splitter.py    # Divisão (range, tamanho, bookmarks)
    pdf_rotator.py     # Rotação de páginas
    pdf_compressor.py  # Compressão com perfis (leve/médio/agressivo)
    signature_handler.py # Detecção e reinserção de assinaturas
    document_classifier.py # Classificacao ML + heuristica
    ocr_engine.py      # OCR via EasyOCR com CUDA
    metadata.py        # Leitura/escrita de metadados
    batch_processor.py # Processamento em lote
    font_detector.py   # Deteccao de fontes
  ui/
    main_window.py     # Janela principal com sidebar + stacked pages
    styles.py          # DraculaTheme (stylesheet global)
    components.py      # Componentes reutilizáveis
    workers.py         # QThread workers (sinais: finished, progress, error)
    widgets/
      pdf_page_viewer.py # Viewer inline de páginas PDF
    screens/           # 9 telas: editor, merge, split, compress, etc.
  utils/
    file_utils.py      # setup_logging, validação, helpers
    gpu_utils.py       # GPUMonitor com fallback CPU
    font_matcher.py    # Identificacao de familias tipograficas
  tests/               # pytest (13 testes)
  packaging/           # .deb, AppImage, Flatpak
```

## Convencoes

- **Logger**: `logging.getLogger("pdfforge.submodulo")` — hierarquia sob `pdfforge`
- **Workers**: QThread com sinais `finished(object)`, `progress(int, int, str)`, `error(str)`
- **Resultados**: dataclasses com `success: bool` e `error: str`
- **Tema**: DraculaTheme em `ui/styles.py`
- **Assinatura**: todo arquivo Python termina com citação filosófica como comentário
- **Idioma**: commits, logs e mensagens em PT-BR com acentuação correta
- **Limite**: 800 linhas por arquivo

## Dependências Críticas

- `PyMuPDF` (fitz): manipulação de PDF
- `PyQt6`: interface gráfica
- `click`: CLI
- `easyocr` (opcional): OCR com CUDA
- `opencv-python` (opcional): compressão de imagens e detecção de assinaturas
- `joblib` (opcional): modelo ML de classificação

## Validação sem PyQt6

O ambiente pode não ter PyQt6 disponível. Usar `ast.parse()` para validar sintaxe.
Testes rodam com `QT_QPA_PLATFORM=offscreen`.
