"""Baseline compressors for benchmarking against Huffman.

- RLE (run-length encoding): byte-level, demonstrates best/worst cases.
- Shannon-Fano: entropy coder that Huffman provably matches or beats.

Both provide round-trippable compress/decompress at the byte level so the
benchmark can verify losslessness. They reuse the ``.huf``-style frequency
header only conceptually; sizes are reported by the benchmark.
"""

from __future__ import annotations

from ..core.huffman import count_frequencies, decode, encode
from ..core.tree import Node

# --------------------------------------------------------------------------- #
# Run-Length Encoding
# --------------------------------------------------------------------------- #


def rle_compress(data: bytes) -> bytes:
    """Encode ``data`` as ``(count, byte)`` pairs, runs capped at 255."""
    out = bytearray()
    i, n = 0, len(data)
    while i < n:
        byte = data[i]
        run = 1
        while i + run < n and data[i + run] == byte and run < 255:
            run += 1
        out.append(run)
        out.append(byte)
        i += run
    return bytes(out)


def rle_decompress(data: bytes) -> bytes:
    """Inverse of :func:`rle_compress`."""
    out = bytearray()
    for i in range(0, len(data), 2):
        out.extend([data[i + 1]] * data[i])
    return bytes(out)


# --------------------------------------------------------------------------- #
# Shannon-Fano coding
# --------------------------------------------------------------------------- #


def build_sf_codes(freq: dict[int, int]) -> dict[int, str]:
    """Build Shannon-Fano codes: recursively split symbols (sorted by frequency
    descending) into two groups of near-equal total frequency.
    """
    if not freq:
        return {}
    if len(freq) == 1:
        return {next(iter(freq)): "0"}

    items = sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))
    codes: dict[int, str] = {sym: "" for sym, _ in items}

    def split(group: list[tuple[int, int]]) -> None:
        if len(group) == 1:
            return
        total = sum(f for _, f in group)
        acc = 0
        best_diff: int | None = None
        cut = 1
        for k in range(len(group) - 1):
            acc += group[k][1]
            diff = abs(total - 2 * acc)
            if best_diff is None or diff < best_diff:
                best_diff = diff
                cut = k + 1
        left, right = group[:cut], group[cut:]
        for sym, _ in left:
            codes[sym] += "0"
        for sym, _ in right:
            codes[sym] += "1"
        split(left)
        split(right)

    split(items)
    return codes


def _tree_from_codes(codes: dict[int, str]) -> Node | None:
    """Reconstruct a decoding tree from a prefix code table."""
    if not codes:
        return None
    root = Node(0)
    for sym, code in codes.items():
        node = root
        for bit in code:
            if bit == "0":
                node.left = node.left or Node(0)
                node = node.left
            else:
                node.right = node.right or Node(0)
                node = node.right
        node.symbol = sym
    return root


def sf_encode(data: bytes) -> tuple[dict[int, int], str]:
    """Return ``(freq, bitstring)`` for Shannon-Fano encoding of ``data``."""
    freq = count_frequencies(data)
    codes = build_sf_codes(freq)
    return freq, encode(data, codes)


def sf_decode(freq: dict[int, int], bits: str) -> bytes:
    """Inverse of :func:`sf_encode` given the frequency table."""
    codes = build_sf_codes(freq)
    root = _tree_from_codes(codes)
    return decode(bits, root, sum(freq.values()))
