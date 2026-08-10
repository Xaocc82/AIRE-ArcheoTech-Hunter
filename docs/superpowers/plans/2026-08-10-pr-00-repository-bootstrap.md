# PR-00 Repository Bootstrap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a reproducible Python foundation for the Discovery Run 01 evidence-first research pipeline.

**Architecture:** A Python `src/` package exposes a small CLI and imports no project-specific infrastructure yet. PostgreSQL and Alembic configuration are included for local development, while policy documents define the non-negotiable provenance, source-access, and Git-data boundaries before adapters or ingestion are introduced.

**Tech Stack:** Python 3.12+, Typer, Pydantic Settings, SQLAlchemy, Alembic, PostgreSQL 16, pytest, Ruff, mypy, GitHub Actions.

## Global Constraints

- All archive access is read-only and legal.
- Git never stores downloaded archival originals or production CAS objects.
- Production claims must always be traceable to a source artifact, page, and span.
- Default tests perform no live network calls.
- Python requirement is `>=3.12`; local verification may use Python 3.13.

---

### Task 1: Package and developer tooling

**Files:**
- Create: `pyproject.toml`
- Create: `src/aire_archeotech/__init__.py`
- Create: `src/aire_archeotech/cli.py`
- Create: `tests/unit/test_cli.py`
- Create: `.gitignore`
- Create: `.env.example`

**Interfaces:**
- Produces `main() -> None`, registered as the `archeotech` console script.
- Consumes no runtime services.

- [ ] **Step 1: Write the failing test**

```python
from typer.testing import CliRunner

from aire_archeotech.cli import app


def test_cli_prints_project_identity() -> None:
    result = CliRunner().invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "AIRE ArcheoTech Hunter" in result.output
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_cli.py -v`

Expected: FAIL because `aire_archeotech` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
import typer

app = typer.Typer(help="AIRE ArcheoTech Hunter research CLI.")


def main() -> None:
    app()
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/test_cli.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/aire_archeotech tests/unit/test_cli.py .gitignore .env.example
git commit -m "chore: bootstrap Python package"
```

### Task 2: Database and migration foundation

**Files:**
- Create: `compose.yaml`
- Create: `alembic.ini`
- Create: `src/aire_archeotech/config.py`
- Create: `src/aire_archeotech/db/session.py`
- Create: `migrations/env.py`
- Create: `migrations/versions/.gitkeep`
- Create: `tests/unit/test_config.py`

**Interfaces:**
- Produces `Settings.database_url: str` and `create_engine_from_settings(settings: Settings) -> Engine`.
- Consumes `ARCHEOTECH_DATABASE_URL` with a local PostgreSQL default.

- [ ] **Step 1: Write the failing test**

```python
from aire_archeotech.config import Settings


def test_settings_use_local_postgres_by_default() -> None:
    assert Settings().database_url.startswith("postgresql+")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_config.py -v`

Expected: FAIL because `Settings` does not exist.

- [ ] **Step 3: Write minimal implementation**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://archeotech:archeotech@localhost:5432/archeotech"
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/test_config.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add compose.yaml alembic.ini migrations src/aire_archeotech/config.py src/aire_archeotech/db tests/unit/test_config.py
git commit -m "chore: add database foundation"
```

### Task 3: Policies, ADR, and automated verification

**Files:**
- Create: `README.md`
- Create: `docs/MVP.md`
- Create: `docs/SOURCE_POLICY.md`
- Create: `docs/PROVENANCE.md`
- Create: `docs/adr/001-evidence-first-mvp.md`
- Create: `.github/workflows/ci.yml`
- Create: `tests/unit/test_policy_docs.py`

**Interfaces:**
- Produces a documented local setup command and policy texts used by later source adapters.
- Consumes only repository files.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_source_policy_prohibits_uncontrolled_crawling() -> None:
    policy = Path("docs/SOURCE_POLICY.md").read_text(encoding="utf-8")
    assert "uncontrolled crawling" in policy
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_policy_docs.py -v`

Expected: FAIL because `SOURCE_POLICY.md` does not exist.

- [ ] **Step 3: Write minimal implementation**

Write the policy documents with the legal boundaries from the approved MVP and
add CI steps for Ruff, mypy, and pytest.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md docs .github tests/unit/test_policy_docs.py
git commit -m "docs: define evidence-first MVP policies"
```

### Task 4: Verify the bootstrap as a clean clone

**Files:**
- Modify: `README.md`
- Modify: `docs/MVP.md`

**Interfaces:**
- Produces exact local verification commands and records unavailable tools.
- Consumes the completed package and CI configuration.

- [ ] **Step 1: Write the failing test**

```python
from pathlib import Path


def test_readme_documents_test_command() -> None:
    assert "python -m pytest" in Path("README.md").read_text(encoding="utf-8")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/test_policy_docs.py -v`

Expected: FAIL until the README contains the command.

- [ ] **Step 3: Write minimal implementation**

Document venv creation, dependency installation, test execution, and the
separate `docker compose up` requirement for PostgreSQL.

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest -v && python -m ruff check . && python -m mypy src`

Expected: PASS; if Docker is unavailable, document that its compose service
cannot be exercised locally.

- [ ] **Step 5: Commit**

```bash
git add README.md docs/MVP.md tests/unit/test_policy_docs.py
git commit -m "docs: record bootstrap verification"
```
