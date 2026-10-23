"""The Hunt — a playable 5-artifact mini puzzle chain in Cicada style.

Stages (each answer unlocks the next clue):
  1. THE POSTER  — LSB steganography + Caesar cipher.
  2. THE SECOND DOOR — Vigenere cipher + a prime riddle.
  3. THE RUNES   — Gematria Primus transliteration.
  4. THE TOTIENT — the Liber Primus totient stream cipher.
  FINALE         — repeating-key XOR, key = all three answers joined.

Answers are never stored in plain text: hunt.json keeps only SHA-256
hashes of the normalised answers, like a real puzzle hunt's checker.
`make_hunt()` generates every artifact with this project's own toolkit.
"""
from __future__ import annotations

import hashlib
import json
import os

from .ciphers import caesar, caesar_crack, vigenere_decrypt, vigenere_encrypt, xor_repeat
from .gematria import latin_to_runes, runes_to_latin, totient_decrypt, totient_encrypt
from .primes import nth_prime
from .stego import lsb_embed, lsb_extract, make_poster, read_ppm, write_ppm

_STAGE1_PLAIN = "THE KEY TO THE SECOND DOOR IS THE INSECTS NAME"
_STAGE2_PLAIN = ("THE GATE NUMBER IS THE PRODUCT OF THE SEVENTH PRIME "
                 "AND THE ELEVENTH PRIME")
_STAGE4_PLAIN = "JOIN THE THREE ANSWERS IN ORDER WITH NOTHING BETWEEN THEM"
_FINAL_PLAIN = ("WELCOME, PILGRIM. YOU REACHED THE END OF THIS SMALL "
                "LABYRINTH. THE REAL ONE STILL WAITS - LIBER PRIMUS "
                "REMAINS UNSOLVED. PATIENCE IS A VIRTUE. "
                "- CICADALAB, A TRIBUTE TO 3301")

ANSWERS = ["CICADA", "527", "PRIMUS", "CICADA527PRIMUS"]

STAGE_META = [
    {"name": "Stage 1 - The Poster",
     "intro": "An image can hold more than it shows. poster.ppm is "
              "hiding something in its least significant bits - and what "
              "it hides is itself shifted. The decoded message names "
              "the key to the second door. Answer with that key."},
    {"name": "Stage 2 - The Second Door",
     "intro": "stage2.txt is locked with the key you just found "
              "(Vigenere). What it reveals is a riddle about primes. "
              "Answer with the gate number."},
    {"name": "Stage 3 - The Runes",
     "intro": "runes.txt is written in the Gematria Primus - the "
              "alphabet 3301 gave the world for Liber Primus. "
              "Transliterate it. Answer with the word."},
    {"name": "Stage 4 - The Totient",
     "intro": "stage4.txt uses the totient stream cipher from the "
              "solved Liber Primus page 'An End'. Decode it, follow "
              "its instruction, and answer with the final key."},
]


def _hash(answer: str) -> str:
    return hashlib.sha256(answer.strip().upper().encode()).hexdigest()


