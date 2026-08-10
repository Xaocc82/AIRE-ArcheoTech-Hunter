"""Evidence-bound candidate cards for human research review."""

from dataclasses import dataclass

from aire_archeotech.evidence.spans import EvidenceSpan


@dataclass(frozen=True)
class CandidateCard:
    """A research candidate supported by one or more archival evidence spans."""

    id: str
    title: str
    evidence: tuple[EvidenceSpan, ...]
    analyst_note: str = ""

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("candidate id must not be blank")
        if not self.title.strip():
            raise ValueError("candidate title must not be blank")
        if not self.evidence:
            raise ValueError("candidate requires at least one evidence span")
