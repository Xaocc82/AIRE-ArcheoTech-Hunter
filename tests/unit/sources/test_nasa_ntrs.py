from importlib.util import find_spec
from json import loads
from urllib.request import Request

from aire_archeotech.sources.base import SourceQuery
from aire_archeotech.sources.nasa_ntrs import NasaNtrsAdapter


def test_nasa_ntrs_module_exists() -> None:
    assert find_spec("aire_archeotech.sources.nasa_ntrs") is not None


def test_ntrs_search_normalizes_record_and_respects_limit() -> None:
    def transport(request: Request, timeout: float) -> dict[str, object]:
        assert request.full_url == "https://ntrs.nasa.gov/api/citations/search"
        assert timeout == 20.0
        assert loads(request.data or b"{}") ["size"] == 1
        return {
            "results": [
                {
                    "id": "19960028014",
                    "title": "NASAwide technical memorandum",
                    "abstract": "A NACA report record.",
                }
            ]
        }

    adapter = NasaNtrsAdapter(transport=transport)
    hits = adapter.search(SourceQuery("experimental", max_records=1))

    assert hits[0].canonical_reference.endswith("19960028014")
    assert adapter.fetch_record("19960028014").source_code == "nasa_ntrs"
