from aire_archeotech.evidence.candidates import CandidateCard
from aire_archeotech.evidence.exports import render_dossier_json, render_dossier_markdown
from aire_archeotech.evidence.spans import EvidenceSpan


def _candidate() -> CandidateCard:
    span = EvidenceSpan.from_page_text(
        source_url="https://ntrs.nasa.gov/citations/123",
        artifact_sha256="a" * 64,
        document_reference="NACA-123",
        page_number=7,
        page_text="The NACA report describes the apparatus.",
        start=4,
        end=15,
    )
    return CandidateCard(
        id="candidate-naca-123",
        title="Apparatus statement",
        evidence=(span,),
        analyst_note="Needs human review.",
    )


def test_json_dossier_is_deterministic() -> None:
    candidate = _candidate()

    assert render_dossier_json(candidate) == render_dossier_json(candidate)
    assert b'"artifact_sha256":"' + b"a" * 64 in render_dossier_json(candidate)


def test_markdown_dossier_contains_source_locator() -> None:
    dossier = render_dossier_markdown(_candidate())

    assert "https://ntrs.nasa.gov/citations/123" in dossier
    assert "NACA-123" in dossier
    assert "Page 7" in dossier
    assert "NACA report" in dossier
