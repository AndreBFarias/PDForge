# Sprint 14 — Reordenacao de Paginas com Thumbnails

## Visao Estrategica

Reordenacao visual de paginas e uma das features mais intuitivas e mais solicitadas. Diferente do merge (que trabalha com arquivos), esta feature opera nas paginas de um unico PDF com interface drag-and-drop de thumbnails.

**Dependencias:** Sprint 10 (base estavel)
**Impacto:** UX critica para usuarios que organizam documentos
**Estimativa:** ~680 LOC novas, 4 arquivos novos, 2 arquivos modificados

## Contexto Tecnico

### Diferenca do widget existente
- `DragDropPDFList` em `ui/widgets/drag_drop_list.py` e para **arquivos PDF** (merge)
- Para reordenacao precisamos de widget novo para **paginas de um PDF** (thumbnails)

### Geracao de thumbnails
- `page.get_pixmap(matrix=fitz.Matrix(0.3, 0.3))` gera thumbnail ~180px
- Converter para QPixmap via QImage para exibir no grid
- Cache de thumbnails em memoria para responsividade

### Operacoes de pagina
- `doc.move_page(from_idx, to_idx)` — reordena
- `doc.delete_page(idx)` — remove
- `doc.copy_page(idx)` — duplica (insere apos o original)
- `doc.select(page_list)` — seleciona subset de paginas na ordem especificada

## Tasks

### Task 14.1 — Criar core/pdf_page_organizer.py (~120 LOC)

```python
@dataclass
class ReorderResult:
    success: bool
    output_path: Path | None = None
    total_pages: int = 0
    error: str = ""

class PDFPageOrganizer:
    def reorder(self, input_path, output_path, new_order: list[int]) -> ReorderResult
    def delete_pages(self, input_path, output_path, pages_to_delete: list[int]) -> ReorderResult
    def duplicate_page(self, input_path, output_path, page_index: int) -> ReorderResult
    def get_page_thumbnails(self, input_path, scale=0.3) -> list[bytes]  # PNG bytes
```

### Task 14.2 — Criar ui/widgets/page_thumbnail_grid.py (~300 LOC)

Widget QScrollArea com grid de thumbnails:
- Cada thumbnail: QLabel com QPixmap + numero da pagina
- Drag-and-drop para reordenar (QDrag + dropEvent)
- Selecao multipla com Ctrl+Click
- Context menu: Duplicar, Deletar
- Signals: `order_changed(list[int])`, `pages_deleted(list[int])`, `page_duplicated(int)`

Implementacao:
- QGridLayout dentro de QScrollArea
- Cada item e um QFrame com QVBoxLayout (imagem + label)
- Drag via mouseMoveEvent + QDrag com QMimeData
- Drop via dragEnterEvent/dropEvent

### Task 14.3 — Criar ui/screens/page_organizer.py (~200 LOC)

Layout:
- SectionHeader "Organizar Paginas"
- FilePathButton para selecionar PDF
- PageThumbnailGrid (area principal)
- Barra de acoes: Salvar, Desfazer, Duplicar Selecionadas, Deletar Selecionadas
- QProgressBar para carregamento de thumbnails

### Task 14.4 — Criar tests/core/test_pdf_page_organizer.py (~60 LOC)

Testes:
1. `test_reorder_pages` — inverte ordem e verifica
2. `test_delete_page` — remove pagina e verifica contagem
3. `test_duplicate_page` — duplica e verifica contagem
4. `test_reorder_invalid_index` — indice invalido retorna erro

### Task 14.5 — Adicionar ReorderWorker em ui/workers.py

Worker para salvar resultado da reordenacao.

### Task 14.6 — Integrar na sidebar em ui/main_window.py

- Adicionar "Organizar" na sidebar
- Criar instancia de PageOrganizer no `_setup_content()`

## Verificacao

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -v --tb=short
ruff check .
```

## Commit

```
feat: adiciona reordenacao de paginas com thumbnails drag-and-drop
```
