"""Tests for CicadaLab — toolkit correctness + the full hunt solve."""
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from cicada.ciphers import (atbash, caesar, caesar_crack, vigenere_decrypt,
                            vigenere_encrypt, xor_repeat)
from cicada.gematria import (gematria_sum, latin_to_runes, runes_to_latin,
                             totient_decrypt, totient_encrypt)
from cicada.hunt import HuntGame, auto_solve, make_hunt
from cicada.primes import euler_totient, is_prime, nth_prime, prime_factors
from cicada.stego import (extract_strings, hexdump, lsb_embed, lsb_extract,
                          make_poster, zw_decode, zw_encode)


class TestCiphers(unittest.TestCase):
    def test_caesar_roundtrip(self):
        self.assertEqual(caesar(caesar("HELLO WORLD", 3), -3), "HELLO WORLD")

    def test_caesar_crack(self):
        ct = caesar("THE KEY TO THE SECOND DOOR IS THE INSECTS NAME", 3)
        _shift, plain = caesar_crack(ct)
        self.assertEqual(plain, "THE KEY TO THE SECOND DOOR IS THE INSECTS NAME")

    def test_vigenere_roundtrip(self):
        ct = vigenere_encrypt("ATTACK AT DAWN", "CICADA")
        self.assertEqual(vigenere_decrypt(ct, "CICADA"), "ATTACK AT DAWN")

    def test_atbash_is_own_inverse(self):
        self.assertEqual(atbash(atbash("Cicada 3301")), "Cicada 3301")

    def test_xor_roundtrip(self):
        data = b"pilgrim"
        self.assertEqual(xor_repeat(xor_repeat(data, b"KEY"), b"KEY"), data)


class TestPrimes(unittest.TestCase):
    def test_is_prime(self):
        self.assertTrue(is_prime(3301))
        self.assertFalse(is_prime(3300))
        self.assertTrue(is_prime(2))
        self.assertFalse(is_prime(1))

    def test_nth_prime(self):
        self.assertEqual(nth_prime(1), 2)
        self.assertEqual(nth_prime(7), 17)
        self.assertEqual(nth_prime(11), 31)
        self.assertEqual(nth_prime(7) * nth_prime(11), 527)  # the hunt's gate

    def test_factors_and_totient(self):
        self.assertEqual(prime_factors(527), [17, 31])
        self.assertEqual(euler_totient(29), 28)  # phi(p) = p-1 for primes


class TestGematria(unittest.TestCase):
    def test_table_has_29_runes_with_prime_values(self):
        from cicada.gematria import RUNES
        from cicada.primes import first_primes
        self.assertEqual(len(RUNES), 29)
        self.assertEqual([p for _r, _l, p in RUNES], first_primes(29))

    def test_transliteration_roundtrip(self):
        self.assertEqual(runes_to_latin(latin_to_runes("PRIMUS")), "PRIMUS")
        self.assertEqual(runes_to_latin(latin_to_runes("THE GATE")), "THE GATE")

    def test_digraphs(self):
        self.assertEqual(latin_to_runes("TH"), "ᚦ")
        self.assertEqual(runes_to_latin("ᛝ"), "NG")

    def test_gematria_sum_positive(self):
        self.assertGreater(gematria_sum("LIBER PRIMUS"), 0)

    def test_totient_cipher_roundtrip(self):
        ct = totient_encrypt("AN END")
        self.assertEqual(totient_decrypt(ct), "AN END")
        ct2 = totient_encrypt("SOME WISDOM THE PRIMES ARE SACRED")
        self.assertEqual(totient_decrypt(ct2), "SOME WISDOM THE PRIMES ARE SACRED")


class TestStego(unittest.TestCase):
    def test_lsb_roundtrip(self):
        pixels = make_poster(64, 48)
        hidden = lsb_embed(pixels, b"3301")
        self.assertEqual(lsb_extract(hidden), b"3301")

    def test_zero_width_roundtrip(self):
        text = zw_encode("an ordinary sentence", b"HI")
        self.assertEqual(zw_decode(text), b"HI")

    def test_analysis_helpers(self):
        self.assertIn("HIDDEN", extract_strings(b"\x00\x01HIDDEN\x00"))
        self.assertIn("00000000", hexdump(b"abc"))


class TestHunt(unittest.TestCase):
    def test_full_auto_solve(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_hunt(tmp)
            transcript = auto_solve(tmp)
            self.assertEqual(len(transcript), 5)
            self.assertIn("WELCOME, PILGRIM", transcript[-1])

    def test_wrong_answers_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_hunt(tmp)
            game = HuntGame(tmp)
            self.assertFalse(game.check(0, "BEETLE"))
            self.assertTrue(game.check(0, "cicada"))  # case-insensitive

    def test_answers_not_stored_in_plain_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            make_hunt(tmp)
            with open(os.path.join(tmp, "hunt.json"), encoding="utf-8") as fh:
                raw = fh.read()
            self.assertNotIn("CICADA527PRIMUS", raw)


if __name__ == "__main__":
    unittest.main()
