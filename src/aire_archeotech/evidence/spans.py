"""Exact archival evidence spans with physical source locators."""

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class EvidenceSpan:
    """A quoted statement tied to one original artifact and physical page."""

    source_url: str
    artifact_sha256: str
    document_reference: str
    page_number: int
    character_start: int
    character_end: int
    quote: str

    def __post_init__(self) -> None:
        parsed = urlparse(self.source_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source_url must be an absolute HTTP(S) URL")
        if len(self.artifact_sha256) != 64 or any(
            character not in "0123456789abcdef" for character in self.artifact_sha256
        ):
            raise ValueError("artifact_sha256 must be a lowercase SHA-256 digest")
        if not self.document_reference.strip():
            raise ValueError("document_reference must not be blank")
        if self.page_number < 1:
            raise ValueError("page_number must be positive")
        if self.character_start < 0 or self.character_end <= self.character_start:
            raise ValueError("character offsets must describe a non-empty range")
        if not self.quote:
            raise ValueError("quote must not be blank")

    @classmethod
    def from_page_text(
        cls,
        *,
        source_url: str,
        artifact_sha256: str,
        document_reference: str,
        page_number: int,
        page_text: str,
        start: int,
        end: int,
    ) -> "EvidenceSpan":
        """Create a span only when its offsets resolve to exact page text."""
        quote = page_text[start:end]
        if start < 0 or end > len(page_text) or end <= start:
            raise ValueError("evidence offsets are outside the supplied page text")
        return cls(
            source_url=source_url,
            artifact_sha256=artifact_sha256,
            document_reference=document_reference,
            page_number=page_number,
            character_start=start,
            character_end=end,
            quote=quote,
        )
