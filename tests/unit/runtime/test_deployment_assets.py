from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[3]


def test_dockerfile_runs_as_unprivileged_user() -> None:
    dockerfile = (PROJECT_ROOT / "Dockerfile").read_text(encoding="utf-8")

    assert "USER archeotech" in dockerfile
    assert "chown -R archeotech:archeotech /var/lib/aire-archeotech" in dockerfile
    assert "uvicorn" in dockerfile


def test_production_compose_binds_application_to_loopback_only() -> None:
    compose = (PROJECT_ROOT / "compose.production.yaml").read_text(encoding="utf-8")

    assert '"127.0.0.1:8088:8088"' in compose
    assert "service_healthy" in compose


def test_production_environment_file_is_not_committed() -> None:
    gitignore = (PROJECT_ROOT / ".gitignore").read_text(encoding="utf-8")
    dockerignore = (PROJECT_ROOT / ".dockerignore").read_text(encoding="utf-8")

    assert ".env.production" in gitignore
    assert ".env*" in dockerignore
    assert not (PROJECT_ROOT / ".env.production").exists()


def test_readme_uses_explicit_production_environment_file() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    command = "docker compose --env-file .env.production -f compose.production.yaml up -d --build"
    assert command in readme
