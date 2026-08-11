# PR-08 Deployment Gate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make PR #8's private container deployment reproducible, smoke-tested, and safe for database credentials containing URL-reserved characters.

**Architecture:** The Compose file passes database components individually rather than interpolating a DSN. `Settings` builds the PostgreSQL URL through SQLAlchemy's `URL.create`, which percent-encodes credentials correctly. Both CI and the Docker image consume the same exact lock graph; a GitHub Actions deployment job validates Compose, builds the image, starts the stack, checks health/storage/non-root execution, and always tears it down.

**Tech Stack:** Python 3.12, FastAPI, Pydantic Settings, SQLAlchemy, Docker Compose, GitHub Actions.

## Global Constraints

- Keep PR #8 scoped to deployment/CI repair; do not merge PR #8 or PR #9 during implementation.
- Pin Python and PostgreSQL Docker Official Images by immutable digests.
- Use the exact build/runtime lock files with `--no-deps` and `--no-build-isolation` in CI and Docker.
- Bind the app only to `127.0.0.1:8088`.
- Do not make live archive requests or add queue/CLI behavior.

---

### Task 1: Freeze the deployment dependency graph

**Files:**
- Modify: `pyproject.toml`
- Create: `requirements-build-ci.lock`
- Create: `requirements-ci.lock`
- Modify: `.github/workflows/ci.yml`

- [ ] Write a failing clean-install command that reproduces the missing `httpx2` dependency.
- [ ] Add `httpx2>=2.0,<3` to the dev extra and exact build/runtime lock files.
- [ ] Pin `hatchling`, its editable-build dependencies, and pip; install lock files with `--no-deps` and `--no-build-isolation`.
- [ ] Add `pip check` to CI.
- [ ] Run the clean installation plus Ruff, mypy, and pytest.

### Task 2: Build a safe database URL from separate settings

**Files:**
- Modify: `src/aire_archeotech/config.py`
- Modify: `compose.production.yaml`
- Modify: `tests/unit/test_config.py`

- [ ] Write a failing test that supplies `@:/#%` in `ARCHEOTECH_DATABASE_PASSWORD` and asserts a valid SQLAlchemy-rendered URL.
- [ ] Replace Compose's `ARCHEOTECH_DATABASE_URL` string interpolation with separate database host/port/name/user/password variables.
- [ ] Build the default URL through `sqlalchemy.engine.URL.create`; preserve `ARCHEOTECH_DATABASE_URL` as an explicit compatibility override.
- [ ] Run the focused config tests, then the full Python suite.

### Task 3: Pin the image inputs and lock Docker installation

**Files:**
- Modify: `Dockerfile`
- Modify: `compose.production.yaml`
- Modify: `tests/unit/runtime/test_deployment_assets.py`

- [ ] Write failing text-level tests requiring digest-pinned Python/PostgreSQL images and lock-file installation flags.
- [ ] Pin `python:3.12-slim` and `postgres:16-alpine` to the documented Docker Hub digests.
- [ ] Copy lock files into the Docker build, install pinned pip/build/runtime graphs, invoke `pip check`, and keep the runtime user non-root with writable storage.
- [ ] Run focused deployment-asset tests and the full Python suite.

### Task 4: Prevent environment-secret variants from entering Git

**Files:**
- Modify: `.gitignore`
- Modify: `tests/unit/runtime/test_deployment_assets.py`

- [ ] Write a failing test for `.env.production.local`, `.env.production.backup`, `.env.server`, and `.env.secret` being ignored while both example files remain allowed.
- [ ] Replace specific env ignores with `.env*` plus explicit example-file allow rules.
- [ ] Run focused tests and validate `git check-ignore` for each secret variant.

### Task 5: Execute the Compose deployment gate in CI

**Files:**
- Create: `.github/scripts/deployment-smoke.sh`
- Modify: `.github/workflows/ci.yml`
- Modify: `README.md`

- [ ] Write a shell-level smoke script that fails if Compose config/build/start/health/storage/non-root/loopback checks fail.
- [ ] Add a GitHub Actions job that runs `docker compose config --quiet`, runs the smoke script, and always tears down volumes.
- [ ] Document the exact local command and precondition that Docker/Compose is required.
- [ ] Run static Python checks locally; rely on the new GitHub Actions job for Docker execution because Docker is unavailable locally.

### Task 6: Verify, commit, and request the PR #8 gate review

**Files:**
- Verify: all modified files

- [ ] Run the lock-based Python installation and `pip check`.
- [ ] Run Ruff, mypy, pytest, and `git diff --check`.
- [ ] Commit the focused deployment repair to `agent/pr-07-deployment-readiness` and push it.
- [ ] Request a refreshed PR #8 review; merge only after an explicit acceptance and green Docker CI.
