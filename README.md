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

## Data boundary

Downloaded archive originals and production content-addressed storage stay
outside Git. Read [the source policy](docs/SOURCE_POLICY.md) before adding an
adapter and [the provenance policy](docs/PROVENANCE.md) before adding a data
model.
