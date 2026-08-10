from datetime import UTC, datetime
from json import dumps

from aire_archeotech.sources.base import SourceQuery, SourceTransportResponse
from aire_archeotech.sources.nasa_ntrs import NasaNtrsAdapter
from aire_archeotech.storage.cas import ContentAddressedStorage


def test_ntrs_search_stores_raw_response_and_returns_access_evidence(tmp_path) -> None:
    raw_response = dumps(
        {"results": [{"id": "19960028014", "title": "NACA memorandum"}]}
    ).encode()

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            source_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    result = adapter.search(SourceQuery("NACA", max_records=1))

    assert result.hits[0].external_id == "19960028014"
    assert result.access.raw_response_sha256 == result.raw_response.sha256
    assert result.access.status_code == 200
    assert result.raw_response.path.read_bytes() == raw_response
