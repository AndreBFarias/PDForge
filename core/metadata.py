import logging
from pathlib import Path
from dataclasses import dataclass, asdict

import fitz

logger = logging.getLogger("pdfforge.metadata")

# Chaves suportadas pelo padrão PDF/PyMuPDF
METADATA_KEYS = ("title", "author", "subject", "keywords", "creator", "producer", "creationDate", "modDate")


@dataclass
class Metadata:
    title: str = ""
    author: str = ""
    subject: str = ""
    keywords: str = ""
    creator: str = ""
    producer: str = ""
    creation_date: str = ""
    mod_date: str = ""

    def to_fitz_dict(self) -> dict[str, str]:
        return {
            "title": self.title,
            "author": self.author,
            "subject": self.subject,
            "keywords": self.keywords,
            "creator": self.creator,
            "producer": self.producer,
            "creationDate": self.creation_date,
            "modDate": self.mod_date,
        }

    def as_display_dict(self) -> dict[str, str]:
        """Retorna apenas campos preenchidos, para exibição."""
        raw = asdict(self)
        return {k: v for k, v in raw.items() if v}


class PDFMetadata:
    """Lê e escreve metadados de PDFs via PyMuPDF."""

    def read(self, doc: fitz.Document) -> Metadata:
        raw = doc.metadata or {}
        return Metadata(
            title=raw.get("title", ""),
            author=raw.get("author", ""),
            subject=raw.get("subject", ""),
            keywords=raw.get("keywords", ""),
            creator=raw.get("creator", ""),
            producer=raw.get("producer", ""),
            creation_date=raw.get("creationDate", ""),
            mod_date=raw.get("modDate", ""),
        )

    def write(self, doc: fitz.Document, metadata: Metadata, output_path: Path) -> None:
        """
        Escreve metadados no documento e salva em output_path.
        Não modifica o arquivo original.
        """
        doc.set_metadata(metadata.to_fitz_dict())
        doc.save(str(output_path), garbage=4, deflate=True)
        logger.info(
            "Metadados escritos em %s (título: '%s', autor: '%s')",
            output_path.name,
            metadata.title,
            metadata.author,
        )

    def clear(self, doc: fitz.Document, output_path: Path) -> None:
        """Remove todos os metadados do documento."""
        empty = Metadata()
        self.write(doc, empty, output_path)
        logger.info("Metadados removidos: %s", output_path.name)
