"""Bit packing/unpacking, MSB-first (see ``docs/format.md``).

Bits are represented as Python strings of ``'0'``/``'1'`` for clarity and
testability. The last byte is zero-padded on the right; the number of valid
symbols is recovered from the frequency table at decode time, so no explicit
padding count is stored.
"""

from __future__ import annotations


def pack_bits(bits: str) -> bytes:
    """Pack a bit string into bytes, MSB-first, zero-padding the final byte.

    Args:
        bits: String of ``'0'`` and ``'1'``.

    Returns:
        Packed bytes (empty input -> ``b""``).
    """
    if not bits:
        return b""
    padding = (-len(bits)) % 8
    padded = bits + "0" * padding
    value = int(padded, 2)
    return value.to_bytes(len(padded) // 8, "big")


def unpack_bits(data: bytes) -> str:
    """Expand bytes into a bit string, MSB-first (inverse of :func:`pack_bits`)."""
    return "".join(f"{byte:08b}" for byte in data)


class BitWriter:
    """Accumulate bit strings and emit packed bytes."""

    def __init__(self) -> None:
        self._chunks: list[str] = []

    def write_bits(self, bits: str) -> None:
        """Append a codeword (bit string)."""
        self._chunks.append(bits)

    def getvalue(self) -> bytes:
        """Return the packed bytes for everything written so far."""
        return pack_bits("".join(self._chunks))


class BitReader:
    """Read a byte buffer one bit at a time, MSB-first."""

    def __init__(self, data: bytes) -> None:
        self._bits = unpack_bits(data)
        self._pos = 0

    def read_bit(self) -> str | None:
        """Return next bit as ``'0'``/``'1'``, or ``None`` at end of stream."""
        if self._pos >= len(self._bits):
            return None
        bit = self._bits[self._pos]
        self._pos += 1
        return bit
