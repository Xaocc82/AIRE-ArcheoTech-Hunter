"""Stable contracts for text extraction and optional OCR engines."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol


class ExtractionStatus(StrEnum):
    """The result of attempting to obtain machine-readable document text."""

    EXTRACTED = "extracted"
    OCR_REQUIRED = "ocr_required"


@dataclass(frozen=True)
class ExtractedText:
    """Text and the specific engine that produced the result."""

    text: str
    status: ExtractionStatus
    engine: str
    engine_version: str


class PdfTextExtractor(Protocol):
    """Extract embedded text from a PDF document."""

    def extract(self, document: bytes) -> ExtractedText:
        """Return extracted text or an explicit OCR requirement."""


class OcrEngine(Protocol):
    """Recognize text in one already-rendered document page image."""

    def recognize_page(self, image: bytes) -> ExtractedText:
        """Return recognized page text and its engine provenance."""
