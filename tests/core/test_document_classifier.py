import fitz
from core.document_classifier import DocumentClassifier


def test_classify_heuristic_fallback(sample_pdf_path):
    doc = fitz.open(str(sample_pdf_path))
    classifier = DocumentClassifier()
    result = classifier.classify(doc)
    doc.close()
    assert result.method in ("ml", "heuristic")
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0


def test_classify_contrato():
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 100), "cláusula primeira — objeto do contrato entre contratante e contratado.")
    classifier = DocumentClassifier()
    result = classifier.classify(doc)
    doc.close()
    assert result.doc_type == "contrato"
    assert result.confidence > 0.0
