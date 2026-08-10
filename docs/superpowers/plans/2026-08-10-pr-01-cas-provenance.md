# PR-01 CAS and Provenance Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Preserve original and derived artifacts outside Git under immutable SHA-256 paths and record reproducible run manifests.

**Architecture:** `hashing.py` streams bytes without loading an entire artifact into memory. `cas.py` writes an artifact atomically to the stable path `objects/sha256/<first-two>/<next-two>/<digest>`, deduplicates repeated content, and returns immutable metadata. `manifests.py` serializes a versioned run description canonically so its hash is reproducible.

**Tech Stack:** Python 3.12+, standard library `hashlib`, `json`, `pathlib`, and pytest.

## Global Constraints

- Never commit CAS objects to Git.
- Never overwrite an existing object for the same SHA-256 digest.
- Use atomic replacement for a newly created artifact.
- A manifest must include the code commit, configuration, source queries, and artifact hashes.
- Tests must not require a network connection, Docker, or PostgreSQL.

---

### Task 1: Stream hash and persist an artifact in CAS

**Files:**
- Create: `src/aire_archeotech/storage/__init__.py`
- Create: `src/aire_archeotech/storage/hashing.py`
- Create: `src/aire_archeotech/storage/cas.py`
- Create: `tests/unit/storage/test_hashing.py`
- Create: `tests/unit/storage/test_cas.py`

**Interfaces:**
- Produces `sha256_stream(stream: BinaryIO, chunk_size: int = 1_048_576) -> tuple[str, int]`.
- Produces `ContentAddressedStorage(root: Path)` and `store(stream: BinaryIO, mime_type: str) -> StoredBlob`.
- `StoredBlob` exposes `sha256`, `byte_size`, `mime_type`, and `path`.

- [ ] **Step 1: Write failing tests**

```python
def test_store_uses_sharded_sha256_path(tmp_path: Path) -> None:
    blob = ContentAddressedStorage(tmp_path).store(BytesIO(b"archive"), "text/plain")
    assert blob.path == tmp_path / "objects" / "sha256" / blob.sha256[:2] / blob.sha256[2:4] / blob.sha256


def test_store_deduplicates_identical_content(tmp_path: Path) -> None:
    store = ContentAddressedStorage(tmp_path)
    first = store.store(BytesIO(b"archive"), "text/plain")
    second = store.store(BytesIO(b"archive"), "text/plain")
    assert first == second
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest tests/unit/storage -v`

Expected: FAIL because the storage package does not exist.

- [ ] **Step 3: Write minimal implementation**

Implement streaming hash calculation and a temporary-file write that atomically
renames to the digest path. If the digest path already exists, delete only the
temporary file and return metadata for the existing object.

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/unit/storage/test_hashing.py tests/unit/storage/test_cas.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/aire_archeotech/storage tests/unit/storage
git commit -m "feat: add content-addressed storage"
```

### Task 2: Create deterministic run manifests

**Files:**
- Create: `src/aire_archeotech/storage/manifests.py`
- Create: `tests/unit/storage/test_manifests.py`
- Modify: `docs/PROVENANCE.md`

**Interfaces:**
- Produces `RunManifest(run_id: str, code_commit: str, configuration: Mapping[str, object], source_queries: tuple[str, ...], artifact_hashes: tuple[str, ...])`.
- Produces `RunManifest.to_json_bytes() -> bytes` and `RunManifest.sha256() -> str`.

- [ ] **Step 1: Write failing test**

```python
def test_manifest_bytes_and_hash_are_deterministic() -> None:
    manifest = RunManifest("run-1", "abc123", {"limit": 25}, ("query",), ("a" * 64,))
    assert manifest.to_json_bytes() == manifest.to_json_bytes()
    assert manifest.sha256() == hashlib.sha256(manifest.to_json_bytes()).hexdigest()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/storage/test_manifests.py -v`

Expected: FAIL because `RunManifest` does not exist.

- [ ] **Step 3: Write minimal implementation**

Serialize a fixed schema using UTF-8 JSON with sorted keys and compact
separators. Validate SHA-256-shaped artifact hashes and write only values
provided by the caller.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/storage/test_manifests.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add src/aire_archeotech/storage/manifests.py tests/unit/storage/test_manifests.py docs/PROVENANCE.md
git commit -m "feat: add deterministic run manifests"
```

### Task 3: Verify the full PR

**Files:**
- Modify: `README.md`

**Interfaces:**
- Documents `ARCHEOTECH_STORAGE_ROOT` as an external path excluded from Git.

- [ ] **Step 1: Write failing test**

```python
def test_readme_forbids_committing_cas_objects() -> None:
    assert "outside Git" in Path("README.md").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_policy_docs.py -v`

Expected: FAIL until the documentation includes the exact phrase.

- [ ] **Step 3: Write minimal implementation**

Document the external `ARCHEOTECH_STORAGE_ROOT` boundary and the local-only
CAS path.

- [ ] **Step 4: Run all verification**

Run: `python -m pytest -v && python -m ruff check . && python -m mypy src && python -m alembic upgrade head --sql`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md tests/unit/test_policy_docs.py
git commit -m "docs: document external artifact storage"
```
