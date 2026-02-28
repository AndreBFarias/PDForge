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
