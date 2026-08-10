# AIRE ArcheoTech Hunter

Evidence-first research pipeline for lawful, public historical technology
archives. Discovery Run 01 begins with a single read-only NASA NTRS/NACA
adapter and a deterministic local fixture adapter.

## Development

Requires Python 3.12 or newer. Create an environment, then install the
project and developer tools:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest
```

PostgreSQL is supplied separately for local integration work:

```powershell
docker compose up -d postgres
```

The first CLI command is intentionally small:

```powershell
archeotech --help
```

## Processing boundary

The initial worker uses `pypdf` to extract text that is already embedded in a
PDF. A PDF without an embedded text layer is explicitly marked as requiring
OCR; it is never treated as successfully transcribed. OCR engines and any
local model files are optional runtime configuration, remain outside Git, and
must preserve the engine identity in each resulting record.

## Evidence dossiers

Candidate dossiers bind each quoted statement to an original artifact hash,
source URL, document reference, page, and character span. They are auditable
research records for human review—not legal, novelty, functionality, or
engineering conclusions.

## Data boundary

Downloaded archive originals and production content-addressed storage stay
outside Git. Read [the source policy](docs/SOURCE_POLICY.md) before adding an
adapter and [the provenance policy](docs/PROVENANCE.md) before adding a data
model.
