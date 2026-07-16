"""Huffman text compressor — small, lossless, order-0 static Huffman coding.

Public API re-exported from subpackages (see docs/architecture.md):
    core/       algorithm + data structures
    container/  bit packing + .huf format
    codec/      compress / decompress orchestration
    common/     shared utilities + metrics
    analysis/   baselines, benchmark, visualization
    cli/        command-line interface

Importing this package has no side effects.
"""

from __future__ import annotations

from .codec.compressor import compress_bytes, compress_file
from .codec.decompressor import decompress_bytes, decompress_file
from .common.metrics import Stats, avg_code_length, compression_stats, entropy
from .core.huffman import build_code_table, build_tree, count_frequencies, decode, encode
from .core.tree import Node, is_leaf

__version__ = "1.0.0"

__all__ = [
    "__version__",
    "compress_bytes",
    "compress_file",
    "decompress_bytes",
    "decompress_file",
    "count_frequencies",
    "build_tree",
    "build_code_table",
    "encode",
    "decode",
    "Node",
    "is_leaf",
    "Stats",
    "entropy",
    "avg_code_length",
    "compression_stats",
]
