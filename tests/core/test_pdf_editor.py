from pathlib import Path
import fitz
from core.pdf_editor import PDFEditor


def test_replace_text(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    editor = PDFEditor()
    output = tmp_output_dir / "edited.pdf"
    result = editor.replace_text(doc, [("PDForge", "TestApp")], output, case_sensitive=False)
    doc.close()
    assert output.exists()
    assert result.total_replacements >= 0
    verify = fitz.open(str(output))
    text = verify[0].get_text()
    verify.close()
    assert "TestApp" in text


def test_replace_multiple_terms(tmp_output_dir):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Gato e Cachorro", fontsize=12)
    output = tmp_output_dir / "multi_replace.pdf"
    editor = PDFEditor()
    result = editor.replace_text(
        doc, [("Gato", "Felino"), ("Cachorro", "Canino")], output, case_sensitive=False
    )
    doc.close()
    assert result.total_replacements >= 2
    verify = fitz.open(str(output))
    text = verify[0].get_text()
    verify.close()
    assert "Felino" in text
    assert "Canino" in text


def test_replace_case_sensitive(tmp_output_dir):
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "Python python PYTHON", fontsize=12)
    output = tmp_output_dir / "case_replace.pdf"
    editor = PDFEditor()
    result = editor.replace_text(
        doc, [("Python", "Java")], output, case_sensitive=True
    )
    doc.close()
    assert output.exists()


def test_replace_no_match(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    editor = PDFEditor()
    output = tmp_output_dir / "no_match.pdf"
    result = editor.replace_text(
        doc, [("INEXISTENTE_XYZ", "Nada")], output, case_sensitive=False
    )
    doc.close()
    assert result.total_replacements == 0
