# Sprint 04 — Testes de Core

**Diretório:** `/home/andrefarias/Desenvolvimento/PDForge`
**Conta git:** `AndreBFarias` / `andre.dsbf@gmail.com`
**Pré-requisito:** Sprint 03 concluído e commitado. Todos os módulos `core/` existem.

Execute todas as tasks direto, sem criar task list, sem confirmar etapas, sem parar a não ser em erro real.

---

## Contexto

Módulos existentes em `core/`:
- `pdf_reader.py` — `PDFReader`, métodos: `get_info()`, `get_page_text(n)`, `get_page_image(n)`
- `pdf_editor.py` — `PDFEditor`, método: `replace_text(doc, pairs, output_path, case_sensitive)`
- `pdf_merger.py` — `PDFMerger.merge(entries, output_path)`
- `pdf_splitter.py` — `PDFSplitter.split_by_range(doc, ranges, output_dir, base_name)`
- `pdf_rotator.py` — `PDFRotator.rotate_all(doc, angle, output_path)`
- `pdf_compressor.py` — `PDFCompressor.analyze_content_type(doc)`, `.compress(doc, path, profile)`
- `document_classifier.py` — `DocumentClassifier.classify(doc)`

---

## Task 1 — Arquivos __init__.py

Criar arquivos vazios:
- `tests/__init__.py`
- `tests/core/__init__.py`
- `tests/utils/__init__.py`

---

## Task 2 — tests/conftest.py

Criar `tests/conftest.py`:

```python
import pytest
import fitz
from pathlib import Path


@pytest.fixture(scope="session")
def tmp_output_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("output")


@pytest.fixture(scope="session")
def sample_pdf_path(tmp_path_factory) -> Path:
    path = tmp_path_factory.mktemp("fixtures") / "sample.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Documento de teste PDForge.", fontsize=12)
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture(scope="session")
def sample_multipage_path(tmp_path_factory) -> Path:
    path = tmp_path_factory.mktemp("fixtures") / "multipage.pdf"
    doc = fitz.open()
    for i in range(5):
        page = doc.new_page()
        page.insert_text((50, 100), f"Pagina {i + 1} do documento de teste.", fontsize=12)
    doc.save(str(path))
    doc.close()
    return path


@pytest.fixture(scope="session")
def sample_pdf_doc(sample_pdf_path) -> fitz.Document:
    doc = fitz.open(str(sample_pdf_path))
    yield doc
    doc.close()
```

---

## Task 3 — tests/core/test_pdf_reader.py

```python
from pathlib import Path
import fitz
from core.pdf_reader import PDFReader


def test_get_info(sample_pdf_path):
    reader = PDFReader(sample_pdf_path)
    info = reader.get_info()
    assert info.page_count == 1
    assert info.file_size != ""
    reader.close()


def test_get_page_text(sample_pdf_path):
    reader = PDFReader(sample_pdf_path)
    text = reader.get_page_text(0)
    assert "PDForge" in text
    reader.close()


def test_get_page_image(sample_pdf_path):
    reader = PDFReader(sample_pdf_path)
    img_bytes = reader.get_page_image(0)
    assert isinstance(img_bytes, bytes)
    assert len(img_bytes) > 0
    reader.close()
```

---

## Task 4 — tests/core/test_pdf_editor.py

```python
from pathlib import Path
import fitz
from core.pdf_editor import PDFEditor


def test_replace_text(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    editor = PDFEditor()
    output = tmp_output_dir / "edited.pdf"
    result = editor.replace_text(doc, [("PDForge", "TestApp")], output, case_sensitive=False)
    doc.close()
    assert result.success
    assert output.exists()
    verify = fitz.open(str(output))
    text = verify[0].get_text()
    verify.close()
    assert "TestApp" in text
```

---

## Task 5 — tests/core/test_pdf_merger.py

```python
from pathlib import Path
import fitz
from core.pdf_merger import PDFMerger, MergeEntry


def test_merge_two_pdfs(sample_pdf_path, sample_multipage_path, tmp_output_dir):
    merger = PDFMerger()
    entries = [
        MergeEntry(path=sample_pdf_path),
        MergeEntry(path=sample_multipage_path),
    ]
    output = tmp_output_dir / "merged.pdf"
    result = merger.merge(entries, output)
    assert result.success
    assert result.total_pages == 6
    assert output.exists()
    assert len(result.sources) == 2
```

---

## Task 6 — tests/core/test_pdf_splitter.py

```python
from pathlib import Path
import fitz
from core.pdf_splitter import PDFSplitter


def test_split_by_range(sample_multipage_path, tmp_output_dir):
    doc = fitz.open(str(sample_multipage_path))
    splitter = PDFSplitter()
    result = splitter.split_by_range(
        doc, [(0, 1), (2, 4)], tmp_output_dir / "split", "doc"
    )
    doc.close()
    assert result.success
    assert len(result.output_files) == 2
    for f in result.output_files:
        assert f.exists()
```

---

## Task 7 — tests/core/test_pdf_rotator.py

```python
from pathlib import Path
import fitz
from core.pdf_rotator import PDFRotator


def test_rotate_all(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    rotator = PDFRotator()
    output = tmp_output_dir / "rotated.pdf"
    result = rotator.rotate_all(doc, 90, output)
    doc.close()
    assert result.success
    assert result.pages_rotated == 1
    assert output.exists()
    verify = fitz.open(str(output))
    assert verify[0].rotation == 90
    verify.close()


def test_rotate_invalid_angle(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    rotator = PDFRotator()
    output = tmp_output_dir / "rotated_invalid.pdf"
    result = rotator.rotate_all(doc, 45, output)
    doc.close()
    assert not result.success
    assert "45" in result.error
```

---

## Task 8 — tests/core/test_pdf_compressor.py

```python
import fitz
from core.pdf_compressor import PDFCompressor, PageContentType


def test_analyze_content_type(sample_pdf_path):
    doc = fitz.open(str(sample_pdf_path))
    compressor = PDFCompressor()
    content_type = compressor.analyze_content_type(doc)
    doc.close()
    assert isinstance(content_type, PageContentType)


def test_compress(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    compressor = PDFCompressor()
    output = tmp_output_dir / "compressed.pdf"
    result = compressor.compress(doc, output, profile="medio")
    doc.close()
    assert result.success
    assert output.exists()


def test_compress_invalid_profile(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    compressor = PDFCompressor()
    output = tmp_output_dir / "compressed_bad.pdf"
    result = compressor.compress(doc, output, profile="inexistente")
    doc.close()
    assert not result.success
```

---

## Task 9 — tests/core/test_document_classifier.py

```python
import fitz
from core.document_classifier import DocumentClassifier


def test_classify_heuristic_fallback(sample_pdf_path):
    doc = fitz.open(str(sample_pdf_path))
    classifier = DocumentClassifier()
    result = classifier.classify(doc)
    doc.close()
    assert result.method in ("ml", "heuristic")
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0


def test_classify_contrato():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "cláusula primeira — objeto do contrato entre contratante e contratado.")
    classifier = DocumentClassifier()
    result = classifier.classify(doc)
    doc.close()
    assert result.doc_type == "contrato"
    assert result.confidence > 0.0
```

---

## Commit final do sprint

```bash
git add tests/
git commit -m "test: infraestrutura de testes e cobertura dos módulos core"
```

**Próximo sprint:** `sprint-05.md`
