# Deployment Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Package the CLI-first research pipeline as a container with a private health endpoint so it can be verified on the local server without exposing a public web application.

**Architecture:** A minimal FastAPI application provides only liveness metadata at `/healthz`; it does not expose source ingestion, archives, screening, or user data. A non-root Python 3.12 container runs the application, and the production Compose file binds its port to loopback while provisioning PostgreSQL and persistent, external-to-Git storage volumes.

**Tech Stack:** Python 3.12, FastAPI, Uvicorn, Docker, Docker Compose, PostgreSQL 16.

## Global Constraints

- Keep the service private: bind `127.0.0.1` only until a domain, TLS proxy, and firewall policy are explicitly configured.
- Never commit secrets, database data, archive originals, or CAS content.
- Preserve CLI-first scope; `/healthz` is operational telemetry, not a browser UI or research API.
- Run as an unprivileged container user and use immutable image dependencies.

---

### Task 1: Add a tested liveness endpoint

**Files:**
- Modify: `pyproject.toml`
- Create: `tests/unit/runtime/test_health.py`
- Create: `src/aire_archeotech/runtime/app.py`
- Create: `src/aire_archeotech/runtime/__init__.py`

- [ ] Write a failing test asserting `GET /healthz` returns a stable `200` JSON payload without database access.
- [ ] Run `python -m pytest tests/unit/runtime/test_health.py -q`; expect missing app failure.
- [ ] Add FastAPI/Uvicorn and implement the smallest no-data health application.
- [ ] Re-run the targeted test; expect pass.

### Task 2: Add private container deployment assets

**Files:**
- Create: `Dockerfile`
- Create: `compose.production.yaml`
- Create: `.env.production.example`
- Modify: `.gitignore`
- Create: `tests/unit/runtime/test_deployment_assets.py`

- [ ] Write failing tests that require a non-root Dockerfile, loopback-only port mapping, and no committed production env file.
- [ ] Run `python -m pytest tests/unit/runtime/test_deployment_assets.py -q`; expect missing assets failure.
- [ ] Implement the smallest image and Compose configuration with PostgreSQL health checks and persistent named volumes.
- [ ] Re-run the targeted test; expect pass.

### Task 3: Verify and deploy privately

**Files:**
- Modify: `README.md`

- [ ] Document the private deployment command and restriction.
- [ ] Run `python -m ruff check .`, `python -m mypy src`, and `python -m pytest -q`; all must exit 0.
- [ ] Push a draft PR based on `agent/pr-06-screening`. After review and merge, clone `main` into a dedicated server directory, create `.env.production` on the server, and run `docker compose -f compose.production.yaml up -d --build`.
- [ ] Verify only from the server itself with `curl http://127.0.0.1:8088/healthz`; do not add public firewall rules.
