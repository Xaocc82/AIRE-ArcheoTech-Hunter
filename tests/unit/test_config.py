from pytest import MonkeyPatch

from aire_archeotech.config import Settings


def test_settings_use_local_postgres_by_default() -> None:
    assert Settings().database_url.startswith("postgresql+")


def test_settings_read_archeotech_database_url(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("ARCHEOTECH_DATABASE_URL", "postgresql+psycopg://example")

    assert Settings().database_url == "postgresql+psycopg://example"
