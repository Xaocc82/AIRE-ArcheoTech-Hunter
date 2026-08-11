from datetime import UTC, datetime
from json import dumps

import pytest

from aire_archeotech.sources.base import (
    SourceQuery,
    SourceSearchFailure,
    SourceTransportFailure,
    SourceTransportResponse,
)
from aire_archeotech.sources.nasa_ntrs import MAX_RESPONSE_BYTES, NasaNtrsAdapter
from aire_archeotech.storage.cas import ContentAddressedStorage


def _assert_failure_evidence(failure: SourceSearchFailure, raw_response: bytes) -> None:
    assert failure.access.request_sha256 == failure.raw_request.sha256
    assert failure.access.raw_response_sha256 == failure.raw_response.sha256
    assert failure.raw_response.path.read_bytes() == raw_response


def test_ntrs_search_stores_raw_response_and_returns_access_evidence(tmp_path) -> None:
    raw_response = dumps(
        {"results": [{"id": "19960028014", "title": "NACA memorandum"}]}
    ).encode()

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
            content_type="application/json",
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


def test_ntrs_search_binds_stored_request_to_stored_response(tmp_path) -> None:
    raw_response = dumps(
        {"results": [{"id": "19960028014", "title": "NACA memorandum"}]}
    ).encode()

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
            content_type="application/json",
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    result = adapter.search(SourceQuery("NACA", max_records=1))

    assert result.access.request_sha256 == result.raw_request.sha256
    assert result.access.final_url == "https://ntrs.nasa.gov/api/citations/search"
    assert result.access.retrieved_at.tzinfo is not None
    assert result.access.source_code == "nasa_ntrs"
    assert result.access.request_method == "POST"
    assert result.access.request_content_type == "application/json"
    assert result.access.request_byte_size == result.raw_request.byte_size


def test_ntrs_non_200_preserves_request_and_response_evidence(tmp_path) -> None:
    raw_response = b'{"error":"rate limited"}'

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=429,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
            content_type="application/json",
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceSearchFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    failure = raised.value
    assert failure.access.status_code == 429
    _assert_failure_evidence(failure, raw_response)


def test_ntrs_rejects_redirect_after_storing_response_evidence(tmp_path) -> None:
    raw_response = dumps(
        {"results": [{"id": "19960028014", "title": "NACA memorandum"}]}
    ).encode()

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://untrusted.example/ntrs",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
            content_type="application/json",
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceSearchFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    assert raised.value.access.final_url == "https://untrusted.example/ntrs"
    _assert_failure_evidence(raised.value, raw_response)


def test_ntrs_rejects_non_json_content_type_after_storing_evidence(tmp_path) -> None:
    raw_response = dumps(
        {"results": [{"id": "19960028014", "title": "NACA memorandum"}]}
    ).encode()

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
            content_type="text/html",
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceSearchFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    assert raised.value.access.content_type == "text/html"
    _assert_failure_evidence(raised.value, raw_response)


def test_ntrs_rejects_naive_retrieval_time_after_storing_evidence(tmp_path) -> None:
    raw_response = dumps(
        {"results": [{"id": "19960028014", "title": "NACA memorandum"}]}
    ).encode()

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10),
            body=raw_response,
            content_type="application/json",
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceSearchFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    assert raised.value.access.retrieved_at.tzinfo is None
    _assert_failure_evidence(raised.value, raw_response)


@pytest.mark.parametrize(
    ("terms_reference", "rights_reference"),
    [
        ("", "https://www.nasa.gov/nasa-brand-center/images-and-media/"),
        ("https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/", "  "),
    ],
)
def test_ntrs_rejects_blank_policy_references_before_transport(
    tmp_path, terms_reference: str, rights_reference: str
) -> None:
    transport_calls = 0

    def transport(*_args: object) -> SourceTransportResponse:
        nonlocal transport_calls
        transport_calls += 1
        raise AssertionError("invalid adapter configuration must not call transport")

    with pytest.raises(ValueError, match="reference must not be blank"):
        NasaNtrsAdapter(
            transport=transport,
            storage=ContentAddressedStorage(tmp_path),
            terms_reference=terms_reference,
            rights_reference=rights_reference,
        )

    assert transport_calls == 0


def test_ntrs_rejects_non_collection_results_with_stored_evidence(tmp_path) -> None:
    raw_response = dumps({"results": {"id": "19960028014"}}).encode()

    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
            content_type="application/json",
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceSearchFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    _assert_failure_evidence(raised.value, raw_response)


def test_ntrs_transport_failure_preserves_stored_request_without_fabricating_response(
    tmp_path,
) -> None:
    def transport(*_args: object) -> SourceTransportResponse:
        raise TimeoutError("connection timed out")

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceTransportFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    assert raised.value.state == "REQUEST_STORED_NO_RESPONSE"
    assert raised.value.raw_request.path.exists()


@pytest.mark.parametrize(
    "raw_response",
    [
        b"not-json",
        dumps([{"id": "19960028014"}]).encode(),
        dumps({"results": [{"title": "NACA memorandum"}]}).encode(),
        dumps({"results": [123]}).encode(),
        dumps({"results": [{"_source": "not-an-object"}]}).encode(),
    ],
)
def test_ntrs_rejects_invalid_response_records_with_stored_evidence(
    tmp_path, raw_response: bytes
) -> None:
    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url="https://ntrs.nasa.gov/api/citations/search",
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=raw_response,
            content_type="application/json",
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceSearchFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    _assert_failure_evidence(raised.value, raw_response)


@pytest.mark.parametrize(
    ("requested_url", "body", "body_complete", "limit_exceeded"),
    [
        (
            "https://untrusted.example/ntrs",
            dumps({"results": []}).encode(),
            True,
            False,
        ),
        (
            "https://ntrs.nasa.gov/api/citations/search",
            b"x" * (MAX_RESPONSE_BYTES + 1),
            True,
            False,
        ),
        (
            "https://ntrs.nasa.gov/api/citations/search",
            dumps({"results": []}).encode(),
            False,
            False,
        ),
        (
            "https://ntrs.nasa.gov/api/citations/search",
            dumps({"results": []}).encode(),
            True,
            True,
        ),
    ],
    ids=("unexpected-request-url", "body-over-cap", "incomplete-body", "limit-exceeded"),
)
def test_ntrs_rejects_bounded_transport_failures_with_stored_evidence(
    tmp_path,
    requested_url: str,
    body: bytes,
    body_complete: bool,
    limit_exceeded: bool,
) -> None:
    def transport(*_args: object) -> SourceTransportResponse:
        return SourceTransportResponse(
            requested_url=requested_url,
            final_url="https://ntrs.nasa.gov/api/citations/search",
            status_code=200,
            retrieved_at=datetime(2026, 8, 10, tzinfo=UTC),
            body=body,
            content_type="application/json",
            body_complete=body_complete,
            limit_exceeded=limit_exceeded,
            bytes_read=len(body),
        )

    adapter = NasaNtrsAdapter(
        transport=transport,
        storage=ContentAddressedStorage(tmp_path),
        terms_reference="https://www.nasa.gov/nasa-web-privacy-policy-and-important-notices/",
        rights_reference="https://www.nasa.gov/nasa-brand-center/images-and-media/",
    )

    with pytest.raises(SourceSearchFailure) as raised:
        adapter.search(SourceQuery("NACA", max_records=1))

    _assert_failure_evidence(raised.value, body)
