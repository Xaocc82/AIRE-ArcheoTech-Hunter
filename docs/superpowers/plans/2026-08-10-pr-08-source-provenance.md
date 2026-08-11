# Source Provenance Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make each bounded NTRS search retain response provenance before any research result can be used.

**Architecture:** The source contract will return a search result containing hits and immutable access evidence. NTRS transport will supply raw bytes, URL, status, and retrieval time; the adapter will cap records/bytes, persist raw bytes in CAS, and bind the resulting hash to its result.

**Tech Stack:** Python 3.12+, standard library HTTP/JSON, existing CAS, pytest.

### Task 1: Bound source queries

- [ ] Write a failing test that rejects a request above the fixed adapter cap.
- [ ] Implement a non-bypassable `MAX_SOURCE_RECORDS` validation in `SourceQuery`.
- [ ] Run targeted tests.

### Task 2: Preserve NTRS access evidence

- [ ] Write a failing test for a raw, timestamped NTRS response stored in CAS and returned as provenance.
- [ ] Change source contracts and NTRS adapter to retain URL, status, terms/rights references, retrieval time, byte count, and raw-response SHA-256.
- [ ] Reject oversized/non-success responses before normalizing records.
- [ ] Update fixture and contract tests; run the full suite.
