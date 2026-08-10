# Discovery Run 01 — Design

## Decision

Build a local, evidence-first research pipeline for legal, public historical
technical records. Discovery Run 01 is deliberately a thin vertical slice:
one real, read-only source adapter (NASA NTRS filtered to NACA records from
1915–1950), one deterministic fixture adapter, and a CLI. The product does
not claim novelty, patent freedom, or technical feasibility.

## Scope

The first implementation starts with PR-00, the repository foundation. It
establishes Python packaging, a PostgreSQL development service, a migration
framework, continuous integration, and the project policies that constrain
all later changes.

Subsequent increments are separately reviewable:

1. Immutable SHA-256 content-addressed storage and run manifests.
2. A source-adapter contract and fixture adapter.
3. NASA NTRS/NACA metadata search and opt-in, rate-limited live smoke test.
4. PostgreSQL job queue and text/OCR abstraction.
5. Evidence spans, candidate cards, and deterministic JSON/Markdown exports.
6. Patent, engineering, and safety screening interfaces.

## Architecture

The package is `aire_archeotech`. Domain rules are pure Python and are kept
independent of HTTP, storage, and database details. Source adapters implement
a read-only contract and preserve raw request/response artifacts. PostgreSQL
is the operational ledger for sources, runs, records, jobs, candidates, and
audit events; immutable originals and derived artifacts live in an external
SHA-256 content-addressed store, never in Git.

Every archival claim must eventually resolve to an original artifact hash,
document, physical PDF page, and exact evidence span. Derived text, OCR,
translations, and model interpretations remain distinct from the original.

## Safety and legal boundary

- Accept only user-uploaded or officially public, permitted records.
- Adapters are read-only, allowlisted, rate limited, and bounded by result,
  document, total-byte, and single-asset limits.
- Do not bypass access controls, crawl uncontrolled sites, or ingest leaks.
- Dangerous operational material is outside the ordinary candidate workflow
  and will require a future safety gate.
- Screening results use only `PASS_FOR_RESEARCH`, `HOLD`, `REJECT`, or
  `UNKNOWN`; they are not legal or engineering conclusions.

## MVP non-goals

No browser UI, graph database, vector database, mass ingestion, handwritten
or historic-script OCR, automated patent conclusions, prototype generation,
or production-system integration belongs to Discovery Run 01.

## Validation

Tests must be deterministic and network-free by default. Live NASA tests are
opt-in. The foundation verifies package installation, CLI invocation, policy
loading, and migration configuration; later increments add idempotency,
provenance, adapter-contract, and full vertical-slice acceptance tests.
