"""Benchmark Huffman against RLE and Shannon-Fano on a set of corpora.

Reproducible: run ``python -m huffman.benchmark`` (with ``src`` on PYTHONPATH)
or ``python src/huffman/benchmark.py``. Writes:
    results/benchmark.csv     one row per (corpus, algorithm)
    results/summary.md        Markdown summary table
    results/environment.txt   platform / versions for reproducibility

Every measurement verifies losslessness (round-trip) before recording.
"""

from __future__ import annotations

import csv
import platform
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from ..codec.compressor import compress_bytes
from ..codec.decompressor import decompress_bytes
from ..common.metrics import entropy
from ..common.utils import Timer
from ..container.bitstream import pack_bits, unpack_bits
from ..container.file_io import header_size
from ..core.huffman import count_frequencies
from .baselines import rle_compress, rle_decompress, sf_decode, sf_encode

# Curated text-oriented subset of standard corpora + synthetic files.
DEFAULT_CORPUS = [
    "canterbury/alice29.txt",
    "canterbury/asyoulik.txt",
    "canterbury/lcet10.txt",
    "canterbury/plrabn12.txt",
    "canterbury/fields.c",
    "canterbury/cp.html",
    "canterbury/grammar.lsp",
    "canterbury/xargs.1",
    "calgary/book1",
    "calgary/book2",
    "calgary/paper1",
    "calgary/news",
    "calgary/progc",
    "random.txt",
    "repeated.txt",
    "vietnamese.txt",
]


@dataclass
class Row:
    corpus: str
    algorithm: str
    original_bytes: int
    compressed_bytes: int
    ratio: float
    space_saving_pct: float
    bpc: float
    entropy: float
    encode_ms: float
    decode_ms: float
    lossless: bool


def _measure_huffman(data: bytes) -> tuple[int, float, float, bool]:
    with Timer() as t_enc:
        freq, payload = compress_bytes(data)
    with Timer() as t_dec:
        restored = decompress_bytes(freq, payload)
    size = header_size(len(freq)) + len(payload)
    return size, t_enc.elapsed, t_dec.elapsed, restored == data


def _measure_shannon_fano(data: bytes) -> tuple[int, float, float, bool]:
    with Timer() as t_enc:
        freq, bits = sf_encode(data)
        payload = pack_bits(bits)
    with Timer() as t_dec:
        restored = sf_decode(freq, unpack_bits(payload))
    size = header_size(len(freq)) + len(payload)
    return size, t_enc.elapsed, t_dec.elapsed, restored == data


def _measure_rle(data: bytes) -> tuple[int, float, float, bool]:
    with Timer() as t_enc:
        packed = rle_compress(data)
    with Timer() as t_dec:
        restored = rle_decompress(packed)
    return len(packed), t_enc.elapsed, t_dec.elapsed, restored == data


ALGORITHMS = {
    "Huffman": _measure_huffman,
    "Shannon-Fano": _measure_shannon_fano,
    "RLE": _measure_rle,
}


def benchmark_file(path: Path) -> list[Row]:
    data = path.read_bytes()
    original = len(data)
    h = entropy(count_frequencies(data))
    rows: list[Row] = []
    for name, measure in ALGORITHMS.items():
        size, enc, dec, lossless = measure(data)
        rows.append(
            Row(
                corpus=path.name,
                algorithm=name,
                original_bytes=original,
                compressed_bytes=size,
                ratio=original / size if size else 0.0,
                space_saving_pct=(1 - size / original) * 100 if original else 0.0,
                bpc=8 * size / original if original else 0.0,
                entropy=h,
                encode_ms=enc * 1000,
                decode_ms=dec * 1000,
                lossless=lossless,
            )
        )
    return rows


def run_benchmark(
    data_dir: Path, out_dir: Path, corpus: list[str] | None = None
) -> list[Row]:
    """Run the benchmark and write CSV/summary/environment files."""
    corpus = corpus or DEFAULT_CORPUS
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[Row] = []
    for rel in corpus:
        path = data_dir / rel
        if not path.exists():
            print(f"  [skip] missing: {rel}", file=sys.stderr)
            continue
        print(f"  benchmarking {rel} ...", file=sys.stderr)
        rows.extend(benchmark_file(path))

    _write_csv(rows, out_dir / "benchmark.csv")
    _write_summary(rows, out_dir / "summary.md")
    _write_environment(out_dir / "environment.txt")
    return rows


def _write_csv(rows: list[Row], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(asdict(rows[0]).keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(asdict(row))


def _write_summary(rows: list[Row], path: Path) -> None:
    cols = ["Corpus", "Algorithm", "Orig (B)", "Comp (B)", "Ratio", "Saving %",
            "BPC", "H (bit)", "Enc ms", "Dec ms", "OK"]
    header = "| " + " | ".join(cols) + " |"
    sep = "|" + "|".join("---" for _ in cols) + "|"
    lines = [
        "# Benchmark Summary",
        "",
        "Compression ratio (higher = better). Round-trip verified lossless.",
        "",
        header,
        sep,
    ]
    for r in rows:
        lines.append(
            f"| {r.corpus} | {r.algorithm} | {r.original_bytes} | {r.compressed_bytes} "
            f"| {r.ratio:.3f} | {r.space_saving_pct:.1f} | {r.bpc:.3f} | {r.entropy:.3f} "
            f"| {r.encode_ms:.1f} | {r.decode_ms:.1f} | {'✔' if r.lossless else '�’'} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_environment(path: Path) -> None:
    info = [
        f"Python   : {platform.python_version()}",
        f"Platform : {platform.platform()}",
        f"Processor: {platform.processor()}",
        f"Machine  : {platform.machine()}",
    ]
    path.write_text("\n".join(info) + "\n", encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    rows = run_benchmark(root / "data", root / "results")
    n_files = len({r.corpus for r in rows})
    all_lossless = all(r.lossless for r in rows)
    print(f"Done: {n_files} files, {len(rows)} rows. All lossless: {all_lossless}")
    return 0 if all_lossless else 1


if __name__ == "__main__":
    sys.exit(main())
