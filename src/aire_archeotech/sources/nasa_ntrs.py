"""Bounded, read-only NASA Technical Reports Server metadata adapter."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from io import BytesIO
from json import dumps, loads
from typing import Any
from urllib.request import Request

from aire_archeotech.sources.base import (
    NormalizedSourceRecord,
    SourceAccessEvidence,
    SourceHit,
    SourceQuery,
    SourceSearchResult,
    SourceTransportResponse,
)
from aire_archeotech.storage.cas import ContentAddressedStorage

NTRS_SEARCH_URL = "https://ntrs.nasa.gov/api/citations/search"
Transport = Callable[[Request, float], SourceTransportResponse]
MAX_RESPONSE_BYTES = 1_048_576


@dataclass
class NasaNtrsAdapter:
    """NASA NTRS adapter whose transport must be explicitly provided."""

    transport: Transport
    storage: ContentAddressedStorage
    terms_reference: str
    rights_reference: str
    timeout_seconds: float = 20.0
    code: str = "nasa_ntrs"
    _records: dict[str, NormalizedSourceRecord] = field(default_factory=dict, init=False)

    def search(self, query: SourceQuery) -> SourceSearchResult:
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
        if response.status_code != 200:
            raise ValueError(f"NTRS returned HTTP {response.status_code}")
        if len(response.body) > MAX_RESPONSE_BYTES:
            raise ValueError("NTRS response exceeds the byte limit")
        payload = loads(response.body)
        if not isinstance(payload, Mapping):
            raise ValueError("NTRS response must be a JSON object")
        raw_response = self.storage.store(BytesIO(response.body), "application/json")
        result_items = payload.get("results", [])
        records = tuple(self._normalize(item) for item in result_items[: query.max_records])
        self._records.update({record.external_id: record for record in records})
        hits = tuple(
            SourceHit(record.external_id, record.title, record.canonical_reference)
            for record in records
        )
        return SourceSearchResult(
            hits=hits,
            access=SourceAccessEvidence(
                source_url=response.source_url,
                status_code=response.status_code,
                retrieved_at=response.retrieved_at,
                terms_reference=self.terms_reference,
                rights_reference=self.rights_reference,
                raw_response_sha256=raw_response.sha256,
                response_byte_size=raw_response.byte_size,
            ),
            raw_response=raw_response,
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
