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
