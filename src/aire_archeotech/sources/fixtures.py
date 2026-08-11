"""Deterministic local adapter used by contract and workflow tests."""

from dataclasses import dataclass
from datetime import UTC, datetime
from io import BytesIO
from json import dumps

from aire_archeotech.sources.base import (
    NormalizedSourceRecord,
    SourceAccessEvidence,
    SourceAdapter,
    SourceHit,
    SourceQuery,
    SourceSearchResult,
)
from aire_archeotech.storage.cas import ContentAddressedStorage


@dataclass(frozen=True)
class FixtureSourceAdapter:
    records: tuple[NormalizedSourceRecord, ...]
    storage: ContentAddressedStorage
    terms_reference: str = "fixture://terms"
    rights_reference: str = "fixture://rights"
    code: str = "fixture"

    def search(self, query: SourceQuery) -> SourceSearchResult:
        query_text = query.text.casefold()
        matching_records = (
            record
            for record in self.records
            if query_text in record.title.casefold() or query_text in record.description.casefold()
        )
        hits = tuple(
            SourceHit(record.external_id, record.title, record.canonical_reference)
            for record in matching_records
        )[: query.max_records]
        request_body = dumps({"query": query.text, "max_records": query.max_records}).encode()
        response_body = dumps(
            {
                "results": [
                    {
                        "id": hit.external_id,
                        "title": hit.title,
                        "reference": hit.canonical_reference,
                    }
                    for hit in hits
                ]
            },
            sort_keys=True,
        ).encode()
        raw_request = self.storage.store(BytesIO(request_body), "application/json")
        raw_response = self.storage.store(BytesIO(response_body), "application/json")
        access = SourceAccessEvidence(
            source_code=self.code,
            adapter_version="0.1",
            requested_url="fixture://search",
            final_url="fixture://search",
            request_method="POST",
            request_content_type="application/json",
            request_byte_size=raw_request.byte_size,
            status_code=200,
            retrieved_at=datetime(1970, 1, 1, tzinfo=UTC),
            terms_reference=self.terms_reference,
            rights_reference=self.rights_reference,
            request_sha256=raw_request.sha256,
            raw_response_sha256=raw_response.sha256,
            response_byte_size=raw_response.byte_size,
            content_type="application/json",
            transport_bytes_read=raw_response.byte_size,
            body_complete=True,
            limit_exceeded=False,
        )
        return SourceSearchResult(
            hits=hits,
            access=access,
            raw_request=raw_request,
            raw_response=raw_response,
        )

    def fetch_record(self, external_id: str) -> NormalizedSourceRecord:
        for record in self.records:
            if record.external_id == external_id:
                return record
        raise KeyError(external_id)


def _as_source_adapter(adapter: FixtureSourceAdapter) -> SourceAdapter:
    """Make the fixture's structural adapter conformance part of the checked source tree."""
    return adapter
