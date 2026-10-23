"""Gematria Primus — the rune alphabet 3301 gave solvers for Liber Primus.

29 runes. Each rune has a Latin value, a decimal index (0-28) and a
prime value (the primes in order, 2..109). This table follows the
community-verified transcription of the original 3301 material.

Also implemented: the *totient cipher* used by the solved Liber Primus
page "An End" — a running shift over rune indices where the shift for
each rune is phi(prime) mod 29 for successive primes (phi(p) = p - 1).
(The original applies an extra "F-skip" quirk for plaintext ᚠ; this
implementation is the clean stream cipher and says so honestly.)
"""
from __future__ import annotations

from .primes import euler_totient, first_primes

# (rune, latin, prime) — decimal index is the position in this list.
RUNES: list[tuple[str, str, int]] = [
    ("ᚠ", "F", 2), ("ᚢ", "U", 3), ("ᚦ", "TH", 5), ("ᚩ", "O", 7),
    ("ᚱ", "R", 11), ("ᚳ", "C", 13), ("ᚷ", "G", 17), ("ᚹ", "W", 19),
    ("ᚻ", "H", 23), ("ᚾ", "N", 29), ("ᛁ", "I", 31), ("ᛄ", "J", 37),
    ("ᛇ", "EO", 41), ("ᛈ", "P", 43), ("ᛉ", "X", 47), ("ᛋ", "S", 53),
    ("ᛏ", "T", 59), ("ᛒ", "B", 61), ("ᛖ", "E", 67), ("ᛗ", "M", 71),
    ("ᛚ", "L", 73), ("ᛝ", "NG", 79), ("ᛟ", "OE", 83), ("ᛞ", "D", 89),
    ("ᚪ", "A", 97), ("ᚫ", "AE", 101), ("ᚣ", "Y", 103), ("ᛡ", "IA", 107),
    ("ᛠ", "EA", 109),
]

_BY_LATIN: dict[str, int] = {}
for _i, (_rune, _latin, _prime) in enumerate(RUNES):
    _BY_LATIN.setdefault(_latin, _i)
# Aliases solvers actually type: U covers V, C covers K, S covers Z.
_BY_LATIN.update({"V": _BY_LATIN["U"], "K": _BY_LATIN["C"], "Z": _BY_LATIN["S"],
                  "Q": _BY_LATIN["C"]})
_BY_RUNE = {rune: i for i, (rune, _l, _p) in enumerate(RUNES)}
_DIGRAPHS = sorted((latin for _r, latin, _p in RUNES if len(latin) == 2),
                   key=len, reverse=True)


def latin_to_runes(text: str) -> str:
    """Transliterate Latin text to Gematria Primus runes.

    Digraphs (TH, NG, EO, OE, AE, IA, EA) become single runes; spaces
    and punctuation pass through unchanged.
    """
    text = text.upper()
    out, i = [], 0
    while i < len(text):
        pair = text[i:i + 2]
        if pair in _BY_LATIN and len(pair) == 2 and pair in _DIGRAPHS + ["TH", "NG", "EO", "OE", "AE", "IA", "EA"]:
            out.append(RUNES[_BY_LATIN[pair]][0])
            i += 2
        elif text[i] in _BY_LATIN:
            out.append(RUNES[_BY_LATIN[text[i]]][0])
            i += 1
        else:
            out.append(text[i])
            i += 1
    return "".join(out)


def runes_to_latin(runes: str) -> str:
    """Transliterate runes back to Latin (digraph runes expand)."""
    return "".join(RUNES[_BY_RUNE[ch]][1] if ch in _BY_RUNE else ch
                   for ch in runes)


def gematria_sum(text: str) -> int:
    """Sum the prime values of a Latin phrase, rune by rune."""
    total, i, text = 0, 0, text.upper()
    while i < len(text):
        pair = text[i:i + 2]
        if len(pair) == 2 and pair in _DIGRAPHS:
            total += RUNES[_BY_LATIN[pair]][2]
            i += 2
        elif text[i] in _BY_LATIN:
            total += RUNES[_BY_LATIN[text[i]]][2]
            i += 1
        else:
            i += 1
    return total


def _totient_shifts(count: int) -> list[int]:
    return [euler_totient(p) % 29 for p in first_primes(count)]


def totient_encrypt(latin_text: str) -> str:
    """Encrypt Latin text with the Liber Primus totient stream cipher."""
    indices = []
    i, text = 0, latin_text.upper()
    while i < len(text):
        pair = text[i:i + 2]
        if len(pair) == 2 and pair in _DIGRAPHS:
            indices.append(_BY_LATIN[pair]); i += 2
        elif text[i] in _BY_LATIN:
            indices.append(_BY_LATIN[text[i]]); i += 1
        else:
            indices.append(-1); i += 1  # passthrough marker
    shifts = _totient_shifts(sum(1 for x in indices if x >= 0) or 1)
    out, si = [], 0
    for idx in indices:
        if idx < 0:
            out.append(" ")
        else:
            out.append(RUNES[(idx + shifts[si]) % 29][0])
            si += 1
    return "".join(out)


def totient_decrypt(runes: str) -> str:
    """Decrypt runes produced by :func:`totient_encrypt`."""
    rune_indices = [_BY_RUNE[ch] if ch in _BY_RUNE else -1 for ch in runes]
    shifts = _totient_shifts(sum(1 for x in rune_indices if x >= 0) or 1)
    out, si = [], 0
    for idx in rune_indices:
        if idx < 0:
            out.append(" ")
        else:
            out.append(RUNES[(idx - shifts[si]) % 29][1])
            si += 1
    return "".join(out)
