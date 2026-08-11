from importlib.util import find_spec

from aire_archeotech.sources.base import NormalizedSourceRecord, SourceAdapter, SourceQuery
from aire_archeotech.sources.fixtures import FixtureSourceAdapter
from aire_archeotech.storage.cas import ContentAddressedStorage


def test_source_contract_module_exists() -> None:
    try:
        spec = find_spec("aire_archeotech.sources.base")
    except ModuleNotFoundError:
        spec = None

    assert spec is not None


def _use_adapter(adapter: SourceAdapter) -> SourceAdapter:
    return adapter


def test_fixture_adapter_returns_full_source_search_result(tmp_path) -> None:
    fixture = FixtureSourceAdapter(
        records=(
            NormalizedSourceRecord(
                source_code="fixture",
                external_id="fixture-1",
                title="Fixture control mechanism",
                canonical_reference="https://example.invalid/fixture-1",
            ),
        ),
        storage=ContentAddressedStorage(tmp_path),
    )

    adapter = _use_adapter(fixture)
    result = adapter.search(SourceQuery("control"))

    assert result.hits[0].external_id == "fixture-1"
    assert result.access.request_sha256 == result.raw_request.sha256
    assert result.access.raw_response_sha256 == result.raw_response.sha256
