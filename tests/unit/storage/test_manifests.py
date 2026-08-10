from importlib import import_module
from importlib.util import find_spec


def test_manifest_module_exists() -> None:
    try:
        spec = find_spec("aire_archeotech.storage.manifests")
    except ModuleNotFoundError:
        spec = None

    assert spec is not None


def test_manifest_bytes_and_hash_are_deterministic() -> None:
    module = import_module("aire_archeotech.storage.manifests")
    manifest_type = getattr(module, "RunManifest", None)

    assert manifest_type is not None
    manifest = manifest_type(
        run_id="run-1",
        code_commit="abc123",
        configuration={"document_limit": 25},
        source_queries=("experimental AND impracticable",),
        artifact_hashes=("a" * 64,),
    )
    assert manifest.to_json_bytes() == manifest.to_json_bytes()
    assert len(manifest.sha256()) == 64
