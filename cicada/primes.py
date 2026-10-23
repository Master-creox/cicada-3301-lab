"""Prime utilities. "The primes are sacred." — Liber Primus (solved page).

Deterministic Miller-Rabin for 64-bit integers, prime generation,
factorisation of small numbers and Euler's totient.
"""
from __future__ import annotations


def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin, exact for all n < 2**64."""
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def first_primes(count: int) -> list[int]:
    """The first `count` primes, in order."""
    primes: list[int] = []
    candidate = 2
    while len(primes) < count:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1 if candidate == 2 else 2
    return primes


def nth_prime(n: int) -> int:
    """The n-th prime, 1-indexed (nth_prime(1) == 2)."""
    if n < 1:
        raise ValueError("n must be >= 1.")
    return first_primes(n)[-1]


def prime_factors(n: int) -> list[int]:
    """Prime factors of n with multiplicity (trial division)."""
    if n < 2:
        return []
    factors, d = [], 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        factors.append(n)
    return factors


def euler_totient(n: int) -> int:
    """Euler's totient phi(n) — central to the Liber Primus totient cipher."""
    if n < 1:
        raise ValueError("n must be >= 1.")
    result, m = n, n
    for p in set(prime_factors(m)):
        result -= result // p
    return result
