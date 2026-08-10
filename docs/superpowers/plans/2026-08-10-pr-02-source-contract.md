# PR-02 Source Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans or superpowers:subagent-driven-development task-by-task.

**Goal:** Add a deterministic, read-only source-adapter contract and fixture adapter.

**Architecture:** `base.py` defines typed query, limit, hit, record, and adapter protocol values. `fixtures.py` filters in-memory public test records by case-insensitive query and limits results without I/O. Later network adapters will implement the same `search()` and `fetch_record()` interface.

**Tech Stack:** Python 3.12+, dataclasses, typing Protocol, pytest.

## Global Constraints

- Source adapters are read-only.
- Production source access must be allowlisted and bounded.
- Fixture tests perform no network calls.

### Task 1: Define the contract

**Files:** Create `src/aire_archeotech/sources/base.py`; test `tests/unit/sources/test_contract.py`.

- [ ] Write a failing test that a fixture adapter search returns a normalized record with its source code and canonical reference.
- [ ] Run `python -m pytest tests/unit/sources/test_contract.py -v` and observe the missing contract failure.
- [ ] Implement frozen `SourceQuery`, `SourceHit`, `NormalizedSourceRecord`, and `SourceAdapter` protocol values.
- [ ] Re-run the test and commit the passing contract.

### Task 2: Implement the fixture adapter

**Files:** Create `src/aire_archeotech/sources/__init__.py`, `src/aire_archeotech/sources/fixtures.py`; test `tests/unit/sources/test_fixtures.py`.

- [ ] Write failing tests for matching only enabled fixture records and obeying `max_records`.
- [ ] Run the focused test and observe the missing adapter failure.
- [ ] Implement the in-memory read-only search and record lookup.
- [ ] Re-run all tests, Ruff, mypy, and `alembic upgrade head --sql`; commit and publish a draft PR.
