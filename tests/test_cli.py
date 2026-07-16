"""Tests for the command-line interface (huffman.cli.main)."""

from __future__ import annotations

from huffman.cli.main import main


def test_cli_compress_decompress_roundtrip(tmp_path, capsys):
    src = tmp_path / "doc.txt"
    original = "CLI round-trip test — Tiếng Việt 😀\n".encode() * 100
    src.write_bytes(original)
    huf = tmp_path / "doc.huf"
    restored = tmp_path / "doc.out"

    assert main(["compress", str(src), "-o", str(huf)]) == 0
    assert main(["decompress", str(huf), "-o", str(restored)]) == 0
    assert restored.read_bytes() == original


def test_cli_stats(tmp_path, capsys):
    src = tmp_path / "doc.txt"
    src.write_bytes(b"abracadabra" * 50)
    assert main(["stats", str(src)]) == 0
    out = capsys.readouterr().out
    assert "Entropy" in out
    assert "Compression ratio" in out


def test_cli_missing_file_returns_error():
    assert main(["decompress", "does_not_exist.huf"]) == 1


def test_cli_bad_format_returns_error(tmp_path):
    bad = tmp_path / "bad.huf"
    bad.write_bytes(b"not a huf file")
    assert main(["decompress", str(bad)]) == 1
