"""Huffman tree node and helpers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Node:
    """A node in the Huffman tree.

    Attributes:
        freq: Frequency (sum of leaf frequencies in the subtree).
        symbol: Byte value (0..255) for a leaf, ``None`` for an internal node.
        left: Left child (bit ``0``).
        right: Right child (bit ``1``).
        order: Deterministic insertion index used as a tie-break key so that the
            same frequency table always rebuilds the same tree (see
            ``docs/architecture.md``).
    """

    freq: int
    symbol: int | None = None
    left: Node | None = None
    right: Node | None = None
    order: int = 0


def is_leaf(node: Node) -> bool:
    """Return True if ``node`` carries a symbol (has no children)."""
    return node.left is None and node.right is None
