"""Generate figures for the report (matplotlib, Agg backend).

Run: ``python -m huffman.visualize`` -> writes results/figures/*.png
Figures are produced programmatically from data — never hand-edited.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ..core.huffman import build_code_table, build_tree, count_frequencies  # noqa: E402
from ..core.tree import Node, is_leaf  # noqa: E402

SAMPLE = b"abracadabra abracadabra huffman coding"


# --------------------------------------------------------------------------- #
# Huffman tree diagram
# --------------------------------------------------------------------------- #


def plot_tree(data: bytes, out: Path) -> None:
    """Draw the Huffman tree for ``data``."""
    root = build_tree(count_frequencies(data))
    if root is None:
        return
    positions: dict[int, tuple[float, float]] = {}
    labels: dict[int, str] = {}
    edges: list[tuple[int, int, str]] = []
    counter = [0]

    def layout(node: Node, depth: int) -> float:
        node_id = id(node)
        if is_leaf(node):
            x = counter[0]
            counter[0] += 1
            positions[node_id] = (x, -depth)
            labels[node_id] = f"{chr(node.symbol)!r}\n{node.freq}"
            return x
        xs = []
        if node.left is not None:
            xs.append(layout(node.left, depth + 1))
            edges.append((node_id, id(node.left), "0"))
        if node.right is not None:
            xs.append(layout(node.right, depth + 1))
            edges.append((node_id, id(node.right), "1"))
        x = sum(xs) / len(xs)
        positions[node_id] = (x, -depth)
        labels[node_id] = str(node.freq)
        return x

    layout(root, 0)
    fig, ax = plt.subplots(figsize=(12, 7))
    for parent, child, bit in edges:
        x1, y1 = positions[parent]
        x2, y2 = positions[child]
        ax.plot([x1, x2], [y1, y2], color="#888", zorder=1)
        ax.text((x1 + x2) / 2, (y1 + y2) / 2, bit, fontsize=9, color="#c0392b")
    for node_id, (x, y) in positions.items():
        ax.scatter([x], [y], s=650, color="#4C78A8", zorder=2, edgecolors="white")
        ax.text(x, y, labels[node_id], ha="center", va="center", fontsize=8, color="white")
    ax.set_title("Huffman Tree — sample: 'abracadabra ... huffman coding'")
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def plot_frequency_hist(data: bytes, out: Path) -> None:
    """Bar chart of symbol frequencies and their Huffman code lengths."""
    freq = count_frequencies(data)
    table = build_code_table(build_tree(freq))
    symbols = sorted(freq, key=lambda s: -freq[s])
    labels = [repr(chr(s)) for s in symbols]
    counts = [freq[s] for s in symbols]
    lengths = [len(table[s]) for s in symbols]

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax1.bar(labels, counts, color="#4C78A8", label="Frequency")
    ax1.set_ylabel("Frequency", color="#4C78A8")
    ax1.set_xlabel("Symbol (sorted by frequency)")
    ax2 = ax1.twinx()
    ax2.plot(labels, lengths, color="#E45756", marker="o", label="Code length")
    ax2.set_ylabel("Huffman code length (bits)", color="#E45756")
    ax1.set_title("Frequency vs. Huffman code length (rare symbol → longer code)")
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


# --------------------------------------------------------------------------- #
# Benchmark comparison charts (from results/benchmark.csv)
# --------------------------------------------------------------------------- #


def _load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _grouped_bar(rows, value_fn, title, ylabel, out: Path, logy: bool = False) -> None:
    corpora = sorted({r["corpus"] for r in rows})
    algos = ["Huffman", "Shannon-Fano", "RLE"]
    data: dict[str, dict[str, float]] = defaultdict(dict)
    for r in rows:
        data[r["algorithm"]][r["corpus"]] = value_fn(r)

    import numpy as np

    x = np.arange(len(corpora))
    width = 0.26
    colors = {"Huffman": "#4C78A8", "Shannon-Fano": "#F58518", "RLE": "#E45756"}
    fig, ax = plt.subplots(figsize=(14, 6))
    for i, algo in enumerate(algos):
        vals = [data[algo].get(c, 0.0) for c in corpora]
        ax.bar(x + (i - 1) * width, vals, width, label=algo, color=colors[algo])
    ax.set_xticks(x)
    ax.set_xticklabels(corpora, rotation=45, ha="right")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    if logy:
        ax.set_yscale("log")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def plot_ratio_comparison(rows, out: Path) -> None:
    _grouped_bar(
        rows, lambda r: float(r["ratio"]),
        "Compression ratio by corpus (higher = better)", "Compression ratio", out,
    )


def plot_time_comparison(rows, out: Path) -> None:
    _grouped_bar(
        rows, lambda r: float(r["encode_ms"]),
        "Encoding time by corpus", "Encode time (ms)", out, logy=True,
    )


def plot_filesize_comparison(rows, out: Path) -> None:
    text_rows = [r for r in rows if r["algorithm"] == "Huffman"]
    corpora = [r["corpus"] for r in text_rows]
    orig = [int(r["original_bytes"]) / 1024 for r in text_rows]
    comp = [int(r["compressed_bytes"]) / 1024 for r in text_rows]
    import numpy as np

    x = np.arange(len(corpora))
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.bar(x - 0.2, orig, 0.4, label="Original", color="#B0B0B0")
    ax.bar(x + 0.2, comp, 0.4, label="Huffman compressed", color="#4C78A8")
    ax.set_xticks(x)
    ax.set_xticklabels(corpora, rotation=45, ha="right")
    ax.set_ylabel("Size (KB)")
    ax.set_title("File size before vs. after Huffman compression")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out, dpi=130)
    plt.close(fig)


def main() -> int:
    root = Path(__file__).resolve().parents[3]
    figures = root / "results" / "figures"
    figures.mkdir(parents=True, exist_ok=True)

    plot_tree(SAMPLE, figures / "huffman_tree.png")
    plot_frequency_hist(SAMPLE, figures / "frequency_hist.png")

    csv_path = root / "results" / "benchmark.csv"
    if csv_path.exists():
        rows = _load_csv(csv_path)
        plot_ratio_comparison(rows, figures / "ratio_comparison.png")
        plot_time_comparison(rows, figures / "time_comparison.png")
        plot_filesize_comparison(rows, figures / "filesize_comparison.png")
        print(f"Wrote 5 figures to {figures}")
    else:
        print("benchmark.csv not found; run huffman.benchmark first (2 figures written).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
