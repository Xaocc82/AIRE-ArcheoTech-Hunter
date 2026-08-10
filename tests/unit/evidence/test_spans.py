from aire_archeotech.evidence.spans import EvidenceSpan


def test_span_preserves_exact_physical_source_locator() -> None:
    page_text = "The NACA report describes the apparatus."

    span = EvidenceSpan.from_page_text(
        source_url="https://ntrs.nasa.gov/citations/123",
        artifact_sha256="a" * 64,
        document_reference="NACA-123",
        page_number=7,
        page_text=page_text,
        start=4,
        end=15,
    )

    assert span.quote == "NACA report"
    assert span.page_number == 7
    assert span.artifact_sha256 == "a" * 64
