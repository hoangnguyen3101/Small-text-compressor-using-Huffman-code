"""Read/write the ``.huf`` container format (see ``docs/format.md``)."""

from __future__ import annotations

import struct
from pathlib import Path

MAGIC = b"HUF1"
VERSION = 1
_HEADER_FIXED = 7  # MAGIC(4) + VERSION(1) + NSYM(2)
_ENTRY_SIZE = 5  # symbol(1) + freq(4)


def header_size(n_symbols: int) -> int:
    """Byte size of the header for ``n_symbols`` distinct symbols."""
    return _HEADER_FIXED + n_symbols * _ENTRY_SIZE


def serialize(freq: dict[int, int], payload: bytes) -> bytes:
    """Serialize a frequency table and payload into ``.huf`` bytes."""
    parts = [MAGIC, bytes([VERSION]), struct.pack(">H", len(freq))]
    for symbol in sorted(freq):
        parts.append(struct.pack(">BI", symbol, freq[symbol]))
    parts.append(payload)
    return b"".join(parts)


def parse(data: bytes) -> tuple[dict[int, int], bytes]:
    """Parse ``.huf`` bytes into ``(freq, payload)``.

    Raises:
        ValueError: If magic/version is wrong or the header is truncated.
    """
    if len(data) < _HEADER_FIXED or data[:4] != MAGIC:
        raise ValueError("Not a .huf file (bad magic)")
    version = data[4]
    if version != VERSION:
        raise ValueError(f"Unsupported .huf version: {version}")
    (nsym,) = struct.unpack(">H", data[5:7])
    freq: dict[int, int] = {}
    offset = _HEADER_FIXED
    for _ in range(nsym):
        chunk = data[offset : offset + _ENTRY_SIZE]
        if len(chunk) != _ENTRY_SIZE:
            raise ValueError("Corrupted header: truncated frequency table")
        symbol, count = struct.unpack(">BI", chunk)
        freq[symbol] = count
        offset += _ENTRY_SIZE
    payload = data[offset:]
    return freq, payload


def write_huf(path: str | Path, freq: dict[int, int], payload: bytes) -> None:
    """Write a ``.huf`` file to ``path``."""
    Path(path).write_bytes(serialize(freq, payload))


def read_huf(path: str | Path) -> tuple[dict[int, int], bytes]:
    """Read a ``.huf`` file into ``(freq, payload)``."""
    return parse(Path(path).read_bytes())
