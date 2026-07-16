"""Deterministic min priority queue over Huffman ``Node`` objects.

Wraps :mod:`heapq`. Ordering key is ``(freq, order)`` so ties break by insertion
index, never by comparing ``Node`` objects — guaranteeing a reproducible tree.
"""

from __future__ import annotations

import heapq

from .tree import Node


class MinPriorityQueue:
    """A min-heap keyed by ``(node.freq, node.order)``."""

    def __init__(self) -> None:
        self._heap: list[tuple[int, int, Node]] = []

    def push(self, node: Node) -> None:
        """Insert a node. Time: O(log n)."""
        heapq.heappush(self._heap, (node.freq, node.order, node))

    def pop(self) -> Node:
        """Remove and return the node with the smallest ``(freq, order)``.

        Raises:
            IndexError: If the queue is empty.
        """
        return heapq.heappop(self._heap)[2]

    def __len__(self) -> int:
        return len(self._heap)
