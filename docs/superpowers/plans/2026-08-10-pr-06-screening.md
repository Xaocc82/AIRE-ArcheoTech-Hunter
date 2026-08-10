# Research Screening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Record bounded, human-reviewable research-screening decisions for evidence-bound candidates.

**Architecture:** Screening is a pure-domain append-only record that binds a channel, allowed verdict, reason, reviewer identity, and candidate ID. It can support patent, engineering, or safety triage, but its vocabulary intentionally prevents the code from representing legal clearance, functional validation, or novelty conclusions.

**Tech Stack:** Python 3.12+, dataclasses, pytest, Ruff, mypy.

## Global Constraints

- Verdict values are exactly `PASS_FOR_RESEARCH`, `HOLD`, `REJECT`, or `UNKNOWN`.
- Screening is not legal clearance, a patent opinion, a novelty determination, or engineering validation.
- A decision requires a nonblank human-readable rationale and reviewer identity.
- All data remains deterministic; no model or online screening service is called.

---

### Task 1: Define safe screening records

**Files:**
- Create: `tests/unit/screening/test_records.py`
- Create: `src/aire_archeotech/screening/records.py`
- Create: `src/aire_archeotech/screening/__init__.py`

- [ ] Write a failing test showing an allowed verdict, channel, reviewer, and rationale are preserved.
- [ ] Run `python -m pytest tests/unit/screening/test_records.py -q`; expect an import failure.
- [ ] Implement immutable `ScreeningRecord`, `ScreeningChannel`, and the constrained verdict enum.
- [ ] Re-run the targeted test; expect pass.

### Task 2: Add candidate-bound review decisions

**Files:**
- Create: `tests/unit/screening/test_review.py`
- Create: `src/aire_archeotech/screening/review.py`

- [ ] Write a failing test that records a `HOLD` decision against an evidence-bound candidate and preserves its candidate ID.
- [ ] Run `python -m pytest tests/unit/screening/test_review.py -q`; expect missing service failure.
- [ ] Implement `record_screening` without external calls or automated conclusions.
- [ ] Re-run the targeted test; expect pass.

### Task 3: Verify and publish

**Files:**
- Modify: `README.md`

- [ ] Document the screening limitation.
- [ ] Run `python -m ruff check .`, `python -m mypy src`, and `python -m pytest -q`; all must exit 0.
- [ ] Commit and push only screening, its tests, README, and this plan. Create a draft PR based on `agent/pr-05-evidence-dossier`.
