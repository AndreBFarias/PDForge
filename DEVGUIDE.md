# PDForge — Referencia Rapida

## Visao Geral

Editor/manipulador de PDF para Linux com GUI PyQt6 e tema Dracula.
9 telas funcionais, ML para classificacao, OCR com CUDA, processamento em lote.

## Comandos

```bash
# Testes
python3 -m pytest tests/ -v --tb=short

# Validar sintaxe (sem PyQt6 disponivel)
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
  core/                # Logica de negocio (sem dependencia de UI)
    pdf_reader.py      # Leitura e inspecao
    pdf_editor.py      # Edicao de texto (busca/substituicao)
    pdf_merger.py      # Mesclagem de PDFs
    pdf_splitter.py    # Divisao (range, tamanho, bookmarks)
    pdf_rotator.py     # Rotacao de paginas
    pdf_compressor.py  # Compressao com perfis (leve/medio/agressivo)
    signature_handler.py # Deteccao e reinsercao de assinaturas
    document_classifier.py # Classificacao ML + heuristica
    ocr_engine.py      # OCR via EasyOCR com CUDA
    metadata.py        # Leitura/escrita de metadados
    batch_processor.py # Processamento em lote
    font_detector.py   # Deteccao de fontes
  ui/
    main_window.py     # Janela principal com sidebar + stacked pages
    styles.py          # DraculaTheme (stylesheet global)
    components.py      # Componentes reutilizaveis
    workers.py         # QThread workers (sinais: finished, progress, error)
    widgets/
      pdf_page_viewer.py # Viewer inline de paginas PDF
    screens/           # 9 telas: editor, merge, split, compress, etc.
  utils/
    file_utils.py      # setup_logging, validacao, helpers
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
- **Assinatura**: todo arquivo Python termina com citacao filosofica como comentario
- **Idioma**: commits, logs e mensagens em PT-BR com acentuacao correta
- **Limite**: 800 linhas por arquivo

## Dependencias Criticas

- `PyMuPDF` (fitz): manipulacao de PDF
- `PyQt6`: interface grafica
- `click`: CLI
- `easyocr` (opcional): OCR com CUDA
- `opencv-python` (opcional): compressao de imagens e deteccao de assinaturas
- `joblib` (opcional): modelo ML de classificacao

## Validacao sem PyQt6

O ambiente pode nao ter PyQt6 disponivel. Usar `ast.parse()` para validar sintaxe.
Testes rodam com `QT_QPA_PLATFORM=offscreen`.
