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
