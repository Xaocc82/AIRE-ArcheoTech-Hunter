# Evidence Dossier Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn processed archival text into an evidence-bound candidate card with deterministic JSON and Markdown dossier exports.

**Architecture:** Pure domain types preserve the physical source locator, original SHA-256 artifact, page number, character span, and quoted source text. Candidate cards only assemble validated evidence; export functions serialize that immutable data without deciding historical function, novelty, or legal status.

**Tech Stack:** Python 3.12+, standard library JSON/dataclasses, pytest, Ruff, mypy.

## Global Constraints

- An archival assertion must resolve to source URL, original artifact hash, document, physical page, and exact evidence span.
- Original statements remain separate from translations and analyst interpretation.
- Candidate creation is screening-only: no legal clearance, novelty, or functionality claim.
- Exports are deterministic and must not include time-dependent or random values.

---

### Task 1: Create validated evidence spans

**Files:**
- Create: `tests/unit/evidence/test_spans.py`
- Create: `src/aire_archeotech/evidence/spans.py`
- Create: `src/aire_archeotech/evidence/__init__.py`

- [ ] Write a failing test that creates a span from page text and checks exact quote, offsets, source URL, and SHA-256 are preserved.
- [ ] Run `python -m pytest tests/unit/evidence/test_spans.py -q`; expect an import failure.
- [ ] Implement immutable `EvidenceSpan` and `EvidenceSpan.from_page_text`, rejecting invalid physical locators or mismatched quote bounds.
- [ ] Re-run the targeted test; expect pass.

### Task 2: Create evidence-bound candidate cards

**Files:**
- Create: `tests/unit/evidence/test_candidates.py`
- Create: `src/aire_archeotech/evidence/candidates.py`

- [ ] Write a failing test showing a named candidate stores one or more evidence spans and rejects an empty evidence collection.
- [ ] Run `python -m pytest tests/unit/evidence/test_candidates.py -q`; expect missing candidate type failure.
- [ ] Implement immutable `CandidateCard` with a caller-provided stable ID, title, evidence collection, and optional analyst note.
- [ ] Re-run the targeted test; expect pass.

### Task 3: Render deterministic dossiers

**Files:**
- Create: `tests/unit/evidence/test_exports.py`
- Create: `src/aire_archeotech/evidence/exports.py`

- [ ] Write a failing test that compares two JSON exports byte-for-byte and checks Markdown includes every source locator.
- [ ] Run `python -m pytest tests/unit/evidence/test_exports.py -q`; expect missing export functions failure.
- [ ] Implement `render_dossier_json` and `render_dossier_markdown` from stable candidate data only.
- [ ] Re-run the targeted test; expect pass.

### Task 4: Verify and publish

**Files:**
- Modify: `README.md`

- [ ] Document that a dossier is an auditable research record, not a legal or technical conclusion.
- [ ] Run `python -m ruff check .`, `python -m mypy src`, and `python -m pytest -q`; all must exit 0.
- [ ] Commit and push only the evidence package, its tests, README, and this plan. Create a draft PR based on `agent/pr-04-processing`.
