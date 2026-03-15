import fitz

from core.pdf_image_converter import PDFImageConverter


def test_pdf_to_png(sample_pdf_path, tmp_output_dir):
    converter = PDFImageConverter()
    output_dir = tmp_output_dir / "img_png"
    result = converter.pdf_to_images(
        sample_pdf_path,
        output_dir,
        fmt="png",
    )
    assert result.success
    assert result.total_pages == 1
    assert len(result.output_paths) == 1
    assert result.output_paths[0].suffix == ".png"
    assert result.output_paths[0].exists()


def test_pdf_to_jpeg(sample_pdf_path, tmp_output_dir):
    converter = PDFImageConverter()
    output_dir = tmp_output_dir / "img_jpg"
    result = converter.pdf_to_images(
        sample_pdf_path,
        output_dir,
        fmt="jpeg",
    )
    assert result.success
    assert result.output_paths[0].suffix == ".jpeg"


def test_images_to_pdf(sample_pdf_path, tmp_output_dir):
    converter = PDFImageConverter()
    img_dir = tmp_output_dir / "img_src"
    converter.pdf_to_images(
        sample_pdf_path,
        img_dir,
        fmt="png",
    )

    images = sorted(img_dir.glob("*.png"))
    output = tmp_output_dir / "from_images.pdf"
    result = converter.images_to_pdf(images, output)
    assert result.success
    assert output.exists()
    doc = fitz.open(str(output))
    assert len(doc) == len(images)
    doc.close()


def test_pdf_to_images_specific_pages(
    sample_multipage_path,
    tmp_output_dir,
):
    converter = PDFImageConverter()
    output_dir = tmp_output_dir / "img_pages"
    result = converter.pdf_to_images(
        sample_multipage_path,
        output_dir,
        pages=[0, 2, 4],
    )
    assert result.success
    assert result.total_pages == 3


def test_images_to_pdf_empty_list(tmp_output_dir):
    converter = PDFImageConverter()
    output = tmp_output_dir / "empty.pdf"
    result = converter.images_to_pdf([], output)
    assert not result.success
    assert "vazia" in result.error.lower()


# "Uma imagem vale mais que mil palavras." -- Fred R. Barnard
