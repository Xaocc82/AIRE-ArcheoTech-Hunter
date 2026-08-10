"""Deterministic local adapter used by contract and workflow tests."""

from dataclasses import dataclass

from aire_archeotech.sources.base import NormalizedSourceRecord, SourceHit, SourceQuery


@dataclass(frozen=True)
class FixtureSourceAdapter:
    records: tuple[NormalizedSourceRecord, ...]
    code: str = "fixture"

    def search(self, query: SourceQuery) -> tuple[SourceHit, ...]:
        query_text = query.text.casefold()
        matching_records = (
            record
            for record in self.records
            if query_text in record.title.casefold() or query_text in record.description.casefold()
        )
        return tuple(
            SourceHit(record.external_id, record.title, record.canonical_reference)
            for record in matching_records
        )[: query.max_records]

    def fetch_record(self, external_id: str) -> NormalizedSourceRecord:
        for record in self.records:
            if record.external_id == external_id:
                return record
        raise KeyError(external_id)
