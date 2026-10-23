"""Steganography & file analysis — "the image contains a hidden message".

- LSB steganography on PPM (P6) images: pure Python, no dependencies.
  (PPM is used so the lab needs zero installs; the technique is the
  same one used on PNG/JPEG carriers.)
- Zero-width character steganography for plain text.
- Analysis helpers from the 2012 puzzle's first steps: hexdump and
  printable-string extraction.
"""
from __future__ import annotations

import struct

# ---------------------------------------------------------------------------
# PPM image handling (binary P6 format)
# ---------------------------------------------------------------------------

def write_ppm(path: str, width: int, height: int, pixels: bytes) -> None:
    if len(pixels) != width * height * 3:
        raise ValueError("Pixel data size does not match dimensions.")
    with open(path, "wb") as fh:
        fh.write(f"P6\n{width} {height}\n255\n".encode())
        fh.write(pixels)


def read_ppm(path: str) -> tuple[int, int, bytes]:
    with open(path, "rb") as fh:
        data = fh.read()
    parts = data.split(b"\n", 3)
    if parts[0].strip() != b"P6":
        raise ValueError("Only binary PPM (P6) images are supported.")
    width, height = (int(x) for x in parts[1].split())
    if int(parts[2]) != 255:
        raise ValueError("Only 8-bit PPM images are supported.")
    return width, height, parts[3][: width * height * 3]


def make_poster(width: int = 160, height: int = 120) -> bytes:
    """Generate the hunt's poster image: a dark field with two pale
    'wing' ellipses and a central body — a nod to the cicada poster."""
    pixels = bytearray()
    cx, cy = width // 2, height // 2
    for y in range(height):
        for x in range(width):
            r = g = b = 12
            # wings: two ellipses angled from the centre
            for sx in (-1, 1):
                ex = (x - (cx + sx * width * 0.26)) / (width * 0.24)
                ey = (y - (cy - height * 0.08)) / (height * 0.16)
                if ex * ex + ey * ey < 1.0:
                    r = g = b = 190
            # body: narrow vertical ellipse
            bx = (x - cx) / (width * 0.045)
            by = (y - cy) / (height * 0.34)
            if bx * bx + by * by < 1.0:
                r = g = b = 220
            pixels += bytes((r, g, b))
    return bytes(pixels)


# ---------------------------------------------------------------------------
# LSB steganography
# ---------------------------------------------------------------------------

def lsb_embed(pixels: bytes, payload: bytes) -> bytes:
    """Hide payload in the least-significant bits of the pixel bytes.

    Format: 4-byte big-endian length header, then the payload bits.
    """
    framed = struct.pack(">I", len(payload)) + payload
    bits = [(byte >> shift) & 1 for byte in framed for shift in range(7, -1, -1)]
    if len(bits) > len(pixels):
        raise ValueError("Payload too large for this image.")
    out = bytearray(pixels)
    for i, bit in enumerate(bits):
        out[i] = (out[i] & 0xFE) | bit
    return bytes(out)


def lsb_extract(pixels: bytes) -> bytes:
    """Extract an LSB-hidden payload (see :func:`lsb_embed`)."""
    def take(bit_start: int, count: int) -> bytes:
        result = bytearray()
        for j in range(count):
            byte = 0
            for k in range(8):
                byte = (byte << 1) | (pixels[bit_start + j * 8 + k] & 1)
            result.append(byte)
        return bytes(result)

    length = struct.unpack(">I", take(0, 4))[0]
    if length > (len(pixels) - 32) // 8:
        raise ValueError("No valid LSB payload found (bad length header).")
    return take(32, length)


# ---------------------------------------------------------------------------
# Zero-width text steganography
# ---------------------------------------------------------------------------

_ZW = ["​", "‌"]  # zero-width space / non-joiner = 0 / 1


def zw_encode(cover_text: str, payload: bytes) -> str:
    """Hide payload bits as zero-width characters after the cover text."""
    bits = "".join(f"{byte:08b}" for byte in payload)
    hidden = "".join(_ZW[int(bit)] for bit in bits)
    return cover_text + hidden


def zw_decode(text: str) -> bytes:
    bits = "".join("0" if ch == _ZW[0] else "1" for ch in text if ch in _ZW)
    if not bits or len(bits) % 8:
        raise ValueError("No complete zero-width payload found.")
    return bytes(int(bits[i:i + 8], 2) for i in range(0, len(bits), 8))


# ---------------------------------------------------------------------------
# Analysis helpers (Step 1 of every Cicada-style puzzle)
# ---------------------------------------------------------------------------

def hexdump(data: bytes, width: int = 16) -> str:
    """Classic hex dump: offset, hex bytes, ASCII gutter."""
    lines = []
    for off in range(0, len(data), width):
        chunk = data[off:off + width]
        hexs = " ".join(f"{b:02X}" for b in chunk)
        text = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{off:08X}  {hexs:<{width * 3}}  {text}")
    return "\n".join(lines)


def extract_strings(data: bytes, min_len: int = 4) -> list[str]:
    """Printable ASCII strings hiding in a binary blob."""
    strings, current = [], []
    for b in data:
        if 32 <= b < 127:
            current.append(chr(b))
        else:
            if len(current) >= min_len:
                strings.append("".join(current))
            current = []
    if len(current) >= min_len:
        strings.append("".join(current))
    return strings
