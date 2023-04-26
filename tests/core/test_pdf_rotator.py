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
