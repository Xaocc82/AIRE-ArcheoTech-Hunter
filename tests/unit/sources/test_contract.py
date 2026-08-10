from importlib.util import find_spec


def test_source_contract_module_exists() -> None:
    try:
        spec = find_spec("aire_archeotech.sources.base")
    except ModuleNotFoundError:
        spec = None

    assert spec is not None
