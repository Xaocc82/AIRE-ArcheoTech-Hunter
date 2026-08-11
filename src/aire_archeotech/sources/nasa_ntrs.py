"""Bounded, read-only NASA Technical Reports Server metadata adapter."""

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from io import BytesIO
from json import JSONDecodeError, dumps, loads
from typing import Any
from urllib.request import Request

from aire_archeotech.sources.base import (
    NormalizedSourceRecord,
    SourceAccessEvidence,
    SourceHit,
    SourceQuery,
    SourceSearchFailure,
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

    def __post_init__(self) -> None:
        if not self.terms_reference.strip() or not self.rights_reference.strip():
            raise ValueError("source policy reference must not be blank")

    def search(self, query: SourceQuery) -> SourceSearchResult:
        request_body = dumps(self._payload(query)).encode("utf-8")
        request = Request(
            NTRS_SEARCH_URL,
            data=request_body,
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AIRE-ArcheoTech-Hunter/0.1 (read-only research)",
            },
            method="POST",
        )
        raw_request = self.storage.store(BytesIO(request_body), "application/json")
        response = self.transport(request, self.timeout_seconds)
        raw_response = self.storage.store(BytesIO(response.body), response.content_type)
        access = SourceAccessEvidence(
            requested_url=response.requested_url,
            final_url=response.final_url,
            status_code=response.status_code,
            retrieved_at=response.retrieved_at,
            terms_reference=self.terms_reference,
            rights_reference=self.rights_reference,
            request_sha256=raw_request.sha256,
            raw_response_sha256=raw_response.sha256,
            response_byte_size=raw_response.byte_size,
            content_type=response.content_type,
        )
        if response.status_code != 200:
            raise SourceSearchFailure(
                f"NTRS returned HTTP {response.status_code}",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        if response.requested_url != NTRS_SEARCH_URL:
            raise SourceSearchFailure(
                "NTRS requested URL is not allowlisted",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        if response.final_url != NTRS_SEARCH_URL:
            raise SourceSearchFailure(
                "NTRS final URL is not allowlisted",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        if response.content_type.split(";", maxsplit=1)[0].strip().lower() != "application/json":
            raise SourceSearchFailure(
                "NTRS response content type is not JSON",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        if (
            response.retrieved_at.tzinfo is None
            or response.retrieved_at.utcoffset() is None
        ):
            raise SourceSearchFailure(
                "NTRS retrieval time must be timezone-aware",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        if len(response.body) > MAX_RESPONSE_BYTES:
            raise SourceSearchFailure(
                "NTRS response exceeds the byte limit",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        try:
            payload = loads(response.body)
        except JSONDecodeError as error:
            raise SourceSearchFailure(
                "NTRS response is not valid JSON",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            ) from error
        if not isinstance(payload, Mapping):
            raise SourceSearchFailure(
                "NTRS response must be a JSON object",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        result_items = payload.get("results", [])
        if not isinstance(result_items, list):
            raise SourceSearchFailure(
                "NTRS response results must be a collection",
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            )
        try:
            records = tuple(self._normalize(item) for item in result_items[: query.max_records])
        except ValueError as error:
            raise SourceSearchFailure(
                str(error),
                access=access,
                raw_request=raw_request,
                raw_response=raw_response,
            ) from error
        self._records.update({record.external_id: record for record in records})
        hits = tuple(
            SourceHit(record.external_id, record.title, record.canonical_reference)
            for record in records
        )
        return SourceSearchResult(
            hits=hits,
            access=access,
            raw_request=raw_request,
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
