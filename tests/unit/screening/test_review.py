from aire_archeotech.evidence.candidates import CandidateCard
from aire_archeotech.evidence.spans import EvidenceSpan
from aire_archeotech.screening.records import ScreeningChannel, ScreeningVerdict
from aire_archeotech.screening.review import record_screening


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
    return CandidateCard(id="candidate-naca-123", title="Apparatus statement", evidence=(span,))


def test_review_binds_hold_decision_to_candidate() -> None:
    record = record_screening(
        candidate=_candidate(),
        channel=ScreeningChannel.PATENT,
        verdict=ScreeningVerdict.HOLD,
        reviewer="researcher@example.test",
        rationale="Requires a jurisdiction-specific human review.",
    )

    assert record.candidate_id == "candidate-naca-123"
    assert record.verdict is ScreeningVerdict.HOLD
