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


def test_split_by_size(sample_multipage_path, tmp_output_dir):
    doc = fitz.open(str(sample_multipage_path))
    splitter = PDFSplitter()
    output_dir = tmp_output_dir / "split_size"
    result = splitter.split_by_size(doc, max_mb=0.005, output_dir=output_dir, base_name="sized")
    doc.close()
    assert result.success
    assert len(result.output_files) >= 1
    for f in result.output_files:
        assert f.exists()


def test_split_by_bookmarks_no_bookmarks(sample_multipage_path, tmp_output_dir):
    doc = fitz.open(str(sample_multipage_path))
    splitter = PDFSplitter()
    output_dir = tmp_output_dir / "split_bm"
    result = splitter.split_by_bookmarks(doc, output_dir=output_dir, base_name="bm")
    doc.close()
    assert not result.success
    assert "bookmark" in result.error.lower() or "toc" in result.error.lower()


def test_split_by_bookmarks_with_toc(tmp_output_dir):
    doc = fitz.open()
    for i in range(4):
        page = doc.new_page()
        page.insert_text((50, 100), f"Capitulo {i + 1}", fontsize=14)
    doc.set_toc([
        [1, "Capitulo 1", 1],
        [1, "Capitulo 2", 2],
        [1, "Capitulo 3", 3],
        [1, "Capitulo 4", 4],
    ])
    pdf_path = tmp_output_dir / "with_toc.pdf"
    doc.save(str(pdf_path))
    doc.close()

    doc = fitz.open(str(pdf_path))
    splitter = PDFSplitter()
    output_dir = tmp_output_dir / "split_toc"
    result = splitter.split_by_bookmarks(doc, output_dir=output_dir, base_name="toc")
    doc.close()
    assert result.success
    assert len(result.output_files) == 4
