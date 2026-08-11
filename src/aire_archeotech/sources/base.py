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
    requested_url: str
    final_url: str
    status_code: int
    retrieved_at: datetime
    body: bytes
    content_type: str
    body_complete: bool = True
    limit_exceeded: bool = False
    bytes_read: int = 0


@dataclass(frozen=True)
class SourceAccessEvidence:
    source_code: str
    adapter_version: str
    requested_url: str
    final_url: str
    request_method: str
    request_content_type: str
    request_byte_size: int
    status_code: int
    retrieved_at: datetime
    terms_reference: str
    rights_reference: str
    request_sha256: str
    raw_response_sha256: str
    response_byte_size: int
    content_type: str
    transport_bytes_read: int
    body_complete: bool
    limit_exceeded: bool


class SourceSearchFailure(ValueError):
    """A rejected source attempt whose stored evidence remains inspectable."""

    def __init__(
        self,
        message: str,
        *,
        access: SourceAccessEvidence,
        raw_request: StoredBlob,
        raw_response: StoredBlob,
    ) -> None:
        super().__init__(message)
        self.access = access
        self.raw_request = raw_request
        self.raw_response = raw_response


class SourceTransportFailure(RuntimeError):
    """A transport failure after the request body was stored, with no response to preserve."""

    state = "REQUEST_STORED_NO_RESPONSE"

    def __init__(self, message: str, *, raw_request: StoredBlob) -> None:
        super().__init__(message)
        self.raw_request = raw_request


@dataclass(frozen=True)
class SourceSearchResult:
    hits: tuple[SourceHit, ...]
    access: SourceAccessEvidence
    raw_request: StoredBlob
    raw_response: StoredBlob


@dataclass(frozen=True)
class NormalizedSourceRecord:
    source_code: str
    external_id: str
    title: str
    canonical_reference: str
    description: str = ""


class SourceAdapter(Protocol):
    @property
    def code(self) -> str: ...

    def search(self, query: SourceQuery) -> SourceSearchResult: ...

    def fetch_record(self, external_id: str) -> NormalizedSourceRecord: ...
