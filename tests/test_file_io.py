"""Unit tests for the .huf container (file_io)."""

from __future__ import annotations

import pytest

from huffman.codec.compressor import compress_bytes
from huffman.container.file_io import MAGIC, parse, serialize


def test_serialize_parse_roundtrip():
    freq, payload = compress_bytes(b"hello world" * 5)
    freq2, payload2 = parse(serialize(freq, payload))
    assert freq2 == freq
    assert payload2 == payload


def test_serialize_starts_with_magic():
    assert serialize({65: 1}, b"\x00").startswith(MAGIC)


def test_parse_bad_magic_raises():
    with pytest.raises(ValueError, match="magic"):
        parse(b"XXXX\x01\x00\x00")


def test_parse_truncated_table_raises():
    # Claims 2 symbols but body is missing.
    data = MAGIC + bytes([1]) + b"\x00\x02"
    with pytest.raises(ValueError):
        parse(data)


def test_empty_input_container():
    freq, payload = compress_bytes(b"")
    freq2, payload2 = parse(serialize(freq, payload))
    assert freq2 == {} and payload2 == b""
