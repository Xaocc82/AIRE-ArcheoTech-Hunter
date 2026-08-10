import pytest

from aire_archeotech.evidence.candidates import CandidateCard
from aire_archeotech.evidence.spans import EvidenceSpan


def _evidence() -> EvidenceSpan:
    return EvidenceSpan.from_page_text(
        source_url="https://ntrs.nasa.gov/citations/123",
        artifact_sha256="a" * 64,
        document_reference="NACA-123",
        page_number=7,
        page_text="The NACA report describes the apparatus.",
        start=4,
        end=15,
    )


def test_candidate_card_contains_evidence() -> None:
    candidate = CandidateCard(
        id="candidate-naca-123",
        title="Apparatus statement",
        evidence=(_evidence(),),
        analyst_note="Needs human review.",
    )

    assert candidate.evidence[0].document_reference == "NACA-123"


def test_candidate_card_rejects_empty_evidence() -> None:
    with pytest.raises(ValueError, match="at least one evidence span"):
        CandidateCard(id="candidate-empty", title="Unsupported", evidence=())
