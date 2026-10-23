"""CicadaLab CLI — a cryptography & steganography lab inspired by Cicada 3301.

Toolkit:
    python main.py caesar "WKH NHB" --shift 3          # shift text
    python main.py crack "WKH NHB LV WKH LQVHFW"       # auto-crack Caesar
    python main.py vigenere "ATTACK AT DAWN" --key CICADA [--decode]
    python main.py atbash "GSV JFRXP"
    python main.py runes encode "PRIMUS"               # -> runes
    python main.py runes decode "ᛈᚱᛁᛗᚢᛋ"              # -> PRIMUS
    python main.py runes sum "LIBER PRIMUS"            # gematria prime sum
    python main.py totient encode "AN END"             # Liber Primus cipher
    python main.py prime check 3301 | prime nth 7 | prime factors 527
    python main.py stego hide poster.ppm "secret" -o out.ppm
    python main.py stego seek out.ppm
    python main.py analyze mystery.bin                 # hexdump + strings

The Hunt (a playable mini puzzle chain):
    python main.py hunt make ./hunt                    # generate artifacts
    python main.py hunt play ./hunt                    # play interactively
    python main.py hunt auto ./hunt                    # watch the toolkit solve it
"""
from __future__ import annotations

import argparse
import sys

from cicada.ciphers import atbash, caesar, caesar_crack, vigenere_decrypt, vigenere_encrypt
from cicada.gematria import gematria_sum, latin_to_runes, runes_to_latin, totient_decrypt, totient_encrypt
from cicada.hunt import HuntGame, auto_solve, make_hunt
from cicada.primes import is_prime, nth_prime, prime_factors
from cicada.stego import extract_strings, hexdump, lsb_embed, lsb_extract, read_ppm, write_ppm


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cicadalab",
                                     description="Cryptography & steganography lab (educational).")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("caesar"); p.add_argument("text"); p.add_argument("--shift", type=int, required=True)
    p = sub.add_parser("crack"); p.add_argument("text")
    p = sub.add_parser("vigenere"); p.add_argument("text"); p.add_argument("--key", required=True)
    p.add_argument("--decode", action="store_true")
    p = sub.add_parser("atbash"); p.add_argument("text")
    p = sub.add_parser("runes"); p.add_argument("action", choices=["encode", "decode", "sum"]); p.add_argument("text")
    p = sub.add_parser("totient"); p.add_argument("action", choices=["encode", "decode"]); p.add_argument("text")
    p = sub.add_parser("prime"); p.add_argument("action", choices=["check", "nth", "factors"]); p.add_argument("number", type=int)

    p = sub.add_parser("stego"); p.add_argument("action", choices=["hide", "seek"])
    p.add_argument("image"); p.add_argument("message", nargs="?"); p.add_argument("-o", "--output")

    p = sub.add_parser("analyze"); p.add_argument("file")

    p = sub.add_parser("hunt"); p.add_argument("action", choices=["make", "play", "auto"])
    p.add_argument("directory")

    args = parser.parse_args(argv)

    if args.command == "caesar":
        print(caesar(args.text, args.shift))
    elif args.command == "crack":
        shift, plain = caesar_crack(args.text)
        print(f"Shift {shift}: {plain}")
    elif args.command == "vigenere":
        fn = vigenere_decrypt if args.decode else vigenere_encrypt
        print(fn(args.text, args.key))
    elif args.command == "atbash":
        print(atbash(args.text))
    elif args.command == "runes":
        if args.action == "encode":
            print(latin_to_runes(args.text))
        elif args.action == "decode":
            print(runes_to_latin(args.text))
        else:
            print(gematria_sum(args.text))
    elif args.command == "totient":
        print(totient_encrypt(args.text) if args.action == "encode" else totient_decrypt(args.text))
    elif args.command == "prime":
        if args.action == "check":
            print(f"{args.number} is {'prime' if is_prime(args.number) else 'not prime'}")
        elif args.action == "nth":
            print(nth_prime(args.number))
        else:
            print(" x ".join(str(f) for f in prime_factors(args.number)) or "no factors")
    elif args.command == "stego":
        if args.action == "hide":
            if not args.message or not args.output:
                print("stego hide needs a message and -o output.ppm")
                return 2
            w, h, pixels = read_ppm(args.image)
            write_ppm(args.output, w, h, lsb_embed(pixels, args.message.encode()))
            print(f"Hidden {len(args.message)} bytes in {args.output}")
        else:
            _w, _h, pixels = read_ppm(args.image)
            print(lsb_extract(pixels).decode(errors="replace"))
    elif args.command == "analyze":
        with open(args.file, "rb") as fh:
            data = fh.read()
        print(hexdump(data[:256]))
        found = extract_strings(data)
        if found:
            print("\nStrings found:")
            for s in found[:20]:
                print(" -", s)
    elif args.command == "hunt":
        if args.action == "make":
            make_hunt(args.directory)
            print(f"Hunt generated in {args.directory}/ — start with the poster.")
        elif args.action == "auto":
            for line in auto_solve(args.directory):
                print(line)
        else:
            game = HuntGame(args.directory)
            print("We are looking for highly intelligent individuals...")
            # interactive play
            last_answer = ""
            for stage in range(game.stage_count):
                print("\n" + game.clue(stage))
                while True:
                    try:
                        answer = input("Your answer: ")
                    except (EOFError, KeyboardInterrupt):
                        print("\nPatience is a virtue. Come back soon.")
                        return 0
                    if game.check(stage, answer):
                        print("Correct. The path continues.")
                        last_answer = answer
                        break
                    print("That is not the way.")
            print("\n" + game.finale(last_answer))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
