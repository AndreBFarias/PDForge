# Sprint 12 — Conversão de Imagens (PDF <-> Imagens)

## Visão Estratégica

Conversão bidirecional entre PDF e imagens é uma das features mais solicitadas. O PDForge já possui `get_page_image()` interno em `pdf_reader.py` mas não o expõe ao usuário. Esta sprint cria a interface completa.

**Dependências:** Sprint 10 (base estável)
**Impacto:** Feature de alta demanda, habilita workflows com imagens
**Estimativa:** ~460 LOC novas, 3 arquivos novos, 2 arquivos modificados

## Contexto Técnico

### Capacidades existentes
- `pdf_reader.py:101` — `get_page_image()` retorna PNG bytes via `page.get_pixmap()`
- PyMuPDF suporta: `page.get_pixmap(matrix=fitz.Matrix(dpi/72, dpi/72))` para controle de DPI
- Formatos de saída: PNG, JPEG, TIFF, BMP

### Para images_to_pdf
- `fitz.open()` cria documento vazio
- `doc.new_page(width=img.width, height=img.height)` + `page.insert_image(rect, filename=path)`
- Pillow para detectar dimensões antes de criar página

## Tasks

### Task 12.1 — Criar core/pdf_image_converter.py (~180 LOC)

```python
@dataclass
class ConvertResult:
    success: bool
    output_paths: list[Path] = field(default_factory=list)
    total_pages: int = 0
    error: str = ""

class PDFImageConverter:
    def pdf_to_images(self, input_path, output_dir, format="png", dpi=150, pages=None) -> ConvertResult
    def images_to_pdf(self, image_paths, output_path, page_size="auto") -> ConvertResult
```

### Task 12.2 — Criar ui/screens/page_images.py (~200 LOC)

Layout com QTabWidget:
- Aba "PDF para Imagens":
  - FilePathButton (PDF)
  - FilePathButton (diretório de saída, mode="dir")
  - QComboBox formato (PNG, JPEG, TIFF)
  - QSpinBox DPI (72-600, default 150)
  - Botão "Converter"
- Aba "Imagens para PDF":
  - FilePathButton (múltiplas imagens, mode="image")
  - Lista de imagens selecionadas (drag-drop para reordenar)
  - FilePathButton (salvar PDF, mode="save")
  - Botão "Criar PDF"
- QProgressBar compartilhada

### Task 12.3 — Criar tests/core/test_pdf_image_converter.py (~80 LOC)

Testes:
1. `test_pdf_to_png` — converte PDF para PNGs e verifica quantidade
2. `test_pdf_to_jpeg` — converte para JPEG e verifica formato
3. `test_images_to_pdf` — cria PDF a partir de imagens e verifica páginas
4. `test_pdf_to_images_specific_pages` — converte apenas páginas selecionadas
5. `test_images_to_pdf_empty_list` — lista vazia retorna erro

### Task 12.4 — Adicionar ImageConvertWorker em ui/workers.py

Dois modos de operação (pdf_to_images e images_to_pdf) no mesmo worker.

### Task 12.5 — Integrar na sidebar em ui/main_window.py

- Adicionar "Imagens" na sidebar (após Segurança)
- Criar instância de PageImages no `_setup_content()`

## Verificação

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -v --tb=short
ruff check .
```

## Commit

```
feat: adiciona conversão bidirecional entre PDF e imagens
```
