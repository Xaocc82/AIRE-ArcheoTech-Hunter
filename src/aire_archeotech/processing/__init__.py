"""Deterministic interfaces for document-processing workers."""

from aire_archeotech.processing.base import (
    ExtractedText,
    ExtractionStatus,
    OcrEngine,
    PdfTextExtractor,
)

__all__ = ["ExtractedText", "ExtractionStatus", "OcrEngine", "PdfTextExtractor"]
