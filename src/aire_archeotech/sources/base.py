"""Stable abstractions for lawful, read-only archive adapters."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from aire_archeotech.storage.cas import StoredBlob

MAX_SOURCE_RECORDS = 100


@dataclass(frozen=True)
class SourceQuery:
    text: str
    max_records: int = 100

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("source queries must not be blank")
        if self.max_records < 1:
            raise ValueError("max_records must be positive")
        if self.max_records > MAX_SOURCE_RECORDS:
            raise ValueError(f"max_records must not exceed {MAX_SOURCE_RECORDS}")


@dataclass(frozen=True)
class SourceHit:
    external_id: str
    title: str
    canonical_reference: str


@dataclass(frozen=True)
class SourceTransportResponse:
    source_url: str
    status_code: int
    retrieved_at: datetime
    body: bytes


@dataclass(frozen=True)
class SourceAccessEvidence:
    source_url: str
    status_code: int
    retrieved_at: datetime
    terms_reference: str
    rights_reference: str
    raw_response_sha256: str
    response_byte_size: int


@dataclass(frozen=True)
class SourceSearchResult:
    hits: tuple[SourceHit, ...]
    access: SourceAccessEvidence
    raw_response: StoredBlob


@dataclass(frozen=True)
class NormalizedSourceRecord:
    source_code: str
    external_id: str
    title: str
    canonical_reference: str
    description: str = ""


class SourceAdapter(Protocol):
    code: str

    def search(self, query: SourceQuery) -> SourceSearchResult: ...

    def fetch_record(self, external_id: str) -> NormalizedSourceRecord: ...