def make_hunt(outdir: str) -> str:
    """Generate all hunt artifacts into `outdir`; returns the path."""
    os.makedirs(outdir, exist_ok=True)

    # Stage 1: poster with LSB-hidden Caesar ciphertext.
    hidden = caesar(_STAGE1_PLAIN, 3)
    poster = lsb_embed(make_poster(), hidden.encode())
    write_ppm(os.path.join(outdir, "poster.ppm"), 160, 120, poster)

    # Stage 2: Vigenere ciphertext, key = stage 1 answer.
    with open(os.path.join(outdir, "stage2.txt"), "w", encoding="utf-8") as fh:
        fh.write(vigenere_encrypt(_STAGE2_PLAIN, ANSWERS[0]) + "\n")

    # Stage 3: the runes.
    with open(os.path.join(outdir, "runes.txt"), "w", encoding="utf-8") as fh:
        fh.write(latin_to_runes(ANSWERS[2]) + "\n")

    # Stage 4: totient-encrypted instruction.
    with open(os.path.join(outdir, "stage4.txt"), "w", encoding="utf-8") as fh:
        fh.write(totient_encrypt(_STAGE4_PLAIN) + "\n")

    # Finale: XOR-encrypted final message, key = stage 4 answer.
    cipher = xor_repeat(_FINAL_PLAIN.encode(), ANSWERS[3].encode())
    with open(os.path.join(outdir, "final.txt"), "w", encoding="utf-8") as fh:
        fh.write(cipher.hex() + "\n")

    config = {"stages": [{"name": m["name"], "intro": m["intro"],
                          "answer_sha256": _hash(a)}
                         for m, a in zip(STAGE_META, ANSWERS)]}
    with open(os.path.join(outdir, "hunt.json"), "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
    return outdir


class HuntGame:
    """Play a generated hunt: read clues, submit answers, win the finale."""

    def __init__(self, hunt_dir: str):
        with open(os.path.join(hunt_dir, "hunt.json"), encoding="utf-8") as fh:
            self.config = json.load(fh)
        self.hunt_dir = hunt_dir
        self.solved = 0

    @property
    def stage_count(self) -> int:
        return len(self.config["stages"])

    def clue(self, stage: int) -> str:
        meta = self.config["stages"][stage]
        return f"{meta['name']}\n{meta['intro']}"

    def check(self, stage: int, answer: str) -> bool:
        ok = _hash(answer) == self.config["stages"][stage]["answer_sha256"]
        if ok and stage == self.solved:
            self.solved += 1
        return ok

    def finale(self, final_key: str) -> str:
        """Decrypt the final message with the stage-4 key."""
        with open(os.path.join(self.hunt_dir, "final.txt"), encoding="utf-8") as fh:
            cipher = bytes.fromhex(fh.read().strip())
        return xor_repeat(cipher, final_key.strip().upper().encode()).decode()


_ORDINALS = {"FIRST": 1, "SECOND": 2, "THIRD": 3, "FOURTH": 4, "FIFTH": 5,
             "SIXTH": 6, "SEVENTH": 7, "EIGHTH": 8, "NINTH": 9, "TENTH": 10,
             "ELEVENTH": 11, "TWELFTH": 12}


def auto_solve(hunt_dir: str) -> list[str]:
    """Solve the whole hunt using only the toolkit + the artifacts.

    Returns a transcript of the solve. The one human hop — knowing the
    insect's name — is taken from the lab's own theme: CICADA.
    """
    game = HuntGame(hunt_dir)
    log: list[str] = []

    _w, _h, pixels = read_ppm(os.path.join(hunt_dir, "poster.ppm"))
    hidden = lsb_extract(pixels).decode()
    _shift, plain = caesar_crack(hidden)
    log.append(f"Stage 1: LSB extract -> Caesar crack -> {plain!r}")
    first = "CICADA"  # the insect the message points to
    assert game.check(0, first)

    with open(os.path.join(hunt_dir, "stage2.txt"), encoding="utf-8") as fh:
        riddle = vigenere_decrypt(fh.read().strip(), first)
    words = riddle.replace(".", " ").split()
    ordinals = [_ORDINALS[w] for w in words if w in _ORDINALS]
    gate = nth_prime(ordinals[0]) * nth_prime(ordinals[1])
    log.append(f"Stage 2: Vigenere -> {riddle!r} -> gate = {gate}")
    assert game.check(1, str(gate))

    with open(os.path.join(hunt_dir, "runes.txt"), encoding="utf-8") as fh:
        third = runes_to_latin(fh.read().strip())
    log.append(f"Stage 3: runes -> {third!r}")
    assert game.check(2, third)

    with open(os.path.join(hunt_dir, "stage4.txt"), encoding="utf-8") as fh:
        instruction = totient_decrypt(fh.read().strip())
    final_key = first + str(gate) + third
    log.append(f"Stage 4: totient -> {instruction!r} -> key = {final_key}")
    assert game.check(3, final_key)

    log.append(f"Finale: {game.finale(final_key)}")
    return log
