from importlib import import_module
from io import BytesIO
from pathlib import Path


def test_cas_exposes_storage_type() -> None:
    module = import_module("aire_archeotech.storage.cas")

    assert getattr(module, "ContentAddressedStorage", None) is not None


def test_store_returns_a_blob_for_content(tmp_path: Path) -> None:
    module = import_module("aire_archeotech.storage.cas")
    storage_type = getattr(module, "ContentAddressedStorage")
    storage = storage_type(tmp_path)

    blob = storage.store(BytesIO(b"archive"), "text/plain")

    assert blob is not None
    assert blob.path == (
        tmp_path / "objects" / "sha256" / blob.sha256[:2] / blob.sha256[2:4] / blob.sha256
    )
    assert blob.path.read_bytes() == b"archive"


def test_store_deduplicates_identical_content(tmp_path: Path) -> None:
    module = import_module("aire_archeotech.storage.cas")
    storage_type = getattr(module, "ContentAddressedStorage")
    storage = storage_type(tmp_path)

    first = storage.store(BytesIO(b"archive"), "text/plain")
    second = storage.store(BytesIO(b"archive"), "text/plain")

    assert first == second
