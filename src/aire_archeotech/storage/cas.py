"""Content-addressed artifact storage."""

import os
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import BinaryIO


@dataclass(frozen=True)
class StoredBlob:
    sha256: str
    byte_size: int
    mime_type: str
    path: Path


class ContentAddressedStorage:
    def __init__(self, root: Path) -> None:
        self.root = root

    def store(self, stream: BinaryIO, mime_type: str) -> StoredBlob:
        """Persist a stream once, using its SHA-256 digest as the object key."""
        temporary_dir = self.root / ".tmp"
        temporary_dir.mkdir(parents=True, exist_ok=True)
        digest = sha256()
        byte_size = 0

        with NamedTemporaryFile(dir=temporary_dir, delete=False) as temporary_file:
            temporary_path = Path(temporary_file.name)
            while chunk := stream.read(1_048_576):
                temporary_file.write(chunk)
                digest.update(chunk)
                byte_size += len(chunk)

        digest_hex = digest.hexdigest()
        object_path = (
            self.root / "objects" / "sha256" / digest_hex[:2] / digest_hex[2:4] / digest_hex
        )
        object_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            os.link(temporary_path, object_path)
        except FileExistsError:
            pass
        finally:
            temporary_path.unlink(missing_ok=True)

        return StoredBlob(
            sha256=digest_hex,
            byte_size=byte_size,
            mime_type=mime_type,
            path=object_path,
        )
