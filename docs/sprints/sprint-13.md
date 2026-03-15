# Sprint 13 — Marca d'Agua (Texto e Imagem)

## Visão Estratégica

Marca d'água é essencial para proteção de propriedade intelectual e identificação de documentos confidenciais. A implementação suporta tanto texto (ex: "CONFIDENCIAL", "RASCUNHO") quanto imagem (ex: logo da empresa).

**Dependências:** Sprint 10 (base estável)
**Impacto:** Feature de alta demanda corporativa
**Estimativa:** ~480 LOC novas, 3 arquivos novos, 3 arquivos modificados

## Contexto Técnico

### Abordagem para opacidade
PyMuPDF não suporta opacidade direta em `insert_text()`. A abordagem recomendada:
1. **Texto:** Gerar PNG semi-transparente via Pillow em memória, inserir com `insert_image()`
2. **Imagem:** Usar Pillow para ajustar opacidade da imagem, inserir com `insert_image()`
3. Alternativa: usar `page.insert_htmlbox()` com CSS opacity (PyMuPDF 1.23+)

### Rotação
- `fitz.Matrix` com `prerotate()` para texto rotacionado
- Posições: centro, diagonal, canto superior/inferior, repetição em grade

## Tasks

### Task 13.1 — Criar core/pdf_watermark.py (~180 LOC)

```python
@dataclass
class WatermarkConfig:
    text: str = ""
    image_path: Path | None = None
    font_size: int = 48
    color: tuple[int, int, int] = (128, 128, 128)
    opacity: float = 0.3
    rotation: float = -45.0
    position: str = "center"  # center, diagonal, tile

@dataclass
class WatermarkResult:
    success: bool
    output_path: Path | None = None
    pages_processed: int = 0
    error: str = ""

class PDFWatermark:
    def apply_text(self, input_path, output_path, config: WatermarkConfig) -> WatermarkResult
    def apply_image(self, input_path, output_path, image_path, opacity=0.3, position="center", scale=1.0) -> WatermarkResult
    def _create_text_overlay(self, text, width, height, config) -> bytes  # PNG bytes via Pillow
    def _create_image_overlay(self, image_path, width, height, opacity, scale) -> bytes
```

### Task 13.2 — Criar ui/screens/page_watermark.py (~220 LOC)

Layout com QTabWidget:
- Aba "Texto":
  - FilePathButton (PDF)
  - QLineEdit para texto da marca
  - QSpinBox font_size (12-200, default 48)
  - QComboBox posição (Centro, Diagonal, Repetição)
  - QSlider opacidade (0-100%, default 30%)
  - QSpinBox rotação (-180 a 180, default -45)
  - QPushButton cor (abre QColorDialog)
  - Botão "Aplicar"
- Aba "Imagem":
  - FilePathButton (PDF)
  - FilePathButton (imagem, mode="image")
  - QComboBox posição
  - QSlider opacidade
  - QDoubleSpinBox escala (0.1-3.0, default 1.0)
  - Botão "Aplicar"
- QProgressBar compartilhada

### Task 13.3 — Criar tests/core/test_pdf_watermark.py (~80 LOC)

Testes:
1. `test_apply_text_watermark` — aplica texto e verifica que PDF foi gerado
2. `test_apply_image_watermark` — aplica imagem e verifica
3. `test_watermark_diagonal` — posição diagonal
4. `test_watermark_tile` — repetição em grade
5. `test_watermark_opacity` — opacidade aplicada corretamente

### Task 13.4 — Adicionar WatermarkWorker em ui/workers.py

Dois modos: texto e imagem. Config passada no construtor.

### Task 13.5 — Integrar na sidebar em ui/main_window.py

- Adicionar "Marca d'Água" na sidebar
- Criar instância de PageWatermark no `_setup_content()`

## Verificação

```bash
QT_QPA_PLATFORM=offscreen python3 -m pytest tests/ -v --tb=short
ruff check .
```

## Commit

```
feat: adiciona marca d'agua com suporte a texto e imagem
```
