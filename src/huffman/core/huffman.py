"""Core Huffman algorithm: frequency counting, tree building, code generation,
encoding and decoding. Operates at the byte level (UTF-8 safe).
"""

from __future__ import annotations

from collections import Counter

from .priority_queue import MinPriorityQueue
from .tree import Node, is_leaf


def count_frequencies(data: bytes) -> dict[int, int]:
    """Count occurrences of each byte value. Time: O(n)."""
    return dict(Counter(data))


def build_tree(freq: dict[int, int]) -> Node | None:
    """Build a Huffman tree from a frequency table.

    Deterministic: leaves are inserted in ascending symbol order and internal
    nodes receive increasing ``order`` values, so the same ``freq`` always
    yields the same tree (required for correct decoding).

    Args:
        freq: Mapping ``symbol -> count`` (count >= 1).

    Returns:
        The root ``Node``, or ``None`` if ``freq`` is empty.
        For a single distinct symbol, the root has one left child (leaf) so the
        symbol gets a valid 1-bit code ``"0"``.
    """
    if not freq:
        return None

    pq = MinPriorityQueue()
    counter = 0
    for symbol in sorted(freq):
        pq.push(Node(freq=freq[symbol], symbol=symbol, order=counter))
        counter += 1

    if len(pq) == 1:
        only = pq.pop()
        return Node(freq=only.freq, left=only, order=counter)

    while len(pq) > 1:
        a = pq.pop()
        b = pq.pop()
        pq.push(Node(freq=a.freq + b.freq, left=a, right=b, order=counter))
        counter += 1
    return pq.pop()


def build_code_table(root: Node | None) -> dict[int, str]:
    """Generate the ``symbol -> codeword`` table by walking the tree.

    Returns an empty table for ``None`` (empty input).
    """
    table: dict[int, str] = {}
    if root is None:
        return table

    def walk(node: Node, prefix: str) -> None:
        if is_leaf(node):
            table[node.symbol] = prefix or "0"
            return
        if node.left is not None:
            walk(node.left, prefix + "0")
        if node.right is not None:
            walk(node.right, prefix + "1")

    walk(root, "")
    return table


def encode(data: bytes, table: dict[int, str]) -> str:
    """Encode bytes into a concatenated bit string using ``table``."""
    return "".join(table[byte] for byte in data)


def decode(bits: str, root: Node | None, total: int) -> bytes:
    """Decode a bit string back into bytes.

    Args:
        bits: Bit string (may include trailing padding bits).
        root: Huffman tree root.
        total: Number of symbols to emit (= sum of frequencies). Decoding stops
            after ``total`` symbols, so padding bits are ignored.

    Returns:
        The decoded bytes.
    """
    out = bytearray()
    if root is None or total == 0:
        return bytes(out)

    node = root
    for ch in bits:
        node = node.left if ch == "0" else node.right
        if node is None:  # malformed stream
            raise ValueError("Corrupted payload: invalid bit path")
        if is_leaf(node):
            out.append(node.symbol)  # type: ignore[arg-type]
            node = root
            if len(out) == total:
                break
    if len(out) != total:
        raise ValueError("Corrupted payload: stream ended before all symbols decoded")
    return bytes(out)
