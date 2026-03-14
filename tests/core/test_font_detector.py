import fitz

from core.font_detector import FontDetector, FontUsage


def test_detect_fonts(sample_pdf_path):
    doc = fitz.open(str(sample_pdf_path))
    detector = FontDetector()
    usages = detector.extract(doc)
    doc.close()
    assert isinstance(usages, list)
    assert len(usages) > 0
    for usage in usages:
        assert isinstance(usage, FontUsage)
        assert usage.occurrences > 0


def test_detect_fonts_empty():
    doc = fitz.open()
    doc.new_page()
    detector = FontDetector()
    usages = detector.extract(doc)
    doc.close()
    assert usages == []


def test_get_dominant_font(sample_pdf_path):
    doc = fitz.open(str(sample_pdf_path))
    detector = FontDetector()
    dominant = detector.get_dominant_font(doc)
    doc.close()
    assert dominant is not None
    assert isinstance(dominant, FontUsage)
    assert dominant.occurrences > 0


def test_get_dominant_font_empty():
    doc = fitz.open()
    doc.new_page()
    detector = FontDetector()
    dominant = detector.get_dominant_font(doc)
    doc.close()
    assert dominant is None


def test_font_usage_properties(sample_pdf_path):
    doc = fitz.open(str(sample_pdf_path))
    detector = FontDetector()
    usages = detector.extract(doc)
    doc.close()
    if usages:
        usage = usages[0]
        assert usage.avg_size > 0
        lo, hi = usage.size_range
        assert lo <= hi
        assert len(usage.pages) > 0
