"""Classical ciphers — the kind Cicada 3301's puzzles are built from.

Caesar, Vigenere, Atbash and repeating-key XOR, plus a Caesar cracker
that scores every shift against English letter frequencies.
"""
from __future__ import annotations

ENGLISH_FREQ = {
    "a": .082, "b": .015, "c": .028, "d": .043, "e": .127, "f": .022,
    "g": .020, "h": .061, "i": .070, "j": .0015, "k": .0077, "l": .040,
    "m": .024, "n": .067, "o": .075, "p": .019, "q": .00095, "r": .060,
    "s": .063, "t": .091, "u": .028, "v": .0098, "w": .024, "x": .0015,
    "y": .020, "z": .00074, " ": .130,
}


def _shift_char(ch: str, shift: int) -> str:
    if "a" <= ch <= "z":
        return chr((ord(ch) - 97 + shift) % 26 + 97)
    if "A" <= ch <= "Z":
        return chr((ord(ch) - 65 + shift) % 26 + 65)
    return ch


def caesar(text: str, shift: int) -> str:
    """Caesar-shift letters by `shift` (negative to decode an encoding)."""
    return "".join(_shift_char(ch, shift) for ch in text)


def caesar_crack(ciphertext: str) -> tuple[int, str]:
    """Brute-force a Caesar cipher; return (encoding_shift, plaintext).

    Every shift is scored with a chi-squared test against English
    letter frequencies; the lowest score wins.
    """
    best = None
    for shift in range(26):
        candidate = caesar(ciphertext, -shift)
        score = 0.0
        counts = {c: 0 for c in ENGLISH_FREQ}
        total = 0
        for ch in candidate.lower():
            if ch in counts:
                counts[ch] += 1
                total += 1
        total = total or 1
        for ch, freq in ENGLISH_FREQ.items():
            expected = freq * total
            score += (counts[ch] - expected) ** 2 / (expected or 1)
        if best is None or score < best[0]:
            best = (score, shift, candidate)
    return best[1], best[2]


def _vigenere(text: str, key: str, sign: int) -> str:
    if not key or not key.isalpha():
        raise ValueError("Vigenere key must be letters only.")
    key = key.lower()
    out, ki = [], 0
    for ch in text:
        if ch.isalpha():
            k = ord(key[ki % len(key)]) - 97
            out.append(_shift_char(ch, sign * k))
            ki += 1
        else:
            out.append(ch)
    return "".join(out)


def vigenere_encrypt(text: str, key: str) -> str:
    return _vigenere(text, key, +1)


def vigenere_decrypt(text: str, key: str) -> str:
    return _vigenere(text, key, -1)


def atbash(text: str) -> str:
    """Atbash: A<->Z, B<->Y, ... (its own inverse)."""
    out = []
    for ch in text:
        if "a" <= ch <= "z":
            out.append(chr(122 - (ord(ch) - 97)))
        elif "A" <= ch <= "Z":
            out.append(chr(90 - (ord(ch) - 65)))
        else:
            out.append(ch)
    return "".join(out)


def xor_repeat(data: bytes, key: bytes) -> bytes:
    """Repeating-key XOR (its own inverse)."""
    if not key:
        raise ValueError("XOR key must not be empty.")
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
