from aire_archeotech.sources.base import NormalizedSourceRecord, SourceQuery
from aire_archeotech.sources.fixtures import FixtureSourceAdapter


def test_fixture_search_returns_normalized_hits_with_limit() -> None:
    adapter = FixtureSourceAdapter(
        records=(
            NormalizedSourceRecord("fixture", "one", "Bearing report", "fixture:one"),
            NormalizedSourceRecord("fixture", "two", "Bearing trials", "fixture:two"),
        )
    )

    hits = adapter.search(SourceQuery("bearing", max_records=1))

    assert hits[0].external_id == "one"
    assert len(hits) == 1


def test_fixture_record_lookup_preserves_source_provenance() -> None:
    record = NormalizedSourceRecord(
        source_code="fixture",
        external_id="one",
        title="Bearing report",
        canonical_reference="fixture:one",
        description="Experimental material study",
    )
    adapter = FixtureSourceAdapter(records=(record,))

    assert adapter.fetch_record("one") == record
