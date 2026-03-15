import fitz

from core.pdf_page_organizer import PDFPageOrganizer


def test_reorder_pages(
    sample_multipage_path,
    tmp_output_dir,
):
    organizer = PDFPageOrganizer()
    output = tmp_output_dir / "reordered.pdf"
    result = organizer.reorder(
        sample_multipage_path,
        output,
        [4, 3, 2, 1, 0],
    )
    assert result.success
    assert result.total_pages == 5
    assert output.exists()
    doc = fitz.open(str(output))
    text_first = doc[0].get_text()
    doc.close()
    assert "5" in text_first


def test_delete_page(
    sample_multipage_path,
    tmp_output_dir,
):
    organizer = PDFPageOrganizer()
    output = tmp_output_dir / "deleted.pdf"
    result = organizer.delete_pages(
        sample_multipage_path,
        output,
        [0, 2],
    )
    assert result.success
    assert result.total_pages == 3


def test_duplicate_page(
    sample_multipage_path,
    tmp_output_dir,
):
    organizer = PDFPageOrganizer()
    output = tmp_output_dir / "duplicated.pdf"
    result = organizer.duplicate_page(
        sample_multipage_path,
        output,
        0,
    )
    assert result.success
    assert result.total_pages == 6


def test_reorder_invalid_index(
    sample_multipage_path,
    tmp_output_dir,
):
    organizer = PDFPageOrganizer()
    output = tmp_output_dir / "invalid.pdf"
    result = organizer.reorder(
        sample_multipage_path,
        output,
        [0, 1, 99],
    )
    assert not result.success
    assert "nv" in result.error.lower()


def test_get_thumbnails(sample_multipage_path):
    organizer = PDFPageOrganizer()
    thumbs = organizer.get_page_thumbnails(
        sample_multipage_path,
    )
    assert len(thumbs) == 5
    for t in thumbs:
        assert isinstance(t, bytes)
        assert len(t) > 0
