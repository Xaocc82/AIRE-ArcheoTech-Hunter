from importlib.util import find_spec


def test_storage_module_exists() -> None:
    try:
        spec = find_spec("aire_archeotech.storage.cas")
    except ModuleNotFoundError:
        spec = None

    assert spec is not None
