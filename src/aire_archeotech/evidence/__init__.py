"""Evidence-bound research domain objects."""

from aire_archeotech.evidence.candidates import CandidateCard
from aire_archeotech.evidence.exports import render_dossier_json, render_dossier_markdown
from aire_archeotech.evidence.spans import EvidenceSpan

__all__ = [
    "CandidateCard",
    "EvidenceSpan",
    "render_dossier_json",
    "render_dossier_markdown",
]
