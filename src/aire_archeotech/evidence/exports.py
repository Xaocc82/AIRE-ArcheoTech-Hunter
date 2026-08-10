"""Deterministic evidence dossier renderers."""

import json
from typing import Any

from aire_archeotech.evidence.candidates import CandidateCard
from aire_archeotech.evidence.spans import EvidenceSpan


def _span_data(span: EvidenceSpan) -> dict[str, Any]:
    return {
        "artifact_sha256": span.artifact_sha256,
        "character_end": span.character_end,
        "character_start": span.character_start,
        "document_reference": span.document_reference,
        "page_number": span.page_number,
        "quote": span.quote,
        "source_url": span.source_url,
    }


def _candidate_data(candidate: CandidateCard) -> dict[str, Any]:
    return {
        "analyst_note": candidate.analyst_note,
        "evidence": [_span_data(span) for span in candidate.evidence],
        "id": candidate.id,
        "title": candidate.title,
    }


def render_dossier_json(candidate: CandidateCard) -> bytes:
    """Return canonical UTF-8 JSON for an evidence-bound candidate card."""
    return json.dumps(
        _candidate_data(candidate),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode()


def render_dossier_markdown(candidate: CandidateCard) -> str:
    """Render a human-readable research dossier without drawing conclusions."""
    lines = [
        f"# Candidate: {candidate.title}",
        "",
        f"ID: `{candidate.id}`",
        "",
        "> Research record only; it is not a legal, novelty, or engineering conclusion.",
        "",
        "## Analyst note",
        "",
        candidate.analyst_note or "None recorded.",
        "",
        "## Evidence",
    ]
    for index, span in enumerate(candidate.evidence, start=1):
        lines.extend(
            [
                "",
                f"### Evidence {index}",
                "",
                f"- Source: {span.source_url}",
                f"- Artifact SHA-256: `{span.artifact_sha256}`",
                f"- Document: {span.document_reference}",
                (
                    f"- Page {span.page_number}, "
                    f"characters {span.character_start}-{span.character_end}"
                ),
                f"- Quote: {span.quote}",
            ]
        )
    return "\n".join(lines) + "\n"
