# Processing Interfaces Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a deterministic processing worker that extracts embedded PDF text first and exposes a replaceable OCR boundary for scanned pages.

**Architecture:** The processing package separates the queue, text result, PDF extractor, and OCR contract. The initial queue is in-memory and deterministic for unit tests; a PostgreSQL-backed worker will replace its storage layer later without changing processor interfaces. PDF text is extracted by `pypdf`; scanned input returns an explicit `OCR_REQUIRED` result rather than silently claiming text was recovered.

**Tech Stack:** Python 3.12+, pypdf, pytest, Ruff, mypy.

## Global Constraints

- Accept only lawful, public source materials; do not bypass source controls.
- Preserve provenance: extraction result identifies engine and version.
- OCR is a screening aid, not proof of historical function, novelty, or legal status.
- Do not download models or archive originals into Git.

---

### Task 1: Define extraction and OCR contracts

**Files:**
- Create: `tests/unit/processing/test_contracts.py`
- Create: `src/aire_archeotech/processing/base.py`
- Create: `src/aire_archeotech/processing/__init__.py`

**Interfaces:** Produces `ExtractionStatus`, `ExtractedText`, `PdfTextExtractor`, and `OcrEngine`.

- [ ] Write a failing test for an extracted text result that records engine identity.
- [ ] Run `python -m pytest tests/unit/processing/test_contracts.py -q`; expect failure because the package is absent.
- [ ] Implement minimal immutable result and protocol types.
- [ ] Re-run the targeted test; expect pass.

### Task 2: Extract embedded PDF text

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/unit/processing/test_pdf_text.py`
- Create: `src/aire_archeotech/processing/pdf_text.py`

**Interfaces:** Consumes `ExtractedText` and `ExtractionStatus`; produces `PypdfTextExtractor.extract(document: bytes) -> ExtractedText`.

- [ ] Write a failing test that builds a one-page PDF with embedded text and checks that exact text is extracted.
- [ ] Run `python -m pytest tests/unit/processing/test_pdf_text.py -q`; expect missing extractor failure.
- [ ] Add `pypdf`, then implement extraction. Empty embedded text must return `OCR_REQUIRED`.
- [ ] Re-run the targeted test; expect pass.

### Task 3: Add a deterministic processing queue

**Files:**
- Create: `tests/unit/processing/test_queue.py`
- Create: `src/aire_archeotech/processing/queue.py`

**Interfaces:** Produces `InMemoryProcessingQueue.submit`, `claim_next`, and `complete` with single-claim semantics.

- [ ] Write a failing test showing one submitted job can be claimed only once, and completion stores its result.
- [ ] Run `python -m pytest tests/unit/processing/test_queue.py -q`; expect missing queue failure.
- [ ] Implement the smallest FIFO queue with explicit job states and immutable payload records.
- [ ] Re-run the targeted test; expect pass.

### Task 4: Verify and publish the focused increment

**Files:**
- Create: `tests/unit/processing/test_worker.py`
- Create: `src/aire_archeotech/processing/worker.py`

- [ ] Write a failing test that submits a document, runs one worker iteration, and asserts a completed job contains the extractor result.
- [ ] Run `python -m pytest tests/unit/processing/test_worker.py -q`; expect missing worker failure.
- [ ] Implement `ProcessingWorker.run_once()` by claiming a job, invoking its injected `PdfTextExtractor`, then completing it.
- [ ] Re-run the targeted test; expect pass.

### Task 5: Verify and publish the focused increment

**Files:**
- Modify: `README.md`

- [ ] Document that embedded PDF text uses pypdf and OCR engines are optional configuration outside Git.
- [ ] Run `python -m ruff check .`, `python -m mypy src`, and `python -m pytest -q`; all must exit 0.
- [ ] Commit only the processing, test, plan, dependency, and README files; push a draft PR based on `agent/pr-03-nasa-ntrs`.
