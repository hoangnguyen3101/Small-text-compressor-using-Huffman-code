"""Decompression: ``.huf`` -> bytes/file."""

from __future__ import annotations

from pathlib import Path

from ..common.utils import Timer
from ..container.bitstream import unpack_bits
from ..container.file_io import read_huf
from ..core.huffman import build_tree, decode


def decompress_bytes(freq: dict[int, int], payload: bytes) -> bytes:
    """Reconstruct the original bytes from a frequency table and payload."""
    root = build_tree(freq)
    total = sum(freq.values())
    return decode(unpack_bits(payload), root, total)


def default_output(src: Path) -> Path:
    """Default decompressed path: strip a trailing ``.huf`` else append ``.out``."""
    name = str(src)
    if name.endswith(".huf"):
        return Path(name[: -len(".huf")])
    return Path(name + ".out")


def decompress_file(src: str | Path, dst: str | Path | None = None) -> tuple[Path, float]:
    """Decompress a ``.huf`` file; return ``(output_path, decode_time_seconds)``."""
    src = Path(src)
    freq, payload = read_huf(src)
    with Timer() as timer:
        data = decompress_bytes(freq, payload)
    out = Path(dst) if dst is not None else default_output(src)
    out.write_bytes(data)
    return out, timer.elapsed
