"""Embedded-text extraction for PDF artifacts."""

from io import BytesIO

import pypdf
from pypdf import PdfReader

from aire_archeotech.processing.base import ExtractedText, ExtractionStatus


class PypdfTextExtractor:
    """Extract text already embedded in PDF pages without invoking OCR."""

    def extract(self, document: bytes) -> ExtractedText:
        """Return embedded PDF text or explicitly mark the document for OCR."""
        reader = PdfReader(BytesIO(document))
        text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
        status = ExtractionStatus.EXTRACTED if text else ExtractionStatus.OCR_REQUIRED
        return ExtractedText(
            text=text,
            status=status,
            engine="pypdf",
            engine_version=pypdf.__version__,
        )
