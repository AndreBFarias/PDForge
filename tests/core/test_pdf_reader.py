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
