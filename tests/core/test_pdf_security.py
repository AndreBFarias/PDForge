from pathlib import Path

import fitz

from core.pdf_security import PDFSecurity, SecurityResult


def test_encrypt_pdf(sample_pdf_path, tmp_output_dir):
    security = PDFSecurity()
    output = tmp_output_dir / "encrypted.pdf"
    result = security.encrypt(sample_pdf_path, output, user_password="teste123")
    assert result.success
    assert output.exists()
    doc = fitz.open(str(output))
    assert doc.is_encrypted
    doc.close()


def test_decrypt_pdf(sample_pdf_path, tmp_output_dir):
    security = PDFSecurity()
    encrypted = tmp_output_dir / "enc_for_dec.pdf"
    security.encrypt(sample_pdf_path, encrypted, user_password="abc")
    decrypted = tmp_output_dir / "decrypted.pdf"
    result = security.decrypt(encrypted, decrypted, password="abc")
    assert result.success
    assert decrypted.exists()
    doc = fitz.open(str(decrypted))
    assert not doc.is_encrypted
    doc.close()


def test_check_encryption_unencrypted(sample_pdf_path):
    security = PDFSecurity()
    result = security.check_encryption(sample_pdf_path)
    assert result.success
    assert not result.is_encrypted
    assert result.permissions is not None


def test_encrypt_with_permissions(sample_pdf_path, tmp_output_dir):
    security = PDFSecurity()
    output = tmp_output_dir / "perm_enc.pdf"
    result = security.encrypt(
        sample_pdf_path, output,
        user_password="test",
        permissions=fitz.PDF_PERM_PRINT,
    )
    assert result.success
    assert output.exists()


def test_decrypt_wrong_password(sample_pdf_path, tmp_output_dir):
    security = PDFSecurity()
    encrypted = tmp_output_dir / "enc_wrong.pdf"
    security.encrypt(sample_pdf_path, encrypted, user_password="correto")
    decrypted = tmp_output_dir / "dec_wrong.pdf"
    result = security.decrypt(encrypted, decrypted, password="errado")
    assert not result.success
    assert "incorreta" in result.error.lower() or "senha" in result.error.lower()


# "Nenhum homem é livre se não é senhor de si mesmo." -- Epicteto
