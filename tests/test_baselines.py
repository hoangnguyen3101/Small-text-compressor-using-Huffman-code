"""Tests for RLE and Shannon-Fano baselines (round-trip + properties)."""

from __future__ import annotations

import random

import pytest

from huffman.analysis.baselines import (
    build_sf_codes,
    rle_compress,
    rle_decompress,
    sf_decode,
    sf_encode,
)
from huffman.common.metrics import avg_code_length
from huffman.core.huffman import build_code_table, build_tree, count_frequencies

CASES = [b"", b"a", b"aaaa", b"abracadabra" * 20, bytes(range(256)) * 3]


@pytest.mark.parametrize("data", CASES)
def test_rle_roundtrip(data):
    assert rle_decompress(rle_compress(data)) == data


@pytest.mark.parametrize("data", CASES)
def test_shannon_fano_roundtrip(data):
    freq, bits = sf_encode(data)
    assert sf_decode(freq, bits) == data


@pytest.mark.parametrize("seed", range(10))
def test_shannon_fano_random_roundtrip(seed):
    rng = random.Random(seed)
    data = bytes(rng.randrange(256) for _ in range(rng.randint(0, 2000)))
    freq, bits = sf_encode(data)
    assert sf_decode(freq, bits) == data


def test_sf_codes_are_prefix_free():
    codes = list(build_sf_codes(count_frequencies(b"hello huffman world")).values())
    for i, a in enumerate(codes):
        for j, b in enumerate(codes):
            if i != j:
                assert not a.startswith(b)


def test_huffman_no_worse_than_shannon_fano():
    # Huffman is provably optimal among prefix codes: L_huffman <= L_sf.
    for data in (b"abracadabra" * 50, b"the quick brown fox " * 30):
        freq = count_frequencies(data)
        huff_l = avg_code_length(freq, build_code_table(build_tree(freq)))
        sf_l = avg_code_length(freq, build_sf_codes(freq))
        assert huff_l <= sf_l + 1e-9
