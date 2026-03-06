# Sprint 05 — UI Widgets + Workers

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`
**Pré-requisito:** Sprint 04 concluído e commitado.

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Contexto do codebase UI

- Theme: `DraculaTheme` de `ui/styles.py` — constantes: `BACKGROUND="#282a36"`, `SIDEBAR="#21222c"`,
  `PURPLE="#bd93f9"`, `GREEN="#50fa7b"`, `RED="#ff5555"`, `CYAN="#8be9fd"`, `COMMENT="#6272a4"`,
  `FOREGROUND="#f8f8f2"`, `CURRENT_LINE="#44475a"`
- Componentes reutilizáveis em `ui/components.py`: `Toast`, `FilePathButton`, `SectionHeader`
- Workers seguem o padrão de `OCRWorker` em `ui/workers.py`:
  `QThread` com sinais `finished = pyqtSignal(object)`, `progress = pyqtSignal(int, int, str)`, `error = pyqtSignal(str)`
- Criar `ui/widgets/__init__.py` vazio se não existir

---

## Task 1 — ui/widgets/pdf_page_viewer.py

Criar `ui/widgets/pdf_page_viewer.py`:

**Classe `PDFPageViewer(QWidget)`**:
- Sinais: `page_changed = pyqtSignal(int)`
- Atributos internos: `_doc: fitz.Document | None`, `_current_page: int`, `_scale: float`
- Layout: `QVBoxLayout` contendo `QScrollArea` com `QLabel` (imagem) + `QHBoxLayout` com botões de navegação

**`_setup_ui()`**:
- `QScrollArea` com `setWidgetResizable(True)`, fundo `DraculaTheme.BACKGROUND`
- `QLabel` para exibir a imagem, `setAlignment(AlignCenter)`, fundo `DraculaTheme.BACKGROUND`
- Barra de navegação: `QPushButton("< Anterior")`, `QLabel` para "pág N / total", `QPushButton("Próxima >")`,
  e botões de zoom `[−]` `[reset]` `[+]`

**Métodos públicos**:
- `load_document(path: Path) -> None`: abre doc com `fitz.open()`, vai para página 0, chama `_render()`
- `show_page(n: int) -> None`: valida índice, atualiza `_current_page`, chama `_render()`, emite `page_changed`
- `zoom_in()`: `_scale = min(_scale * 1.25, Settings.PDF_VIEWER_MAX_SCALE)`, re-renderiza
- `zoom_out()`: `_scale = max(_scale / 1.25, Settings.PDF_VIEWER_MIN_SCALE)`, re-renderiza
- `zoom_reset()`: `_scale = Settings.PDF_VIEWER_DEFAULT_SCALE`, re-renderiza

**`_render()`** (privado):
- Se `_doc` é None, limpa label e retorna
- `page = _doc[_current_page]`
- `mat = fitz.Matrix(_scale, _scale)`
- `pix = page.get_pixmap(matrix=mat)`
- `img_bytes = pix.tobytes("png")`
- Converte para `QImage` via `QImage.fromData(img_bytes)` → `QPixmap.fromImage(img)` → `label.setPixmap()`
- Atualiza label de navegação: `f"{_current_page + 1} / {_doc.page_count}"`
- Habilita/desabilita botões anterior/próximo

**`closeEvent`**: fecha `_doc` se aberto.

---

## Task 2 — ui/widgets/drag_drop_list.py

Criar `ui/widgets/drag_drop_list.py`:

**Classe `DragDropPDFList(QListWidget)`**:
- `items_reordered = pyqtSignal()`
- No `__init__`: `setDragDropMode(DragDropMode.InternalMove)`, `setAcceptDrops(True)`, `setDropIndicatorShown(True)`
- `dragEnterEvent`: aceita se `event.mimeData().hasUrls()`
- `dropEvent`: se URLs externas, filtra `.pdf`, abre com fitz para contar páginas,
  exibe item como `"nome.pdf  (N págs)"`, armazena `Path` em `item.setData(Qt.UserRole, path)`;
  se InternalMove, chama super e emite `items_reordered`
- `get_merge_entries() -> list[MergeEntry]`:
  - Itera `range(count())`, recupera path via `item.data(Qt.UserRole)`
  - Retorna lista de `MergeEntry(path=path)`
  - Import `MergeEntry` de `core.pdf_merger`

---

## Task 3 — Adicionar 6 workers a ui/workers.py

Ler `ui/workers.py` antes de editar. Adicionar ao final do arquivo (antes do comentário de assinatura) os 6 workers:

**`MergeWorker(QThread)`**:
- `__init__`: recebe `entries: list[MergeEntry]`, `output_path: Path`
- `run()`: instancia `PDFMerger()`, chama `merge(entries, output_path, on_progress=lambda c,t,n: self.progress.emit(c,t,n))`
- Sinais: `finished(object)` (MergeResult), `progress(int, int, str)`, `error(str)`

**`SplitWorker(QThread)`**:
- `__init__`: recebe `pdf_path: Path`, `mode: str` ("range"|"size"|"bookmarks"), `output_dir: Path`,
  `base_name: str`, `ranges: list[tuple[int,int]] | None = None`, `max_mb: float = 10.0`
- `run()`: abre doc, instancia `PDFSplitter()`, chama método adequado pelo `mode`
- Sinais: `finished(object)` (SplitResult), `error(str)`

**`CompressWorker(QThread)`**:
- `__init__`: recebe `pdf_path: Path`, `output_path: Path`, `profile: str`
- `run()`: abre doc, instancia `PDFCompressor()`, chama `compress()`
- Sinais: `finished(object)` (CompressResult), `error(str)`

**`SignatureWorker(QThread)`**:
- `__init__`: recebe `pdf_path: Path`
- `run()`: abre doc, instancia `SignatureHandler()`, chama `detect_signatures(doc)`
- `finished` emite `list[SignatureRegion]`
- Sinais: `finished(object)`, `error(str)`

**`ReinsertWorker(QThread)`**:
- `__init__`: recebe `pdf_path: Path`, `region: SignatureRegion`, `image_path: Path`, `output_path: Path`
- `run()`: abre doc, chama `SignatureHandler().reinsert_signature()`
- Sinais: `finished(bool)`, `error(str)`

**`ClassifyWorker(QThread)`**:
- `__init__`: recebe `pdf_path: Path`
- `run()`: abre doc com fitz, chama `DocumentClassifier().classify(doc)`
- Sinais: `finished(object)` (ClassificationResult), `error(str)`

Cada worker segue o mesmo padrão: `try/except`, `logger.error()` no except, `self.error.emit(str(exc))`.

Imports necessários no topo de workers.py (adicionar apenas os que faltam):
```python
from core.pdf_merger import PDFMerger, MergeEntry, MergeResult
from core.pdf_splitter import PDFSplitter, SplitResult
from core.pdf_rotator import PDFRotator
from core.pdf_compressor import PDFCompressor, CompressResult
from core.signature_handler import SignatureHandler, SignatureRegion
from core.document_classifier import DocumentClassifier, ClassificationResult
```

---

## Commit final do sprint

```bash
git add ui/widgets/ ui/workers.py
git commit -m "feat: widgets PDFPageViewer e DragDropPDFList, workers para novas funcionalidades"
```

**Próximo sprint:** `sprint-06.md`
