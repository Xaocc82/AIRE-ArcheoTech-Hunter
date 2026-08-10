"""Constrained, human-reviewable screening decisions."""

from dataclasses import dataclass
from enum import StrEnum


class ScreeningChannel(StrEnum):
    """The research dimension being screened."""

    PATENT = "patent"
    ENGINEERING = "engineering"
    SAFETY = "safety"


class ScreeningVerdict(StrEnum):
    """Permitted screening outcomes; none represent a substantive conclusion."""

    PASS_FOR_RESEARCH = "pass_for_research"
    HOLD = "hold"
    REJECT = "reject"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ScreeningRecord:
    """A bounded researcher decision that must be interpreted by a human."""

    candidate_id: str
    channel: ScreeningChannel
    verdict: ScreeningVerdict
    reviewer: str
    rationale: str

    def __post_init__(self) -> None:
        if not self.candidate_id.strip():
            raise ValueError("candidate_id must not be blank")
        if not self.reviewer.strip():
            raise ValueError("reviewer must not be blank")
        if not self.rationale.strip():
            raise ValueError("rationale must not be blank")
