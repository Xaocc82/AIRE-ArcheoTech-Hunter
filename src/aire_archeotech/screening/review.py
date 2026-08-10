"""Candidate-bound construction of bounded screening records."""

from aire_archeotech.evidence.candidates import CandidateCard
from aire_archeotech.screening.records import ScreeningChannel, ScreeningRecord, ScreeningVerdict


def record_screening(
    *,
    candidate: CandidateCard,
    channel: ScreeningChannel,
    verdict: ScreeningVerdict,
    reviewer: str,
    rationale: str,
) -> ScreeningRecord:
    """Record a human research decision without making an external conclusion."""
    return ScreeningRecord(
        candidate_id=candidate.id,
        channel=channel,
        verdict=verdict,
        reviewer=reviewer,
        rationale=rationale,
    )
