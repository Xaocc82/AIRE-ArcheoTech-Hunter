from importlib import import_module
from importlib.util import find_spec
from io import BytesIO


def test_hashing_module_exists() -> None:
    try:
        spec = find_spec("aire_archeotech.storage.hashing")
    except ModuleNotFoundError:
        spec = None

    assert spec is not None


def test_sha256_stream_returns_digest_and_byte_count() -> None:
    module = import_module("aire_archeotech.storage.hashing")
    hasher = getattr(module, "sha256_stream", None)

    assert callable(hasher)
    digest, byte_size = hasher(BytesIO(b"archive"), chunk_size=2)
    assert digest == "0eb3e36bfb24dcd9bb1d1bece1531216b59539a8fde17ee80224af0653c92aa3"
    assert byte_size == 7
