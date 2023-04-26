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
