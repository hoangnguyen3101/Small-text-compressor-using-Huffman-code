"""Unit tests for priority queue, tree and bitstream."""

from __future__ import annotations

from huffman.container.bitstream import BitReader, pack_bits, unpack_bits
from huffman.core.priority_queue import MinPriorityQueue
from huffman.core.tree import Node, is_leaf


def test_priority_queue_pops_in_frequency_order():
    pq = MinPriorityQueue()
    pq.push(Node(freq=5, symbol=1, order=0))
    pq.push(Node(freq=1, symbol=2, order=1))
    pq.push(Node(freq=3, symbol=3, order=2))
    assert [pq.pop().freq for _ in range(3)] == [1, 3, 5]


def test_priority_queue_tie_break_by_order():
    pq = MinPriorityQueue()
    pq.push(Node(freq=2, symbol=1, order=1))
    pq.push(Node(freq=2, symbol=2, order=0))
    assert pq.pop().order == 0  # same freq -> lower order first


def test_is_leaf():
    leaf = Node(freq=1, symbol=65)
    internal = Node(freq=2, left=leaf)
    assert is_leaf(leaf)
    assert not is_leaf(internal)


def test_pack_unpack_roundtrip():
    bits = "1011001110001"
    packed = pack_bits(bits)
    # unpack pads to a multiple of 8; original prefix must be preserved.
    assert unpack_bits(packed).startswith(bits)


def test_pack_empty():
    assert pack_bits("") == b""
    assert unpack_bits(b"") == ""


def test_bitreader_reads_all_then_none():
    reader = BitReader(bytes([0b10100000]))
    assert reader.read_bit() == "1"
    assert reader.read_bit() == "0"
    for _ in range(6):
        reader.read_bit()
    assert reader.read_bit() is None
