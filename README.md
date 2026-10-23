# CicadaLab 3301

```
We are looking for highly intelligent individuals.
To find them, we have devised a test.
```

A cryptography & steganography **lab and playable puzzle hunt** inspired by
**Cicada 3301** — the mysterious 2012–2014 puzzle series that hid clues in
images, ciphers, prime numbers, runes and posters across the world.

CicadaLab rebuilds the *actual techniques* of the solved Cicada puzzles as
working, tested tools — Caesar & Vigenère ciphers, LSB steganography,
prime mathematics, the **Gematria Primus** rune alphabet and the **totient
cipher** from Liber Primus — and wraps them in a 4-stage hunt you can
actually play and finish.

> Educational tribute. Not affiliated with 3301. Liber Primus remains
> unsolved — this project says so honestly instead of faking a solution.
> Background & myth-busting: [docs/cicada-3301-background.md](docs/cicada-3301-background.md)

## 🎮 The Hunt

```bash
python main.py hunt make ./hunt     # generate the puzzle artifacts
python main.py hunt play ./hunt     # play: each answer unlocks the next stage
python main.py hunt auto ./hunt     # watch the toolkit solve it end-to-end
```

1. **The Poster** — an image hiding data in its least significant bits;
   what it hides is Caesar-shifted
2. **The Second Door** — a Vigenère-locked riddle about prime numbers
3. **The Runes** — a word written in the Gematria Primus
4. **The Totient** — the stream cipher from the solved page *"An End"*
5. **Finale** — an XOR-locked message; the key is everything you found

Answers are stored only as SHA-256 hashes — the checker never holds the
plaintext, like a real puzzle hunt.

## 🧰 The Toolkit

```bash
python main.py crack "WKH NHB LV WKH LQVHFW"        # auto-crack a Caesar cipher
python main.py vigenere "ATTACK AT DAWN" --key CICADA
python main.py runes encode "PRIMUS"                # -> ᛈᚱᛁᛗᚢᛋ
python main.py runes sum "LIBER PRIMUS"             # gematria prime-value sum
python main.py totient encode "AN END"              # Liber Primus totient cipher
python main.py prime check 3301                     # 3301 is prime
python main.py prime nth 11                         # -> 31
python main.py stego hide poster.ppm "secret" -o out.ppm
python main.py stego seek out.ppm                   # -> secret
python main.py analyze mystery.bin                  # hexdump + hidden strings
```

- **Ciphers** — Caesar (+ chi-squared auto-cracker), Vigenère, Atbash, XOR
- **Gematria Primus** — the authentic 29-rune table (prime values 2–109),
  transliteration both ways, gematria sums, totient stream cipher
- **Primes** — deterministic Miller-Rabin (exact < 2⁶⁴), nth prime,
  factorisation, Euler's totient
- **Steganography** — LSB image hiding (pure-Python PPM), zero-width
  character hiding in text, hexdump & string extraction for analysis

Zero dependencies. Pure Python 3.10+.

## 🧪 Tests

```bash
python -m pytest tests/ -q    # 19 tests: every tool + the full hunt solve
```

The suite includes an end-to-end proof: the hunt is generated, then solved
start-to-finale using only the toolkit — and a check that no answer is
stored in plain text.

## 📁 Layout

```
cicada/   ciphers.py · gematria.py · primes.py · stego.py · hunt.py
main.py   the CLI
tests/    the test suite
docs/     the real Cicada 3301 background — and what the viral posts get wrong
```

## ⚖️ Ethics

For learning cryptography, CTF practice and puzzle design. The steganography
here is a teaching tool — don't hide data in systems you don't own.

## License

MIT
