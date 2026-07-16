"""Compression orchestration: bytes/file -> ``.huf``."""

from __future__ import annotations

from pathlib import Path

from ..common.metrics import Stats, compression_stats
from ..common.utils import Timer
from ..container.bitstream import pack_bits
from ..container.file_io import header_size, write_huf
from ..core.huffman import build_code_table, build_tree, count_frequencies, encode


def compress_bytes(data: bytes) -> tuple[dict[int, int], bytes]:
    """Compress raw bytes; return ``(freq, payload)`` for the ``.huf`` container."""
    freq = count_frequencies(data)
    root = build_tree(freq)
    table = build_code_table(root)
    payload = pack_bits(encode(data, table))
    return freq, payload


def default_output(src: Path) -> Path:
    """Default compressed path: append ``.huf`` to the source name."""
    return Path(str(src) + ".huf")


def compress_file(src: str | Path, dst: str | Path | None = None) -> Stats:
    """Compress ``src`` into a ``.huf`` file and return statistics.

    Args:
        src: Path to the input file.
        dst: Output path; defaults to ``<src>.huf``.
    """
    src = Path(src)
    data = src.read_bytes()
    freq = count_frequencies(data)
    with Timer() as timer:
        root = build_tree(freq)
        table = build_code_table(root)
        payload = pack_bits(encode(data, table))
    out = Path(dst) if dst is not None else default_output(src)
    write_huf(out, freq, payload)

    compressed = header_size(len(freq)) + len(payload)
    return compression_stats(
        original_bytes=len(data),
        compressed_bytes=compressed,
        freq=freq,
        table=table,
        encode_time=timer.elapsed,
    )
