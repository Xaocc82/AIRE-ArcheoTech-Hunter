"""Bounded, read-only NASA Technical Reports Server metadata adapter."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from json import dumps
from typing import Any
from urllib.request import Request

from aire_archeotech.sources.base import NormalizedSourceRecord, SourceHit, SourceQuery

NTRS_SEARCH_URL = "https://ntrs.nasa.gov/api/citations/search"
Transport = Callable[[Request, float], Mapping[str, Any]]


@dataclass
class NasaNtrsAdapter:
    """NASA NTRS adapter whose transport must be explicitly provided."""

    transport: Transport
    timeout_seconds: float = 20.0
    code: str = "nasa_ntrs"
    _records: dict[str, NormalizedSourceRecord] = field(default_factory=dict, init=False)

    def search(self, query: SourceQuery) -> tuple[SourceHit, ...]:
        request = Request(
            NTRS_SEARCH_URL,
            data=dumps(self._payload(query)).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AIRE-ArcheoTech-Hunter/0.1 (read-only research)",
            },
            method="POST",
        )
        response = self.transport(request, self.timeout_seconds)
        records = tuple(self._normalize(item) for item in response.get("results", []))
        self._records.update({record.external_id: record for record in records})
        return tuple(
            SourceHit(record.external_id, record.title, record.canonical_reference)
            for record in records[: query.max_records]
        )

    def fetch_record(self, external_id: str) -> NormalizedSourceRecord:
        return self._records[external_id]

    @staticmethod
    def _payload(query: SourceQuery) -> dict[str, object]:
        return {
            "query": {
                "bool": {
                    "must": [
                        {"query_string": {"query": query.text}},
                        {"range": {"publication_date": {"gte": "19150101", "lte": "19501231"}}},
                    ]
                }
            },
            "size": query.max_records,
        }

    def _normalize(self, item: Mapping[str, Any]) -> NormalizedSourceRecord:
        source = item.get("_source", item)
        external_id = str(source.get("id", source.get("document_id", "")))
        if not external_id:
            raise ValueError("NTRS response record is missing an identifier")
        title = str(source.get("title", "Untitled NTRS record"))
        description = str(source.get("abstract", source.get("description", "")))
        return NormalizedSourceRecord(
            source_code=self.code,
            external_id=external_id,
            title=title,
            canonical_reference=f"https://ntrs.nasa.gov/citations/{external_id}",
            description=description,
        )
