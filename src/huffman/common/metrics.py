"""Compression metrics (see ``docs/theory.md`` for formulas)."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass
class Stats:
    """Compression statistics for one compress/decompress run."""

    original_bytes: int
    compressed_bytes: int
    ratio: float
    space_saving: float
    bpc: float
    entropy: float
    avg_code_length: float
    encode_time: float = 0.0
    decode_time: float = 0.0

    def format_report(self) -> str:
        """Human-readable multi-line summary."""
        return (
            f"Original size    : {self.original_bytes} bytes\n"
            f"Compressed size  : {self.compressed_bytes} bytes\n"
            f"Compression ratio: {self.ratio:.3f} x\n"
            f"Space saving     : {self.space_saving * 100:.2f} %\n"
            f"Bits per char    : {self.bpc:.3f} bit/byte\n"
            f"Entropy (H)      : {self.entropy:.3f} bit/symbol\n"
            f"Avg code length  : {self.avg_code_length:.3f} bit/symbol\n"
            f"Encode time      : {self.encode_time * 1000:.2f} ms\n"
            f"Decode time      : {self.decode_time * 1000:.2f} ms"
        )


def entropy(freq: dict[int, int]) -> float:
    """Shannon entropy in bits/symbol: ``H = -sum p_i log2 p_i``."""
    total = sum(freq.values())
    if total == 0:
        return 0.0
    h = 0.0
    for count in freq.values():
        p = count / total
        h -= p * math.log2(p)
    return h


def avg_code_length(freq: dict[int, int], table: dict[int, str]) -> float:
    """Average code length ``L = sum p_i * len(code_i)`` in bits/symbol."""
    total = sum(freq.values())
    if total == 0:
        return 0.0
    return sum(freq[s] * len(table[s]) for s in freq) / total


def compression_stats(
    original_bytes: int,
    compressed_bytes: int,
    freq: dict[int, int],
    table: dict[int, str],
    encode_time: float = 0.0,
    decode_time: float = 0.0,
) -> Stats:
    """Assemble a :class:`Stats` from sizes and the frequency/code tables.

    ``compressed_bytes`` should be the full ``.huf`` size (header + payload) so
    the header overhead is reflected honestly.
    """
    ratio = original_bytes / compressed_bytes if compressed_bytes else 0.0
    space_saving = 1 - compressed_bytes / original_bytes if original_bytes else 0.0
    bpc = 8 * compressed_bytes / original_bytes if original_bytes else 0.0
    return Stats(
        original_bytes=original_bytes,
        compressed_bytes=compressed_bytes,
        ratio=ratio,
        space_saving=space_saving,
        bpc=bpc,
        entropy=entropy(freq),
        avg_code_length=avg_code_length(freq, table),
        encode_time=encode_time,
        decode_time=decode_time,
    )
