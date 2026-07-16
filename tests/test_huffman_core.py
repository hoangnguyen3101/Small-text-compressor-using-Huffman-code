"""Unit tests for the core Huffman algorithm."""

from __future__ import annotations

import math

import pytest

from huffman.common.metrics import avg_code_length, entropy
from huffman.core.huffman import (
    build_code_table,
    build_tree,
    count_frequencies,
    decode,
    encode,
)


def test_count_frequencies():
    assert count_frequencies(b"aab") == {ord("a"): 2, ord("b"): 1}
    assert count_frequencies(b"") == {}


def test_build_tree_empty_returns_none():
    assert build_tree({}) is None


def test_single_symbol_gets_one_bit_code():
    table = build_code_table(build_tree({ord("a"): 5}))
    assert table == {ord("a"): "0"}


def test_code_table_is_prefix_free():
    freq = count_frequencies(b"abracadabra" * 10)
    codes = list(build_code_table(build_tree(freq)).values())
    for i, a in enumerate(codes):
        for j, b in enumerate(codes):
            if i != j:
                assert not a.startswith(b), f"{a} is prefixed by {b}"


def test_clrs_example_is_optimal():
    # Classic CLRS frequencies -> known optimal weighted path length = 224.
    freq = {
        ord("a"): 45,
        ord("b"): 13,
        ord("c"): 12,
        ord("d"): 16,
        ord("e"): 9,
        ord("f"): 5,
    }
    table = build_code_table(build_tree(freq))
    weighted = sum(freq[s] * len(table[s]) for s in freq)
    assert weighted == 224
    assert math.isclose(avg_code_length(freq, table), 2.24)
    # 'a' is most frequent -> shortest code.
    assert len(table[ord("a")]) == 1


def test_encode_decode_roundtrip():
    data = b"the quick brown fox"
    freq = count_frequencies(data)
    root = build_tree(freq)
    table = build_code_table(root)
    bits = encode(data, table)
    assert decode(bits, root, sum(freq.values())) == data


def test_entropy_of_uniform_two_symbols():
    assert math.isclose(entropy({0: 1, 1: 1}), 1.0)


def test_decode_corrupted_raises():
    freq = count_frequencies(b"abc")
    root = build_tree(freq)
    with pytest.raises(ValueError):
        decode("", root, 3)  # not enough bits
