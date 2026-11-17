"""GSTIN helpers: build and check Indian GST numbers.

A GSTIN has 15 characters:
  2 digits   state code       (27 = Maharashtra)
  10 chars   the business PAN (AAPFU0939F)
  1 char     entity number    (1-9 or A-Z)
  1 char     always "Z"
  1 char     checksum         (calculated from the first 14)
"""

import random
import re

CHARSET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
GSTIN_PATTERN = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]$")

STATES = {
    "27": "Maharashtra",
    "29": "Karnataka",
    "07": "Delhi",
    "33": "Tamil Nadu",
    "24": "Gujarat",
    "09": "Uttar Pradesh",
    "36": "Telangana",
    "19": "West Bengal",
}


def checksum_char(first14: str) -> str:
    """Return the 15th GSTIN character for the first 14 characters."""
    total = 0
    for i, ch in enumerate(first14):
        factor = 1 if i % 2 == 0 else 2
        product = CHARSET.index(ch) * factor
        total += product // 36 + product % 36
    return CHARSET[(36 - total % 36) % 36]


def is_valid_gstin(gstin: str) -> bool:
    """True if the GSTIN has the right shape and the right checksum."""
    if not GSTIN_PATTERN.match(gstin):
        return False
    return gstin[-1] == checksum_char(gstin[:14])


def random_pan(rng: random.Random) -> str:
    """Make a random PAN-shaped string: 5 letters, 4 digits, 1 letter."""
    first3 = "".join(rng.choice(LETTERS) for _ in range(3))
    entity_type = rng.choice("CPF")  # C company, P person, F firm
    fifth = rng.choice(LETTERS)
    digits = "".join(rng.choice("0123456789") for _ in range(4))
    return first3 + entity_type + fifth + digits + rng.choice(LETTERS)


def make_gstin(state_code: str, rng: random.Random) -> str:
    """Make a valid random GSTIN for the given state."""
    first14 = state_code + random_pan(rng) + rng.choice("123456789") + "Z"
    return first14 + checksum_char(first14)