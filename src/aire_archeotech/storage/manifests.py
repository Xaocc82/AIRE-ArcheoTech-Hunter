"""Deterministic research-run manifests."""

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
from json import dumps


@dataclass(frozen=True)
class RunManifest:
    run_id: str
    code_commit: str
    configuration: Mapping[str, object]
    source_queries: tuple[str, ...]
    artifact_hashes: tuple[str, ...]

    def __post_init__(self) -> None:
        for artifact_hash in self.artifact_hashes:
            if len(artifact_hash) != 64 or any(
                character not in "0123456789abcdef" for character in artifact_hash
            ):
                raise ValueError("artifact hashes must be lowercase SHA-256 hex digests")

    def to_json_bytes(self) -> bytes:
        payload = {
            "artifact_hashes": self.artifact_hashes,
            "code_commit": self.code_commit,
            "configuration": self.configuration,
            "run_id": self.run_id,
            "source_queries": self.source_queries,
        }
        json_text = dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return json_text.encode("utf-8")

    def sha256(self) -> str:
        return sha256(self.to_json_bytes()).hexdigest()
