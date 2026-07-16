"""Command-line interface for the Huffman text compressor.

Usage:
    python -m huffman.main compress   <src> [-o OUT] [--verbose]
    python -m huffman.main decompress <src.huf> [-o OUT] [--verbose]
    python -m huffman.main stats      <src> [--verbose]
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from ..codec.compressor import compress_bytes, compress_file
from ..common.metrics import compression_stats
from ..common.utils import get_logger
from ..container.file_io import header_size
from ..core.huffman import build_code_table, build_tree, count_frequencies


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="huffman", description="Small text compressor using Huffman coding."
    )
    parser.add_argument("--verbose", action="store_true", help="Enable DEBUG logging.")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_c = sub.add_parser("compress", help="Compress a file to .huf")
    p_c.add_argument("src", type=Path)
    p_c.add_argument("-o", "--output", type=Path, default=None)

    p_d = sub.add_parser("decompress", help="Decompress a .huf file")
    p_d.add_argument("src", type=Path)
    p_d.add_argument("-o", "--output", type=Path, default=None)

    p_s = sub.add_parser("stats", help="Show compression statistics without writing")
    p_s.add_argument("src", type=Path)

    return parser


def _stats_only(src: Path) -> str:
    data = src.read_bytes()
    freq = count_frequencies(data)
    table = build_code_table(build_tree(freq))
    _, payload = compress_bytes(data)
    compressed = header_size(len(freq)) + len(payload)
    stats = compression_stats(len(data), compressed, freq, table)
    return stats.format_report()


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code (0 = success)."""
    parser = _build_parser()
    args = parser.parse_args(argv)

    level = logging.DEBUG if args.verbose else getattr(logging, args.log_level)
    logger = get_logger("huffman", level)

    try:
        if args.command == "compress":
            stats = compress_file(args.src, args.output)
            out = args.output or Path(str(args.src) + ".huf")
            logger.info("Compressed %s -> %s", args.src, out)
            print(stats.format_report())

        elif args.command == "decompress":
            from ..codec.decompressor import decompress_file

            out, decode_time = decompress_file(args.src, args.output)
            logger.info("Decompressed %s -> %s (%.2f ms)", args.src, out, decode_time * 1000)
            print(f"Decompressed -> {out}")

        elif args.command == "stats":
            print(_stats_only(args.src))

    except FileNotFoundError as exc:
        logger.error("File not found: %s", exc.filename)
        return 1
    except ValueError as exc:
        logger.error("Invalid input: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
