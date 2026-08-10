from datetime import UTC, datetime
from importlib.util import find_spec
from json import dumps, loads
from urllib.request import Request

from aire_archeotech.sources.base import SourceQuery, SourceTransportResponse
from aire_archeotech.sources.nasa_ntrs import NasaNtrsAdapter
from aire_archeotech.storage.cas import ContentAddressedStorage


def test_nasa_ntrs_module_exists() -> None:
    assert find_spec("aire_archeotech.sources.nasa_ntrs") is not None


def test_ntrs_search_normalizes_record_and_respects_limit(tmp_path) -> None:
    def transport(request: Request, timeout: float) -> SourceTransportResponse:
        assert request.full_url == "https://ntrs.nasa.gov/api/citations/search"
        assert timeout == 20.0
        assert loads(request.data or b"{}") ["size"] == 1
        return SourceTransportResponse(
            source_url=request.full_url,
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=dumps(
                {
                    "results": [
                        {
                            "id": "19960028014",
                            "title": "NASAwide technical memorandum",
                            "abstract": "A NACA report record.",
                        }
                    ]
                }
            ).encode(),
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="terms",
        rights_reference="rights",
    )
    result = adapter.search(SourceQuery("experimental", max_records=1))

    assert result.hits[0].canonical_reference.endswith("19960028014")
    assert adapter.fetch_record("19960028014").source_code == "nasa_ntrs"
