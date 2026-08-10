# ADR-001: Evidence-first CLI MVP

## Status

Accepted

## Context

The project needs a small, reproducible research slice rather than a broad
archive crawler or unverified technology finder.

## Decision

Discovery Run 01 uses Python, PostgreSQL, immutable external SHA-256 storage,
a read-only NASA NTRS/NACA adapter, a fixture adapter, and a CLI. Screening is
not a patent or engineering validation. GitHub tracks source code, decisions,
Issues, and reviews; PostgreSQL and immutable manifests track runtime
provenance.

## Consequences

The project ships more slowly than a scraper prototype, but every later
candidate can be traced to its source and safely reviewed.
