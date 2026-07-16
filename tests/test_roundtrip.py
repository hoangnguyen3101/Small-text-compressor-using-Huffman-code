"""Integration + property/randomized round-trip tests (the core guarantee)."""

from __future__ import annotations

import os
import random

import pytest

from huffman.codec.compressor import compress_bytes, compress_file
from huffman.codec.decompressor import decompress_bytes, decompress_file

EDGE_CASES = {
    "empty": b"",
    "one_char": b"a",
    "single_symbol_repeated": b"z" * 5000,
    "two_symbols": b"ab" * 1000,
    "ascii_text": b"the quick brown fox jumps over the lazy dog. " * 100,
    "unicode_vietnamese": "Tiếng Việt có dấu! 😀🎉 Huffman.".encode() * 50,
    "all_byte_values": bytes(range(256)) * 4,
}


@pytest.mark.parametrize("name", list(EDGE_CASES))
def test_roundtrip_edge_cases(name):
    data = EDGE_CASES[name]
    freq, payload = compress_bytes(data)
    assert decompress_bytes(freq, payload) == data


@pytest.mark.parametrize("seed", range(25))
def test_roundtrip_random(seed):
    rng = random.Random(seed)
    size = rng.randint(0, 4000)
    data = bytes(rng.randrange(256) for _ in range(size))
    freq, payload = compress_bytes(data)
    assert decompress_bytes(freq, payload) == data


def test_roundtrip_urandom_large():
    data = os.urandom(100_000)
    freq, payload = compress_bytes(data)
    assert decompress_bytes(freq, payload) == data


def test_file_roundtrip(tmp_path):
    src = tmp_path / "input.txt"
    original = "Xin chào! Hello Huffman. ".encode() * 200
    src.write_bytes(original)

    stats = compress_file(src)
    huf = tmp_path / "input.txt.huf"
    assert huf.exists()
    assert stats.original_bytes == len(original)

    out, _ = decompress_file(huf, tmp_path / "restored.txt")
    assert out.read_bytes() == original


def test_compression_actually_shrinks_redundant_text():
    data = b"aaaabbbbcccc" * 1000
    freq, payload = compress_bytes(data)
    from huffman.container.file_io import header_size

    compressed = header_size(len(freq)) + len(payload)
    assert compressed < len(data)
