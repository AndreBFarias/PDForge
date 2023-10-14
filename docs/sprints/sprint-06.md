# Sprint 06 — Telas UI (merge, split, compress, signature, classifier) + page_batch

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`
**Pré-requisito:** Sprint 05 concluído e commitado.

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Contexto

Todas as telas ficam em `ui/screens/`. Padrão de referência: ler `ui/screens/page_editor.py` antes de começar.
Estrutura típica de tela:
- Herda `QWidget`
- Sinal `pdf_changed = pyqtSignal(Path)` (se aplicável)
- `__init__(use_gpu, parent)`, `_setup_ui()`, `refresh_state(pdf_path, output_dir)`
- Componentes: `SectionHeader`, `FilePathButton`, `QProgressBar`, `QLabel` status, botão de ação
- Worker em `self._worker`, conectado a `_on_progress`, `_on_finished`, `_on_error`
- `_on_error`: restaura botão, colore label em `DraculaTheme.RED`
- Assinatura filosófica no final

---

## Task 1 — ui/screens/page_merge.py

**Classe `PageMerge(QWidget)`**:
- Sinal: `pdf_changed = pyqtSignal(Path)`
- UI: `SectionHeader("Mesclar", "PDFs")` + `DragDropPDFList` (área de drag) +
  `FilePathButton` para arquivo de saída (modo file, filtro pdf) +
  `QProgressBar` + `QLabel` status + `QPushButton("MESCLAR")`
- Instrução de uso acima da lista: label "Arraste PDFs ou clique [+] para adicionar"
- Botão `[+ Adicionar PDF]` que abre `QFileDialog.getOpenFileNames()` para pdf,
  adiciona itens na lista via `_list.addItem(...)` com path em `UserRole`
- Botão `[Remover selecionado]`
- `_run()`:
  - Valida lista não vazia e output path definido
  - Instancia `MergeWorker(entries=_list.get_merge_entries(), output_path=...)`
  - `_on_finished`: mostra resultado (páginas totais, tamanho), emite `pdf_changed`

---

## Task 2 — ui/screens/page_split.py

**Classe `PageSplit(QWidget)`**:
- UI: `SectionHeader("Dividir", "PDF")` + `FilePathButton` para PDF de entrada (sinal emite `pdf_changed`) +
  `FilePathButton` para pasta de saída (modo dir) + `QTabWidget` com 3 abas

**Aba "Por Range"**:
- `QLineEdit` com placeholder `"0-2, 3-4, 5-9"` (páginas base 0, separadas por vírgula)
- Parse: split por vírgula, cada item split por `-`, converte para `tuple[int, int]`

**Aba "Por Tamanho"**:
- `QDoubleSpinBox` para tamanho máximo em MB (1.0–500.0, default 10.0)

**Aba "Por Marcadores"**:
- Só label explicativo: "Divide o PDF nos marcadores (TOC) de nível 1."

- `QProgressBar` + `QLabel` status + `QPushButton("DIVIDIR")`
- `_run()`: detecta aba ativa, instancia `SplitWorker` com mode adequado
- `_on_finished`: lista arquivos gerados no label de status

---

## Task 3 — ui/screens/page_compress.py

**Classe `PageCompress(QWidget)`**:
- UI: `SectionHeader("Comprimir", "PDF")` + `FilePathButton` (entrada) +
  `FilePathButton` (saída, modo file) + `QComboBox` perfil (Leve / Médio / Agressivo) +
  `QPushButton("ANALISAR")` + `QLabel` para estimativa +
  `QProgressBar` + `QPushButton("COMPRIMIR")`
- `_analyze()`: abre doc, chama `PDFCompressor().analyze_content_type()` e `get_compression_estimate()`,
  exibe no label: tipo detectado + estimativa de redução
- `_run()`: instancia `CompressWorker`, mapeia texto do combobox para chave do perfil
  ("Leve" → "leve", "Médio" → "medio", "Agressivo" → "agressivo")
- `_on_finished`: exibe `original_mb`, `compressed_size_mb`, `reduction_pct`

---

## Task 4 — ui/screens/page_signature.py

**Classe `PageSignature(QWidget)`**:
- UI: `SectionHeader("Assinaturas", "")` + `FilePathButton` (entrada) +
  `QPushButton("DETECTAR ASSINATURAS")` + `QListWidget` para regiões detectadas +
  `QPushButton("EXTRAIR SELECIONADA")` + `QPushButton("REINSERIR")` +
  `FilePathButton` para imagem de reinserção (filtro png/jpg) +
  `FilePathButton` para PDF de saída + `QLabel` status
- `_detect()`: instancia `SignatureWorker`; `_on_detect_finished(regions)`: popula lista
  com `f"Página {r.page_index + 1} — confiança {r.confidence:.0%}"`, armazena região em `UserRole`
- `_extract()`: pega item selecionado, define output path automático em temp dir,
  instancia `SignatureHandler().extract_signature()` diretamente (não precisa de worker — é rápido),
  exibe path no label, abre `QFileSystemWatcher` para monitorar mudanças no arquivo extraído
- `_reinsert()`: valida seleção + imagem + output, instancia `ReinsertWorker`

---

## Task 5 — ui/screens/page_classifier.py

**Classe `PageClassifier(QWidget)`**:
- UI: `SectionHeader("Classificar", "Documentos")` + radio buttons "Arquivo único" / "Pasta (lote)" +
  `FilePathButton` (muda entre file e dir conforme radio) +
  `QPushButton("CLASSIFICAR")` + `QTableWidget` com colunas: Arquivo, Tipo, Confiança, Método

- Modo único: instancia `ClassifyWorker(pdf_path)`; `_on_finished`: adiciona 1 linha na tabela
- Modo lote: para cada `.pdf` na pasta, instancia `ClassifyWorker` sequencialmente via fila,
  ou usa `DocumentClassifier().classify_batch()` diretamente em um worker genérico
- Cor da linha: verde se `confidence >= 0.7`, amarelo se `0.4–0.7`, vermelho se `< 0.4`
  (usando `item.setForeground(QColor(...))`)

---

## Task 6 — Atualizar ui/screens/page_batch.py

Ler o arquivo antes de editar. Adicionar ao dict `_OPERATIONS`:

```python
_OPERATIONS = {
    "Extrair Metadados": "metadata",
    "Aplicar OCR": "ocr",
    "Rotacionar 90°": "rotate_90",
    "Rotacionar 180°": "rotate_180",
    "Rotacionar 270°": "rotate_270",
}
```

Em `BatchWorker._build_operation()` (em `ui/workers.py`), adicionar os casos de rotação:

```python
if self._operation_name.startswith("rotate_"):
    angle = int(self._operation_name.split("_")[1])
    def _rotate_op(doc: fitz.Document, output_path: Path) -> str:
        from core.pdf_rotator import PDFRotator
        result = PDFRotator().rotate_all(doc, angle, output_path)
        return f"{result.pages_rotated} paginas rotacionadas {angle}°"
    return _rotate_op
```

---

## Commit final do sprint

```bash
git add ui/screens/page_merge.py ui/screens/page_split.py ui/screens/page_compress.py
git add ui/screens/page_signature.py ui/screens/page_classifier.py ui/screens/page_batch.py
git add ui/workers.py
git commit -m "feat: telas de merge, split, compressão, assinaturas e classificação; rotação no lote"
```

**Próximo sprint:** `sprint-07.md`
