import logging
from dataclasses import dataclass
from pathlib import Path

import fitz

logger = logging.getLogger("pdfforge.security")


@dataclass
class SecurityResult:
    success: bool = True
    output_path: Path | None = None
    is_encrypted: bool = False
    permissions: dict[str, bool] | None = None
    error: str = ""


class PDFSecurity:
    """Encriptação e decriptação de PDFs via PyMuPDF (AES-256)."""

    def encrypt(
        self,
        input_path: Path,
        output_path: Path,
        user_password: str,
        owner_password: str | None = None,
        permissions: int = fitz.PDF_PERM_PRINT | fitz.PDF_PERM_COPY | fitz.PDF_PERM_ANNOTATE,
    ) -> SecurityResult:
        try:
            doc = fitz.open(str(input_path))
            owner_pw = owner_password or user_password
            doc.save(
                str(output_path),
                encryption=fitz.PDF_ENCRYPT_AES_256,
                user_pw=user_password,
                owner_pw=owner_pw,
                permissions=permissions,
            )
            doc.close()
            logger.info("PDF encriptado com AES-256: %s", output_path.name)
            return SecurityResult(output_path=output_path)
        except Exception as exc:
            logger.error("Erro ao encriptar: %s", exc)
            return SecurityResult(success=False, error=str(exc))

    def decrypt(
        self,
        input_path: Path,
        output_path: Path,
        password: str,
    ) -> SecurityResult:
        try:
            doc = fitz.open(str(input_path))
            if not doc.is_encrypted:
                doc.close()
                return SecurityResult(
                    success=False,
                    error="PDF não está encriptado",
                )
            if not doc.authenticate(password):
                doc.close()
                return SecurityResult(
                    success=False,
                    error="Senha incorreta",
                )
            doc.save(str(output_path))
            doc.close()
            logger.info("PDF decriptado: %s", output_path.name)
            return SecurityResult(output_path=output_path)
        except Exception as exc:
            logger.error("Erro ao decriptar: %s", exc)
            return SecurityResult(success=False, error=str(exc))

    def check_encryption(self, input_path: Path) -> SecurityResult:
        try:
            doc = fitz.open(str(input_path))
            encrypted = doc.is_encrypted
            perms = None
            if not encrypted:
                perms = {
                    "print": bool(doc.permissions & fitz.PDF_PERM_PRINT),
                    "modify": bool(doc.permissions & fitz.PDF_PERM_MODIFY),
                    "copy": bool(doc.permissions & fitz.PDF_PERM_COPY),
                    "annotate": bool(doc.permissions & fitz.PDF_PERM_ANNOTATE),
                }
            doc.close()
            return SecurityResult(
                is_encrypted=encrypted,
                permissions=perms,
            )
        except Exception as exc:
            logger.error("Erro ao verificar encriptação: %s", exc)
            return SecurityResult(success=False, error=str(exc))


# "A liberdade consiste em fazer tudo o que não prejudica o outro." -- Montesquieu
