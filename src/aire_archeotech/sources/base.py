"""Stable abstractions for lawful, read-only archive adapters."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class SourceQuery:
    text: str
    max_records: int = 100

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValueError("source queries must not be blank")
        if self.max_records < 1:
            raise ValueError("max_records must be positive")


@dataclass(frozen=True)
class SourceHit:
    external_id: str
    title: str
    canonical_reference: str


@dataclass(frozen=True)
class NormalizedSourceRecord:
    source_code: str
    external_id: str
    title: str
    canonical_reference: str
    description: str = ""


class SourceAdapter(Protocol):
    code: str

    def search(self, query: SourceQuery) -> tuple[SourceHit, ...]: ...

    def fetch_record(self, external_id: str) -> NormalizedSourceRecord: ...
