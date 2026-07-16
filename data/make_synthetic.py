"""Generate reproducible synthetic corpora for benchmarking.

Creates high-entropy (random) and low-entropy (repeated) text files plus a
Vietnamese UTF-8 sample. Run:  python data/make_synthetic.py
"""

from __future__ import annotations

import random
import string
from pathlib import Path

HERE = Path(__file__).parent
SEED = 20260711


def main() -> None:
    rng = random.Random(SEED)

    # High-entropy: random printable ASCII (~6.5 bits/char) -> Huffman worst case.
    alphabet = string.ascii_letters + string.digits + " .,\n"
    random_text = "".join(rng.choice(alphabet) for _ in range(100_000))
    (HERE / "random.txt").write_text(random_text, encoding="utf-8")

    # Low-entropy: highly repetitive -> Huffman/RLE best case.
    repeated = ("abcabcabcabc " * 8 + "\n") * 2000
    (HERE / "repeated.txt").write_text(repeated, encoding="utf-8")

    # Vietnamese UTF-8 (multi-byte) sample.
    para = (
        "Nén dữ liệu là quá trình mã hóa thông tin sử dụng ít bit hơn biểu diễn "
        "gốc. Mã Huffman là một thuật toán nén không mất dữ liệu, gán mã ngắn cho "
        "ký hiệu xuất hiện nhiều và mã dài cho ký hiệu hiếm gặp. 😀🎉\n"
    )
    (HERE / "vietnamese.txt").write_text(para * 400, encoding="utf-8")

    for name in ("random.txt", "repeated.txt", "vietnamese.txt"):
        size = (HERE / name).stat().st_size
        print(f"{name:16} {size:>8} bytes")


if __name__ == "__main__":
    main()
