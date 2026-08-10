"""Streaming hash helpers for immutable artifacts."""

from hashlib import sha256
from typing import BinaryIO


def sha256_stream(stream: BinaryIO, chunk_size: int = 1_048_576) -> tuple[str, int]:
    """Return the SHA-256 digest and byte count for a binary stream."""
    digest = sha256()
    byte_size = 0

    while chunk := stream.read(chunk_size):
        digest.update(chunk)
        byte_size += len(chunk)

    return digest.hexdigest(), byte_size
