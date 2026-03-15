import fitz

from core.metadata import Metadata, PDFMetadata


def test_read_metadata(sample_pdf_path):
    doc = fitz.open(str(sample_pdf_path))
    reader = PDFMetadata()
    meta = reader.read(doc)
    doc.close()
    assert isinstance(meta, Metadata)
    assert isinstance(meta.title, str)
    assert isinstance(meta.author, str)


def test_write_metadata(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    handler = PDFMetadata()
    output = tmp_output_dir / "meta_write.pdf"
    meta = Metadata(title="Teste PDForge", author="Autor Teste")
    handler.write(doc, meta, output)
    doc.close()

    verify = fitz.open(str(output))
    result = handler.read(verify)
    verify.close()
    assert result.title == "Teste PDForge"
    assert result.author == "Autor Teste"


def test_read_metadata_empty_pdf(tmp_output_dir):
    path = tmp_output_dir / "empty_meta.pdf"
    doc = fitz.open()
    doc.new_page()
    doc.save(str(path))
    doc.close()

    doc = fitz.open(str(path))
    handler = PDFMetadata()
    meta = handler.read(doc)
    doc.close()
    display = meta.as_display_dict()
    assert "title" not in display or display.get("title") == ""


def test_clear_metadata(sample_pdf_path, tmp_output_dir):
    doc = fitz.open(str(sample_pdf_path))
    handler = PDFMetadata()
    output_set = tmp_output_dir / "meta_set.pdf"
    handler.write(doc, Metadata(title="Titulo", author="Autor"), output_set)
    doc.close()

    doc2 = fitz.open(str(output_set))
    output_clear = tmp_output_dir / "meta_clear.pdf"
    handler.clear(doc2, output_clear)
    doc2.close()

    doc3 = fitz.open(str(output_clear))
    result = handler.read(doc3)
    doc3.close()
    assert result.title == ""
    assert result.author == ""
