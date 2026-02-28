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
