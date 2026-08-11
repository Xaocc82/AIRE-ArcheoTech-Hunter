# PR-08 Source Provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the bounded NASA NTRS metadata adapter preserve verifiable request and response provenance on both success and failure paths.

**Architecture:** The adapter will store the canonical request before transport and the bounded response before parsing. A typed source-attempt failure will carry persisted evidence when validation fails. The transport response contract will expose requested/final URLs and HTTP metadata so the adapter can reject redirects and untrusted content without losing its audit chain.

**Tech Stack:** Python 3.12+, pytest, mypy strict, ruff, ContentAddressedStorage.

## Global Constraints

- Only `https://ntrs.nasa.gov/api/citations/search` is accepted for this adapter.
- Metadata request limit is 100 records; response body limit is 1 MiB.
- No document download, queue, CLI orchestration, OCR, new source adapter, or external network test is included.
- Request and response JSON are stored in CAS before response parsing or normalization.
- UTC-aware retrieval times and nonblank terms/rights references are mandatory.

---

### Task 1: Define transport and provenance contracts

**Files:**
- Modify: `src/aire_archeotech/sources/base.py`
- Test: `tests/unit/sources/test_ntrs_provenance.py`

**Interfaces:**
- Produces `SourceTransportResponse(requested_url, final_url, status_code, retrieved_at, body, content_type)`.
- Produces `SourceAccessEvidence(request_sha256, raw_response_sha256, requested_url, final_url, status_code, retrieved_at, terms_reference, rights_reference, response_byte_size, content_type)`.
- Produces `SourceSearchFailure` with `access` and `raw_request`/`raw_response` artefacts.

- [ ] **Step 1: Write failing tests for evidence fields and an aware timestamp.**

```python
assert result.access.request_sha256 == result.raw_request.sha256
assert result.access.final_url == NTRS_SEARCH_URL
assert result.access.retrieved_at.tzinfo is not None
```

- [ ] **Step 2: Run the focused test and verify it fails because the fields do not exist.**

Run: `pytest tests/unit/sources/test_ntrs_provenance.py -v`

- [ ] **Step 3: Add only the typed dataclass fields and source failure type required by the tests.**

```python
@dataclass(frozen=True)
class SourceSearchFailure(Exception):
    message: str
    access: SourceAccessEvidence
    raw_request: StoredBlob
    raw_response: StoredBlob
```

- [ ] **Step 4: Re-run the focused test and verify the contract compiles.**

Run: `pytest tests/unit/sources/test_ntrs_provenance.py -v`

### Task 2: Persist bounded attempts before parsing

**Files:**
- Modify: `src/aire_archeotech/sources/nasa_ntrs.py`
- Test: `tests/unit/sources/test_ntrs_provenance.py`

**Interfaces:**
- Consumes the Task 1 transport response and `ContentAddressedStorage`.
- Produces `SourceSearchResult(raw_request, raw_response, access)` on success.
- Raises `SourceSearchFailure` for non-200, over-limit body, wrong content type, invalid JSON, non-object JSON, bad redirect, and missing record IDs.

- [ ] **Step 1: Add one failing test per failure path; each asserts the request and response blobs exist and their hashes match evidence.**

```python
with pytest.raises(SourceSearchFailure) as raised:
    adapter.search(SourceQuery("NACA"))
assert raised.value.raw_response.path.read_bytes() == raw_response
assert raised.value.access.raw_response_sha256 == raised.value.raw_response.sha256
```

- [ ] **Step 2: Run the focused tests and verify the current adapter raises `ValueError` without preserved evidence.**

Run: `pytest tests/unit/sources/test_ntrs_provenance.py -v`

- [ ] **Step 3: Store request JSON, call the injected transport, store response bytes, build evidence, then validate in the stated order.**

```python
raw_request = storage.store(BytesIO(request_body), "application/json")
response = transport(request, timeout_seconds)
raw_response = storage.store(BytesIO(response.body), response.content_type)
access = _build_access_evidence(...)
```

- [ ] **Step 4: Re-run the focused tests and verify success and all failure evidence paths pass.**

Run: `pytest tests/unit/sources/test_ntrs_provenance.py -v`

### Task 3: Enforce source-policy invariants

**Files:**
- Modify: `src/aire_archeotech/sources/nasa_ntrs.py`
- Test: `tests/unit/sources/test_nasa_ntrs.py`
- Test: `tests/unit/sources/test_ntrs_provenance.py`

**Interfaces:**
- `NasaNtrsAdapter.search(SourceQuery)` accepts only NTRS final URL, `application/json` content type, nonblank references, and timezone-aware retrieval time.

- [ ] **Step 1: Add failing tests for redirect, blank terms/rights, naive datetime, invalid content type, response byte cap, and missing identifier.**

```python
assert raised.value.access.final_url == "https://untrusted.example/"
assert raised.value.raw_response.byte_size == len(raw_response)
```

- [ ] **Step 2: Run the two source test modules and verify each new case fails for the missing policy check.**

Run: `pytest tests/unit/sources/test_nasa_ntrs.py tests/unit/sources/test_ntrs_provenance.py -v`

- [ ] **Step 3: Implement direct checks and a `fail(message, access, request, response)` helper; do not add retries or live I/O.**

```python
if response.final_url != NTRS_SEARCH_URL:
    raise self._failure("NTRS final URL is not allowlisted", access, raw_request, raw_response)
```

- [ ] **Step 4: Re-run the two modules and verify all policy tests pass.**

Run: `pytest tests/unit/sources/test_nasa_ntrs.py tests/unit/sources/test_ntrs_provenance.py -v`

### Task 4: Verify the PR-08 gate

**Files:**
- Modify only files changed by Tasks 1–3.

- [ ] **Step 1: Run all tests, lint, and strict type checking.**

Run: `pytest -q && ruff check . && mypy src`

- [ ] **Step 2: Inspect the diff for scope creep.**

Run: `git diff --check && git diff -- src/aire_archeotech/sources tests/unit/sources`

- [ ] **Step 3: Commit the focused provenance repair.**

Run: `git add src/aire_archeotech/sources/base.py src/aire_archeotech/sources/nasa_ntrs.py tests/unit/sources && git commit -m "fix: preserve bounded NTRS source attempts"`

## Self-Review

- Coverage: Tasks 1–3 cover request/response linkage, failure evidence, URL/content/timestamp/reference validation, and byte-cap tests. Task 4 verifies the gate.
- Scope: PostgreSQL queue, executable CLI, document retrieval, OCR, extra source adapters, and candidate screening are excluded.
- Type consistency: Task 1 defines every artefact named by Tasks 2–3.
